#!/usr/bin/python3
import sys
print('NEW DATA')
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
#from wireless import Wireless
#wire = Wireless()

try:
 #status =wire.connect(ssid='HUAWEI-9F29',password='Root@123')
 #if status == True:
  #print("NET IS PROPERLY CONNECTED")
 #else:
  #print("NET IS NOT CONNECTED")
  pass
except:
 print('ANY ISSUE IN NETWORKING')   #print('i have came here')

while(True):
    try:
      
      ser.flush()
      time.sleep(1)
      
      
      received_data = ser.read() # Read the newest output
      #received_data = "HELLO NEW DATA" # Read the newest output 
      time.sleep(0.05)
      data_left = ser.inWaiting()
      received_data += ser.read(data_left)
      print(received_data,'is received from Sensor')
      index_strt=received_data.find('&')
      index_end=received_data.find('!')
      if((index_strt>0 or index_strt == -1 or index_end<index_strt) and len(received_data)>10):
        #print('i am in loop2')
        continue;#print (received_Data)
      
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
      #connection=False
      #if not connection:
      if True:
        print('I AM TRYING TO CONNECT WIFI')
        f = open("LOG.txt", "a+")
        if len(received_data)>10:
          now = datetime.now()
          f.write('%s'%now)
          f.write("\r\n")
          f.write(received_data)
          f.write("\r\n")
          f.close()
        received_data=""
        #connection=wire.connect(ssid='HUAWEI-9F29',password='Root@123')
        
        #print("Connected");
                
      

