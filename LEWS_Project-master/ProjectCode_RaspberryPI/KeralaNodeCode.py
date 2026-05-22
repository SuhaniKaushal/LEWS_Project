#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto Zigbee Serial Detection Version
"""

import time
import os
import socket
from datetime import datetime
import NodeClass_op
import serial
import serial.tools.list_ports
import subprocess


BAUD = 115200
SERVER_IP = "103.37.200.35"
SERVER_PORT = 5000
MODEM_MANAGER = "/usr/bin/python3 /home/sailab/modem_manager.py"
PING_HOST = "8.8.8.8"


# ------------------ LOGGING ------------------

def print_log(message):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] {message}")

def log_error(msg):
    with open('/home/sailab/ProjectCode/log_error.txt', 'a+') as f:
        f.write(f"{datetime.now()} - {msg}\n")

def log_info(msg):
    with open('/home/sailab/ProjectCode/log_info.txt', 'a+') as f:
        f.write(f"{datetime.now()} - {msg}\n")


# ------------------ INTERNET CHECK ------------------

def internet_connected():
    try:
        subprocess.check_call(
            ["ping", "-c", "1", "-W", "2", PING_HOST],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return True
    except subprocess.CalledProcessError:
        return False


def restart_modem_manager(reason):
    log_info(f"Internet down → restarting modem manager. Reason: {reason}")
    print("Restarting modem manager...")
    subprocess.Popen(MODEM_MANAGER, shell=True)
    time.sleep(75)


# ------------------ ZIGBEE PORT DETECTION ------------------

def find_zigbee_port():
    """
    Automatically detect Zigbee USB serial device.
    Returns the device path (e.g. /dev/ttyUSB0)
    """
    ports = serial.tools.list_ports.comports()

    zigbee_keywords = [
        "zigbee",
        "cc2531",
        "cc2652",
        "cp210",
        "ftdi",
        "ch340",
        "xbee"
    ]

    for port in ports:
        description = (port.description or "").lower()
        manufacturer = (port.manufacturer or "").lower()
        hwid = (port.hwid or "").lower()

        for keyword in zigbee_keywords:
            if keyword in description or keyword in manufacturer or keyword in hwid:
                print_log(f"Zigbee detected: {port.device}")
                return port.device

    # Fallback: first USB serial device
    for port in ports:
        if port.device.startswith("/dev/ttyUSB") or port.device.startswith("/dev/ttyACM"):
            print_log(f"Fallback serial used: {port.device}")
            return port.device

    raise Exception("No Zigbee USB device found")


def wait_for_zigbee():
    while True:
        try:
            port = find_zigbee_port()
            return port
        except Exception as e:
            print("Zigbee not found, retrying...")
            log_error(str(e))
            time.sleep(3)


# ------------------ SERIAL CONNECT ------------------

def connect_serial():
    while True:
        try:
            serial_port = wait_for_zigbee()
            ser = serial.Serial(serial_port, BAUD, timeout=3)
            print_log(f"Serial connected on {serial_port}")
            return ser
        except Exception as e:
            print("Serial connection failed, retrying...", e)
            log_error(f"Serial connect failed: {e}")
            time.sleep(3)


# ================== MAIN PROGRAM ==================

ser = connect_serial()
received_data = ""

while True:
    try:
        ser.flush()
        time.sleep(0.5)

        data = ser.read()
        time.sleep(0.05)
        data_left = ser.inWaiting()
        data += ser.read(data_left)

        received_data = data.decode(errors="ignore")

        index_strt = received_data.find('&')
        index_end = received_data.find('!')

        if (index_end == -1 or index_strt == -1 or
            received_data.count('@') != 2 or
            not received_data.endswith('!') or
            received_data.count('!') != 1 or
            received_data.count('&') != 1):
            continue

        received_data = received_data[index_strt + 1:index_end]

        with open('/home/sailab/ProjectCode/log_data.txt', 'a+') as f:
            f.write(f"{received_data} {datetime.now()}\n")

        c = NodeClass_op.ContentFromClient(received_data)
        c.sensorvalues()

        # -------- SEND DATA TO SERVER --------
        host = socket.gethostbyname(SERVER_IP)
        s = socket.create_connection((host, SERVER_PORT), 5)
        s.sendall(bytes(received_data, 'utf-8'))
        s.close()

        print_log("Data sent successfully")

    # ---------- ERROR HANDLING ----------

    except serial.SerialException as e:
        print("Serial error:", e)
        log_error(f"SerialException: {e}")
        try:
            ser.close()
        except:
            pass
        time.sleep(2)
        ser = connect_serial()
        continue

    except socket.timeout:
        print("Socket timeout")
        log_error("Socket timeout")
        time.sleep(5)

    except socket.gaierror:
        print("DNS resolution failed")
        log_error("DNS resolution failed")
        time.sleep(5)

    except ConnectionError as e:
        print(e)
        log_error(str(e))
        time.sleep(5)

    except Exception as e:
        print("Unknown error:", e)
        log_error(f"Unknown error: {e}")
        time.sleep(5)
