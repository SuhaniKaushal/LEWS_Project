#!/usr/bin/python3






'''import sys
print('NEW DATA..................................')
#print(sys.version)
import time

import select
import socket
import json
#import httplib
import urllib
from datetime import datetime
import NodeValue
import Send_sms
import serial
ser = serial.Serial('/dev/ttyUSB0', 115200)
from wireless import Wireless
wire = Wireless()

try:
 status =wire.connect(ssid='HUAWEI-9F29',password='Root@123')
 if status == True:
  print("NET IS PROPERLY CONNECTED")
 else:
  print("NET IS NOT CONNECTED")
except:
 print('ANY ISSUE IN NETWORKING')   #print('i have came here')
temp=''
while(True):
    try:
      
      ser.flush()
      time.sleep(1)
      
      
      received_data = ser.read() # Read the newest output
      #received_data = "&c1@netala@n2(moisture1:56.48)(voltage1:3.66)(vols1:2269.00)(pitch1:-85)(roll1:-12)(pitch2:24)(roll2:-68)(pitch3:86)(roll3:1)(pitch4:1)(roll4:84)!" # Read the newest output 
      time.sleep(0.05)
      data_left = ser.inWaiting()
      received_data += ser.read(data_left)
      #print(received_data,'is received from Sensor')
      index_strt=received_data.find('&')
      index_end=received_data.find('!')
      if(index_end!=-1 and index_strt!=-1):
        temp=''
      if(index_end==-1 and index_strt==-1):
        temp=''
        continue
      if(index_end!=-1 and index_strt>index_end):
        temp=''
        continue;
      if(index_end==-1):
        temp=received_data
        continue;#
        #print('i am in loop2')
        #print (received_Data)
      received_data=temp+received_data
      temp=''
      received_data=received_data[index_strt+1:index_end]
      print(received_data)
      time.sleep(1)
      #received_data='hi'
      
      c=NodeValue.ContentFromClient(received_data)
      c.sensorvalues()
      
      
      host = socket.gethostbyname("103.37.200.16")
      s = socket.create_connection((host, 5000), 2)
      s.sendall(received_data)
      print("data send")
      
      s.close()
    except Exception as e:
      print(e,'')
      print('DATA CANT SEND')      
      connection=False
      if not connection:
        print('I AM TRYING TO CONNECT WIFI')
        f = open("/home/pi/02012021/tangni/LOG.txt", "a+")
        if len(received_data)>10:
          now = datetime.now()
          f.write('%s'%now)
          f.write("\r\n")
          f.write(received_data)
          f.write("\r\n")
          f.close()
        received_data=""
        connection=wire.connect(ssid='HUAWEI-9F29',password='Root@123')
        
        print("Connected");'''






#!/usr/bin/python3
import select
import socket
import sys
import time
import json
#import httplib
import urllib
print('I AM IN START.....')
#import serial
print('ZZZZZZ2')
#ser = serial.Serial('/dev/ttyUSB0', 115200)
print('ZZZZZZ1')
while(True):
    try:
      #received_data = "hello" # Read the newest output 
      print('ZZZZZZ')
      #ser.flush()
      time.sleep(1)
      #received_data = ser.read()
      received_data='HELLO321654'
      print(received_data)
      time.sleep(0.05)
      #data_left = ser.inWaiting()
      #received_data += ser.read(data_left)
      print(received_data,"")
    except Exception as e:
      print(e,'')
      
      



                
      
