#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import serial
import time
import subprocess
import glob

BAUD = 115200
CHECK_HOST = "8.8.8.8"
CHECK_INTERVAL = 60       # seconds between checks
REBOOT_WAIT = 80          # seconds after modem reboot
MAX_FAILS = 3

APN = "airtlegprs.com"    # Set your APN here

# --------------------------------------------------

def find_modem_port():
    ports = sorted(glob.glob("/dev/ttyUSB*"))
    return ports[-1] if ports else None

def open_modem():
    port = find_modem_port()
    if not port:
        print("No modem port found")
        return None
    try:
        ser = serial.Serial(port, BAUD, timeout=5)
        time.sleep(1)
        return ser
    except Exception as e:
        print("Failed to open modem:", e)
        return None

def send_at(ser, cmd, wait=2):
    print(f"AT> {cmd}")
    ser.write((cmd + "\r\n").encode())
    time.sleep(wait)
    try:
        resp = ser.read_all().decode(errors="ignore")
        print(resp.strip())
        return resp
    except:
        return ""

# --------------------------------------------------

def reboot_modem():
    ser = open_modem()
    if not ser:
        return False

    print("Rebooting modem...")
    ser.write(b"AT+CFUN=1,1\r\n")
    time.sleep(1)
    ser.close()

    print("Waiting for modem reboot...")
    time.sleep(REBOOT_WAIT)
    return True

# --------------------------------------------------

def wait_for_registration(timeout=120):
    ser = open_modem()
    if not ser:
        return False

    start = time.time()
    while time.time() - start < timeout:
        reg = send_at(ser, "AT+CREG?")
        if ",1" in reg or ",5" in reg:
            print("Network registered")
            ser.close()
            return True
        time.sleep(5)

    ser.close()
    print("Network registration timeout")
    return False

# --------------------------------------------------

def setup_modem():
    print("Setting up modem...")

    ser = open_modem()
    if not ser:
        return False

    send_at(ser, "AT")
    send_at(ser, "ATE1")
    send_at(ser, 'AT+QCFG="usbnet",1')
    send_at(ser, f'AT+CGDCONT=1,"IP","{APN}"')
    ser.close()

    if not reboot_modem():
        return False

    if not wait_for_registration():
        return False

    ser = open_modem()
    if not ser:
        return False

    send_at(ser, "AT+QNETDEVCTL=1,1,1")
    time.sleep(10)
    ser.close()

    print("Bringing up usb0 interface...")
    subprocess.run(["ip", "link", "set", "usb0", "up"])
    subprocess.run(["dhclient", "-v", "usb0"])

    return True

# --------------------------------------------------

def check_internet():
    return subprocess.call(
        ["ping", "-c", "2", CHECK_HOST],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    ) == 0

# --------------------------------------------------

def main():
    print("=== EC200U Modem Internet Stabilizer ===")

    if not setup_modem():
        print("Initial modem setup failed")

    fail_count = 0

    while True:
        internet_ok = check_internet()
        print(f"[Status] Internet = {internet_ok}")

        if not internet_ok:
            fail_count += 1
            print(f"Internet failure count: {fail_count}/{MAX_FAILS}")
        else:
            fail_count = 0

        if fail_count >= MAX_FAILS:
            print("Internet unstable → Restarting modem...")
            setup_modem()
            fail_count = 0

        time.sleep(CHECK_INTERVAL)

# --------------------------------------------------

if __name__ == "__main__":
    main()
