#!/usr/bin/python3




#!/usr/bin/python3
import sys
print('NEW DATA..................................')
#print(sys.version)
import time

import select
import socket
import json
#import httplib
#import urllib
from datetime import datetime
import NodeValue
import serial
ser = serial.Serial('/dev/ttyUSB0', 115200)
from wireless import Wireless
wire = Wireless()
try:
 
 status =wire.connect(ssid='HUAWEI_1B6B',password='Root@123')
 if status == True:
  print("NET IS PROPERLY CONNECTED")
 else:
  print("NET IS NOT CONNECTED")
except:
 print('ANY ISSUE IN NETWORKING')   #print('i have came here')
temp=''

try:
    
  from Net_email import Emailer
  Emailer().sendmail('amritajoshi.er@gmail.com','NHMS','SERVER HAS BEEN STARTED')
  print('MAIL SENT')
except Exception as e:
  print("mail cant send",e)
  f1 = open("/home/pi/Desktop/latest/error1.txt", "w+")
  now1 = datetime.now()
  f1.write(str(e))
  f1.write(' ')
  f1.write('%s'%now1)
  f1.write("\r\n")
  f1.close()

while(True):
    try:
      
      print('waiting on serial')
      ser.flush()
      time.sleep(1)
      
      
      data = ser.read() # Read the newest output
      #data = b"&c1@netala@n2(moisture1:56.48)(voltage1:3.66)(vols1:2269.00)(pitch1:-85)(roll1:-12)(pitch2:24)(roll2:-68)(pitch3:86)(roll3:1)(pitch4:1)(roll4:84)!" # Read the newest output 
      time.sleep(0.05)
      data_left = ser.inWaiting()
      data += ser.read(data_left)
      #print(received_data,'is received from Sensor')
      received_data=data.decode()
      #received_data="tch2:-95)(roll2:-95)(pitch3:18)(roll3:-74)(pitch4:-95)(roll4:-95)!"
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
      f=open('/home/pi/Desktop/latest/All.txt','a+')
      f.write(received_data)
      now3 = datetime.now()
      f.write('%s'%now3)
      f.write("\r\n")
      
      f.close()
      print(received_data)
      time.sleep(1)
    
      c=NodeValue.ContentFromClient(received_data)
      c.sensorvalues()
      
      #print('here')
      host = socket.gethostbyname("103.37.200.16")
      s = socket.create_connection((host, 5000), 2)
      s.sendall(bytes(received_data,'utf-8'))
      print("data send")
      
      s.close()
    except Exception as e:
      print(e,'')
      print('DATA CANT SEND')      
      f = open("/home/pi/Desktop/latest/error1.txt", "a+")
      now1 = datetime.now()
      f.write(str(e))
      f.write(' ')
      f.write('%s'%now1)
      f.write("\r\n")
      f.close()
      connection=False
      if not connection:
        print('I AM TRYING TO CONNECT WIFI')
        f = open("/home/pi/Desktop/latest/LOG.txt", "a+")
        if len(received_data)>10:
          now = datetime.now()
          f.write('%s'%now)
          f.write("\r\n")
          f.write(received_data)
          f.write("\r\n")
          f.close()
        received_data=""
        #connection=wire.connect(ssid='HUAWEI-9F29',password='Root@123')
        connection =wire.connect(ssid='HUAWEI_1B6B',password='Root@123')
        print("Connected");





















'''
import sys
print('NEW DATA..................................')
#print(sys.version)
import time

import select
import socket
import json
#import httplib
import urllib
from datetime import datetime
#import NodeValue
#import Send_sms
import serial
ser = serial.Serial('/dev/ttyUSB0', 115200)
from wireless import Wireless
wire = Wireless()

try:
 status =wire.connect(ssid='HUAWEI_1B6B',password='Root@123')
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
      
      print('waiting')
      received_data = ser.read() # Read the newest output
      #received_data = "&c1@netala@n2(moisture1:56.48)(voltage1:3.66)(vols1:2269.00)(pitch1:-85)(roll1:-12)(pitch2:24)(roll2:-68)(pitch3:86)(roll3:1)(pitch4:1)(roll4:84)!" # Read the newest output 
      print(received_data)
      time.sleep(0.05)
      data_left = ser.inWaiting()
      received_data += ser.read(data_left)
      
      
      
      print(received_data,'is received from Sensor')
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
      f=open('/home/pi/Desktop/latest/All.txt','a+')
      f.write(received_data)
      now3 = datetime.now()
      f.write('%s'%now3)
      f.write("\r\n")
      
      f.close()
      print(received_data)
      time.sleep(1)
      #received_data='hi'
      
      #c=NodeValue.ContentFromClient(received_data)
      #c.sensorvalues()
      
      
      host = socket.gethostbyname("103.37.200.16")
      s = socket.create_connection((host, 5000), 2)
      s.sendall(received_data)
      print("data send")
      
      s.close()
    except Exception as e:
      print(e,'')
      print('DATA CANT SEND')      
      f = open("/home/pi/Desktop/latest/error.txt", "a+")
      now1 = datetime.now()
      f.write(str(e))
      f.write(' ')
      f.write('%s'%now1)
      f.write("\r\n")
      f.close()
      connection=False
      if not connection:
        print('I AM TRYING TO CONNECT WIFI')
        f = open("/home/pi/Desktop/latest/LOG.txt", "a+")
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






