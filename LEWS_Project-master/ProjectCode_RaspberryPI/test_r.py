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
while True:
    try:
        print('waiting on serial')
        ser.flush()
        time.sleep(1)
        data = ser.read() # Read the newest output
     	#data = b"&c1@netala@n2(moisture1:56.48)(voltage1:3.66)(vols1:2269.00)(pitch1:-85)(roll1:-12)(pitch2:24)(roll2:-68)(pitch3:86)(roll3:1)(pitch4:1)(roll4:84)!" # Read the newest output
        print(data)
        time.sleep(0.05)
        data_left = ser.inWaiting()
        data += ser.read(data_left)   #print(received_data,'is received from Sensor')
        received_data=data.decode()
      	#received_data="tch2:-95)(roll2:-95)(pitch3:18)(roll3:-74)(pitch4:-95)(roll4:-95)!"
        index_strt=received_data.find('&')
        index_end=received_data.find('!')
        l=len(received_data);
      	#if(index_end!=-1 and index_strt!=-1):
        	#temp=''
        if(index_end==-1 or index_strt==-1 or received_data.count('@')!=2 or received_data[-1]!='!' or received_data.count('!')!=1  or received_data.count('&')!=1):
        	#temp=''
        	continue
      #if(index_end!=-1 and index_strt>index_end):
        #temp=''
        #continue;
      #if(index_end==-1):
        #temp=received_data
        #continue;#
        #print('i am in loop2')
        #print (received_Data)
      #received_data=temp+received_data
      #temp=''
        received_data=received_data[index_strt+1:index_end]
        f=open('/home/sailab/Raspberry pi code/All.txt','a+')
        f.write(received_data)
        now3 = datetime.now()
        f.write('%s'%now3)
        f.write("\r\n")

        f.close()
        print(received_data)
        time.sleep(1)

    

    except Exception as e:
        print("❌ ERROR:", e)
        time.sleep(1)
