# This is the latest code till 25/05/2020
import time;
import select
import socket
import sys
import queue
import time
import Sensorinformation
import NodeValue
from datetime import datetime

# Create a TCP/IP socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setblocking(0)

# Bind the socket to the port
server_address = ('10.13.1.211', 10000)
server.bind(server_address)

# Listen for incoming connections

server.listen(5)

inputs=[server]
outputs=[]

message_queues = {}
print('waiting for request')
while inputs:
  readable, writable, exceptional = select.select(inputs, outputs, inputs,0)
  for s in readable:     
    if s is server:
      connection, client_address = s.accept()
      connection.setblocking(0)
      inputs.append(connection)
      print('connection done')
    else:
      try:
        data = s.recv(2000)
        print('I have received data')
        
        if data:
          print('DATA RECEIVED')
          f=open('A.txt','a+')
          process_data=data.decode('utf-8').lower()
          print(process_data)
          print(len(process_data))
          c=NodeValue.ContentFromClient(process_data)
          c.sensorvalues()
          #f.write(process_data)
          
          
          now = datetime.now()
          f.write('%s'%now)
          f.write("\r\n")
          f.write(process_data)
          
          
          
          
                    
          if process_data[len(process_data)-1] == ')':
            f.write('\n')
          f.close()
          print('WRITTEN IN DATA')
          print("")
          print("")
          print("")
          print("")
          print("")
          print(process_data)
        else:
          inputs.remove(s)
          s.close()
          print('out')
        
      except Exception as e:
        print('in',e)
        if s in inputs:
          inputs.remove(s)
           
  for s in exceptional:
    print('i am in exceptional')
    inputs.remove(s)
    if s in outputs:
      outputs.remove(s)
      s.close()
  
          # Remove message queue
  
  for item in inputs:
    #print(item)
    pass
