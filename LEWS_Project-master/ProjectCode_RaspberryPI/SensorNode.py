#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import os
import socket
from datetime import datetime
import NodeValue
import serial
import subprocess
import glob

BAUD = 115200
SERVER_IP = "103.37.200.35"
SERVER_PORT = 5000
MODEM_MANAGER = "/usr/bin/python3 /home/sailab/modem_manager.py"
PING_HOST = "8.8.8.8"

# --------------------------------------------------
# LOGGING
# --------------------------------------------------
def log_error(msg):
    with open('/home/sailab/Raspberry pi code/error1.txt', 'a+') as f:
        f.write(f"{datetime.now()} - {msg}\n")

def log_info(msg):
    with open('/home/sailab/Raspberry pi code/LOG.txt', 'a+') as f:
        f.write(f"{datetime.now()} - {msg}\n")

# --------------------------------------------------
# INTERNET CHECK
# --------------------------------------------------
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
    log_info(f"Restarting modem manager. Reason: {reason}")
    print("Restarting modem manager...")
    subprocess.Popen(MODEM_MANAGER, shell=True)
    time.sleep(10)

# --------------------------------------------------
# ZIGBEE PORT DETECTION
# --------------------------------------------------
def find_zigbee_port():
    ports = sorted(glob.glob("/dev/ttyUSB*"))
    print("Scanning for Zigbee USB port...")

    for port in ports:
        try:
            ser = serial.Serial(port, BAUD, timeout=2)
            time.sleep(2)

            if ser.in_waiting > 0:
                data = ser.read(ser.in_waiting)
                print(f"✅ Zigbee device detected on {port}")
                #print("Initial data:", data.decode(errors="ignore"))
                ser.close()
                return port

            ser.close()
        except Exception:
            continue

    return None

# --------------------------------------------------
# SERIAL CONNECT
# --------------------------------------------------
while True:
    try:
        ZIGBEE_PORT = find_zigbee_port()
        if not ZIGBEE_PORT:
            raise Exception("Zigbee USB not found")

        ser = serial.Serial(ZIGBEE_PORT, BAUD, timeout=3)
        print(f"Serial connected to Zigbee on {ZIGBEE_PORT}")
        log_info(f"Zigbee connected on {ZIGBEE_PORT}")
        break

    except Exception as e:
        print("Zigbee serial not ready, retrying...", e)
        log_error(f"Zigbee serial connect failed: {e}")
        time.sleep(3)

# --------------------------------------------------
# MAIN LOOP
# --------------------------------------------------
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
        # 🔹 PRINT RAW ZIGBEE DATA
        if received_data:
            print("📥 Raw Zigbee Data:", received_data)

        with open('/home/sailab/Raspberry pi code/All.txt', 'a+') as f:
            f.write(f"{received_data} {datetime.now()}\n")

        c = NodeValue.ContentFromClient(received_data)
        c.sensorvalues()

        # --- Internet Check ---
        if not internet_connected():
            restart_modem_manager("No ping response")
            raise ConnectionError("Internet down")

        # --- Send Data ---
        host = socket.gethostbyname(SERVER_IP)
        s = socket.create_connection((host, SERVER_PORT), 5)
        s.sendall(received_data.encode("utf-8"))
        s.close()

        print("✅ Data sent to server")

    # --------------------------------------------------
    # ERROR HANDLING
    # --------------------------------------------------
    except serial.SerialException as e:
        print("Serial error:", e)
        log_error(f"SerialException: {e}")
        time.sleep(2)
        try:
            ser.close()
        except:
            pass
        time.sleep(2)

    except socket.timeout:
        print("Socket timeout")
        log_error("Socket timeout")
        restart_modem_manager("Socket timeout")
        time.sleep(5)

    except socket.gaierror:
        print("DNS resolution failed")
        log_error("DNS resolution failed")
        restart_modem_manager("DNS failure")
        time.sleep(5)

    except ConnectionError as e:
        print(e)
        log_error(str(e))
        time.sleep(5)

    except Exception as e:
        print("Unknown error:", e)
        log_error(f"Unknown error: {e}")
        restart_modem_manager("Unknown error")
        time.sleep(5)
