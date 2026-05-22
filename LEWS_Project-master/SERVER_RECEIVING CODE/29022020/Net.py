import select
import socket
import sys
import threading
import Sensorinformation
import NodeValue
from datetime import datetime

# Force unbuffered stdout so logs never appear "stuck"
# This is the root cause of the hung-log issue: Python block-buffers
# stdout when not attached to an interactive terminal (e.g. nohup, screen,
# or pipe). Prints accumulate silently in a memory buffer and only appear
# when the buffer fills (~4-8 KB) or the process exits / receives Ctrl+C.
sys.stdout.reconfigure(line_buffering=True)

# Shared lock for all print/log calls across threads to prevent interleaved output
_print_lock = threading.Lock()


def log(msg):
    """Timestamped, thread-safe log."""
    with _print_lock:
        print('[%s] %s' % (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), msg), flush=True)


# Create a TCP/IP socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.setblocking(0)

# Bind the socket to the port
server_address = ('localhost', 5000)
# server_address = ('10.13.1.211', 5000)
server_address = ('192.168.104.84', 5000)
server.bind(server_address)

# Listen for incoming connections
server.listen(128)

inputs = [server]
outputs = []

log('SERVER started on %s:%d' % (server_address[0], server_address[1]))


def process_data_async(process_data):
    """Process received data in a separate thread so the select loop stays responsive."""
    try:
        # Data format from Pi: "YYYY-MM-DD HH:MM:SS|sensordata"
        # If timestamp prefix is present, extract it as the Pi's receive_time
        if '|' in process_data:
            pi_timestamp_str, sensor_data = process_data.split('|', 1)
            try:
                pi_timestamp = datetime.strptime(pi_timestamp_str.strip(), '%Y-%m-%d %H:%M:%S')
            except ValueError:
                # Malformed timestamp, fall back to server time
                sensor_data = process_data
                pi_timestamp = datetime.now()
        else:
            # Backwards compatibility: no timestamp prefix
            sensor_data = process_data
            pi_timestamp = datetime.now()

        c = NodeValue.ContentFromClient(sensor_data, pi_timestamp)
        c.sensorvalues()

        with open('A.txt', 'a+') as f:
            now = datetime.now()
            f.write('%s' % now)
            f.write("\r\n")
            f.write(sensor_data)
            if sensor_data[-1] == ')':
                f.write('\n')
        log('SAVED to A.txt | %s' % sensor_data[:60])
    except Exception as e:
        log('ERROR processing data: %s' % e)


active_connections = 0

while inputs:
    readable, writable, exceptional = select.select(inputs, outputs, inputs, 1)
    for s in readable:
        if s is server:
            connection, client_address = s.accept()
            connection.setblocking(0)
            inputs.append(connection)
            active_connections += 1
            log('CONNECT from %s:%d | active=%d' % (client_address[0], client_address[1], active_connections))
        else:
            try:
                data = s.recv(2000)

                if data:
                    process_data = data.decode('utf-8').lower()
                    if process_data.startswith("get"):
                        continue
                    log('RECV %d bytes | %s' % (len(process_data), process_data[:80]))

                    # Process in a worker thread to keep the select loop free
                    t = threading.Thread(target=process_data_async, args=(process_data,))
                    t.daemon = True
                    t.start()
                else:
                    inputs.remove(s)
                    s.close()
                    active_connections -= 1
                    log('DISCONNECT | active=%d' % active_connections)

            except Exception as e:
                log('ERROR on client socket: %s' % e)
                if s in inputs:
                    inputs.remove(s)
                s.close()
                active_connections -= 1

    for s in exceptional:
        log('ERROR exceptional condition on socket')
        inputs.remove(s)
        if s in outputs:
            outputs.remove(s)
        s.close()
        active_connections -= 1
