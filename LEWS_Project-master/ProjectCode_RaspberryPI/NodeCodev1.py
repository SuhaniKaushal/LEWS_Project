#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import os
import socket
from datetime import datetime
import NodeValue
import serial
import subprocess

SERIAL_PORT = '/dev/ttyUSB7'
BAUD = 115200
SERVER_IP = "103.37.200.35"
SERVER_PORT = 5000
MODEM_MANAGER = "/usr/bin/python3 /home/sailab/modem_manager.py"
PING_HOST = "8.8.8.8"
DATA_LOG_FILE = "/home/sailab/ProjectCode/received_dataset.txt"


# ---------------- LOGGING ---------------- #

def log_error(msg):
    with open('/home/sailab/ProjectCode/log_error.txt', 'a+') as f:
        f.write(f"{datetime.now()} - {msg}\n")

def log_info(msg):
    with open('/home/sailab/ProjectCode/log_info.txt', 'a+') as f:
        f.write(f"{datetime.now()} - {msg}\n")

# ---------------- INTERNET CHECK ---------------- #

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

# ---------------- MODEM RESTART ---------------- #

def restart_modem_manager(reason):
    log_info(f"Internet down → restarting modem manager. Reason: {reason}")
    print("Restarting modem manager...")
    subprocess.Popen(MODEM_MANAGER, shell=True)
    time.sleep(10)

# ---------------- OPEN DATASET DISPLAY WINDOW ---------------- #

def open_dataset_window():
    subprocess.Popen(
        f'lxterminal -e "bash -c \'echo RECEIVED DATASET WINDOW; tail -f {DATA_LOG_FILE}; exec bash\'"',
        shell=True
    )

# Open dataset window at startup
open_dataset_window()

# ---------------- SERIAL CONNECT ---------------- #

while True:
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD, timeout=3)
        print("Serial connected")
        break
    except Exception as e:
        print("Serial not ready, retrying...", e)
        log_error(f"Serial connect failed: {e}")
        time.sleep(2)

# ---------------- MAIN LOOP ---------------- #

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

        # -------- DISPLAY SEPARATELY -------- #
        print("\n==============================")
        print(received_data)
        print("==============================\n")

        # Write to dataset file (for second window)
        with open(DATA_LOG_FILE, 'a+') as f:
            f.write(f"{received_data} {datetime.now()}\n")

        # Process values
        c = NodeValue.ContentFromClient(received_data)
        c.sensorvalues()

        # -------- CHECK INTERNET -------- #
        if not internet_connected():
            restart_modem_manager("No ping response")
            raise ConnectionError("Internet down")

        # -------- SEND DATA -------- #
        host = socket.gethostbyname(SERVER_IP)
        s = socket.create_connection((host, SERVER_PORT), 5)
        s.sendall(bytes(received_data, 'utf-8'))
        s.close()

        print("Data sent")

    # ---------------- ERROR HANDLING ---------------- #

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
