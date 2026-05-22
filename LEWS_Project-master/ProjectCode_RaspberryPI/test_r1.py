#!/usr/bin/python3
import time
import socket
from datetime import datetime
import NodeValue
import serial
import subprocess
import glob

BAUD = 115200
SERVER_IP = "103.37.200.35"
SERVER_PORT = 5000
PING_HOST = "8.8.8.8"

# --------------------------------------------------
def find_zigbee_port():
    ports = sorted(glob.glob("/dev/ttyUSB*"))
    for port in ports:
        try:
            ser = serial.Serial(port, BAUD, timeout=1)
            time.sleep(1)
            if ser.in_waiting > 0:
                ser.close()
                return port
            ser.close()
        except:
            continue
    return None

# --------------------------------------------------
# SERIAL CONNECT (ONCE)
# --------------------------------------------------
while True:
    try:
        ZIGBEE_PORT = find_zigbee_port()
        if not ZIGBEE_PORT:
            raise Exception("Zigbee not found")

        ser = serial.Serial(ZIGBEE_PORT, BAUD)
        print("✅ Connected to Zigbee on", ZIGBEE_PORT)
        break

    except Exception as e:
        print("Waiting for Zigbee...", e)
        time.sleep(2)

# --------------------------------------------------
# MAIN LOOP (MATCHES YOUR OLD LOGIC)
# --------------------------------------------------
buffer = b""   # RAW BYTE BUFFER

while True:
    try:
        print("waiting on serial")

        chunk = ser.read(ser.inWaiting() or 1)
        if not chunk:
            continue

        buffer += chunk
        print("RAW CHUNK:", chunk)

        # Look for frame start & end
        start = buffer.find(b'&')
        end = buffer.find(b'!')

        if start == -1 or end == -1 or end < start:
            # buffer too noisy or incomplete
            if len(buffer) > 4096:
                buffer = buffer[-1024:]  # prevent memory blow-up
            continue

        frame = buffer[start + 1:end]
        buffer = buffer[end + 1:]  # remove processed data

        # Now decode ONLY the frame
        received_data = frame.decode("ascii", errors="ignore")

        # Validate format
        if received_data.count('@') != 2:
            continue

        print("✅ FRAME:", received_data)

        # Log
        with open('/home/pi/Desktop/latest/All.txt', 'a+') as f:
            f.write(received_data + " " + str(datetime.now()) + "\n")

        # Process
        c = NodeValue.ContentFromClient(received_data)
        c.sensorvalues()

        # Send to server
        host = socket.gethostbyname("103.37.200.35")
        s = socket.create_connection((host, 5000), 5)
        s.sendall(received_data.encode())
        s.close()

        print("📡 Data sent")

    except Exception as e:
        print("❌ ERROR:", e)
        time.sleep(1)
