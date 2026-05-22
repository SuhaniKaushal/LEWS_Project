#!/usr/bin/python3
"""LEWS Pi gateway: read sensor packets from USB-serial, forward over TCP.

Reliability layers (see usr-bin-python3-import-sys-wild-meerkat.md plan):
  1. timeouts on every blocking syscall (serial, socket)
  2. in-process watchdog that os._exit(1) on loop stall
  3. systemd Restart=always (see lews-net.service)
"""

import sys
sys.stdout.reconfigure(line_buffering=True)

import fcntl
import logging
import logging.handlers
import os
import socket
import threading
import time
from datetime import datetime

import serial
import termios

import NodeValue


# --- Configuration ---
SERIAL_PORT = "/dev/serial/by-id/usb-1a86_USB2.0-Serial-if00-port0"
SERIAL_BAUD = 115200
SERIAL_TIMEOUT = 2            # bounds ser.read()

SERVER_IP = "103.37.200.35"
SERVER_PORT = 5000
SOCKET_TIMEOUT = 10

WATCHDOG_TIMEOUT = 60         # max time main loop may stall before we self-kill
FLUSH_INTERVAL = 30           # background buffer drain cadence

RX_BUFFER_MAX = 64 * 1024
MAX_UNSENT_BYTES = 50 * 1024 * 1024   # 50 MB hard cap on unsent_data.txt

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(SCRIPT_DIR, 'log.txt')
UNSENT_FILE = os.path.join(SCRIPT_DIR, 'unsent_data.txt')
BACKUP_FILE = os.path.join(SCRIPT_DIR, 'all_received_data.txt')

USBDEVFS_RESET = 21780        # _IO('U', 20)


# --- Logging setup ---
def _make_logger(name, path, to_console):
    lg = logging.getLogger(name)
    lg.setLevel(logging.INFO)
    lg.propagate = False
    fh = logging.handlers.RotatingFileHandler(
        path, maxBytes=1_048_576, backupCount=5)
    fh.setFormatter(logging.Formatter('%(asctime)s %(message)s',
                                      datefmt='%Y-%m-%d %H:%M:%S'))
    lg.addHandler(fh)
    if to_console:
        ch = logging.StreamHandler(sys.stdout)
        ch.setFormatter(logging.Formatter('[%(asctime)s] %(message)s',
                                          datefmt='%H:%M:%S'))
        lg.addHandler(ch)
    return lg


log_event = _make_logger('lews.event', LOG_FILE, to_console=True)
log_backup = _make_logger('lews.backup', BACKUP_FILE, to_console=False)


# --- Watchdog (Layer 2) ---
last_loop_tick = time.monotonic()


def watchdog_loop():
    """Force-exit the process if the main loop stalls. systemd will restart us."""
    while True:
        time.sleep(5)
        idle = time.monotonic() - last_loop_tick
        if idle > WATCHDOG_TIMEOUT:
            try:
                log_event.critical(
                    'WATCHDOG | hang detected, last tick %.1fs ago, killing process',
                    idle)
            except Exception:
                pass
            os._exit(1)


# --- USB best-effort reset (bonus mitigation for CH340 wedge) ---
def _resolve_usb_devnode(tty_by_id_path):
    """Map /dev/serial/by-id/... -> /dev/bus/usb/BBB/DDD, or None."""
    try:
        real_tty = os.path.realpath(tty_by_id_path)
        tty_name = os.path.basename(real_tty)
        sysfs = os.path.realpath('/sys/class/tty/%s/device/../..' % tty_name)
        with open(os.path.join(sysfs, 'busnum')) as f:
            busnum = int(f.read().strip())
        with open(os.path.join(sysfs, 'devnum')) as f:
            devnum = int(f.read().strip())
        return '/dev/bus/usb/%03d/%03d' % (busnum, devnum)
    except Exception:
        return None


def usb_reset_best_effort():
    """Try USBDEVFS_RESET on the CH340. Needs write perm on /dev/bus/usb/..."""
    node = _resolve_usb_devnode(SERIAL_PORT)
    if not node:
        log_event.info('USB    | reset skipped: could not resolve devnode')
        return False
    try:
        fd = os.open(node, os.O_WRONLY)
        try:
            fcntl.ioctl(fd, USBDEVFS_RESET, 0)
            log_event.info('USB    | reset OK on %s', node)
            return True
        finally:
            os.close(fd)
    except PermissionError:
        log_event.info('USB    | reset skipped: no permission on %s', node)
        return False
    except Exception as e:
        log_event.warning('USB    | reset failed: %s', e)
        return False


# --- Serial connect / reconnect ---
def open_serial():
    return serial.Serial(SERIAL_PORT, SERIAL_BAUD, timeout=SERIAL_TIMEOUT)


def reconnect_serial():
    """Block until serial is open again. Tries USB reset on persistent failure."""
    backoff = 1
    attempt = 0
    while True:
        attempt += 1
        try:
            s = open_serial()
            log_event.info('SERIAL | reconnected on %s', SERIAL_PORT)
            return s
        except Exception as e:
            log_event.warning('SERIAL | reconnect failed (attempt %d): %s', attempt, e)
            if attempt == 5:
                usb_reset_best_effort()
        time.sleep(backoff)
        backoff = min(backoff * 2, 30)


# --- TCP send (single attempt; flusher provides the retry cadence) ---
def _set_keepalive(sock):
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
    for opt_name, value in (('TCP_KEEPIDLE', 30),
                            ('TCP_KEEPINTVL', 10),
                            ('TCP_KEEPCNT', 3)):
        opt = getattr(socket, opt_name, None)
        if opt is not None:
            try:
                sock.setsockopt(socket.IPPROTO_TCP, opt, value)
            except OSError:
                pass


def send_to_server(payload):
    """One send attempt with timeout. Returns True on success, False on any failure."""
    sock = None
    try:
        sock = socket.create_connection((SERVER_IP, SERVER_PORT),
                                        timeout=SOCKET_TIMEOUT)
        sock.settimeout(SOCKET_TIMEOUT)
        _set_keepalive(sock)
        sock.sendall(payload.encode('utf-8'))
        return True
    except Exception as e:
        log_event.warning('SEND   | failed: %s', e)
        return False
    finally:
        if sock is not None:
            try:
                sock.close()
            except Exception:
                pass


# --- Unsent-data buffer (thread-safe, disk-capped) ---
unsent_lock = threading.Lock()


def _trim_unsent_head_locked():
    """Drop oldest lines if file exceeds the cap. Caller holds unsent_lock."""
    try:
        size = os.path.getsize(UNSENT_FILE)
        if size <= MAX_UNSENT_BYTES:
            return
        with open(UNSENT_FILE, 'rb') as f:
            data = f.read()
        target = MAX_UNSENT_BYTES * 9 // 10   # trim to 90% so we don't trim on every append
        excess = len(data) - target
        cut = data.find(b'\n', excess)
        data = b'' if cut == -1 else data[cut + 1:]
        with open(UNSENT_FILE, 'wb') as f:
            f.write(data)
        log_event.warning('BUFFER | trimmed unsent file to %d bytes (cap %d)',
                          len(data), MAX_UNSENT_BYTES)
    except Exception as e:
        log_event.warning('BUFFER | trim failed: %s', e)


def buffer_unsent_data(line):
    """Append a packet to the unsent buffer. Bounded by MAX_UNSENT_BYTES."""
    with unsent_lock:
        try:
            with open(UNSENT_FILE, 'a+') as f:
                f.write(line + '\n')
            _trim_unsent_head_locked()
        except Exception as e:
            log_event.warning('BUFFER | could not append: %s', e)


def flush_unsent_data():
    """Drain unsent_data.txt by resending. Runs from flusher_loop."""
    # Snapshot under lock then truncate, so the main thread's appends don't race.
    with unsent_lock:
        try:
            if not os.path.exists(UNSENT_FILE) or os.path.getsize(UNSENT_FILE) == 0:
                return
            with open(UNSENT_FILE, 'r') as f:
                snapshot = f.read()
            open(UNSENT_FILE, 'w').close()
        except Exception as e:
            log_event.warning('BUFFER | snapshot failed: %s', e)
            return

    lines = [l for l in snapshot.splitlines() if l.strip()]
    if not lines:
        return

    log_event.info('BUFFER | attempting flush of %d packets', len(lines))
    sent = 0
    remaining = []
    for i, line in enumerate(lines):
        if send_to_server(line):
            sent += 1
        else:
            remaining = lines[i:]   # stop on first failure; rest stay buffered
            break

    if not remaining:
        log_event.info('BUFFER | flushed all %d', sent)
        return

    # Prepend `remaining` back, ahead of anything the main thread appended.
    with unsent_lock:
        try:
            appended = ''
            if os.path.exists(UNSENT_FILE):
                with open(UNSENT_FILE, 'r') as f:
                    appended = f.read()
            with open(UNSENT_FILE, 'w') as f:
                for l in remaining:
                    f.write(l + '\n')
                if appended:
                    f.write(appended)
            log_event.info('BUFFER | flushed %d, %d kept', sent, len(remaining))
            _trim_unsent_head_locked()
        except Exception as e:
            log_event.warning('BUFFER | rewrite failed: %s', e)


def flusher_loop():
    while True:
        time.sleep(FLUSH_INTERVAL)
        try:
            flush_unsent_data()
        except Exception as e:
            log_event.warning('BUFFER | flusher iteration failed: %s', e)


# --- Frame extraction ---
def extract_frames(buf):
    """Pull complete &...! frames from a raw byte buffer.

    Returns (frames, remaining). `frames` are decoded text payloads (bytes
    between & and !). `remaining` is the unconsumed tail (possibly a partial
    frame) to carry into the next call.
    """
    frames = []
    while True:
        start = buf.find(b'&')
        if start == -1:
            return frames, b''
        end = buf.find(b'!', start + 1)
        if end == -1:
            return frames, buf[start:]
        raw = buf[start + 1:end]
        buf = buf[end + 1:]
        text = raw.decode('utf-8', errors='replace')
        # Match original validation: payload must contain exactly two '@'
        # and no embedded framing characters.
        if text.count('@') != 2 or '&' in text or '!' in text:
            log_event.warning('RECV   | malformed frame discarded: %r', text[:120])
            continue
        frames.append(text)


# --- Main ---
def main():
    global last_loop_tick

    log_event.info('========== STARTING UP ==========')

    threading.Thread(target=watchdog_loop, name='watchdog', daemon=True).start()
    threading.Thread(target=flusher_loop, name='flusher', daemon=True).start()

    ser = None
    while ser is None:
        try:
            ser = open_serial()
            log_event.info('SERIAL | connected on %s', SERIAL_PORT)
        except Exception as e:
            log_event.warning('SERIAL | initial connect failed: %s', e)
            time.sleep(1)

    rx_buffer = b''
    packet_count = 0
    send_failures = 0

    while True:
        last_loop_tick = time.monotonic()
        try:
            chunk = ser.read(4096)
            if not chunk:
                continue

            rx_buffer += chunk
            if len(rx_buffer) > RX_BUFFER_MAX:
                dropped = len(rx_buffer) - RX_BUFFER_MAX
                rx_buffer = rx_buffer[-RX_BUFFER_MAX:]
                log_event.warning('RECV   | rx buffer overflow, dropped %d bytes', dropped)

            frames, rx_buffer = extract_frames(rx_buffer)

            for payload in frames:
                packet_count += 1
                pi_ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                data_with_time = '%s|%s' % (pi_ts, payload)

                log_event.info('RECV   | #%d | %s', packet_count, payload)
                log_backup.info('%s', data_with_time)

                try:
                    NodeValue.ContentFromClient(payload).sensorvalues()
                except Exception as e:
                    log_event.warning('NODEVAL| %s', e)

                if send_to_server(data_with_time):
                    if send_failures:
                        log_event.info('SEND   | recovered after %d failures', send_failures)
                    send_failures = 0
                    log_event.info('SEND   | OK | #%d -> %s:%d',
                                   packet_count, SERVER_IP, SERVER_PORT)
                else:
                    send_failures += 1
                    log_event.warning('SEND   | #%d buffered (consecutive failures: %d)',
                                      packet_count, send_failures)
                    buffer_unsent_data(data_with_time)

        except (serial.SerialException, termios.error, OSError) as e:
            log_event.warning('SERIAL | disconnected: %s', e)
            try:
                ser.close()
            except Exception:
                pass
            ser = reconnect_serial()
            rx_buffer = b''

        except Exception as e:
            log_event.error('ERROR  | %s', e)


if __name__ == '__main__':
    main()
