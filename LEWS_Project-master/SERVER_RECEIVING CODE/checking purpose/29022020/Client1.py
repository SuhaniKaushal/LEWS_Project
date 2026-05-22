import socket             
 
s = socket.socket()       
  
# Define the port on which you want to connect  
port = 10000                
  
# connect to the server on local computer  
s.connect(('10.13.1.211', port))  

s.sendall(b'c1@netala@n1(moisture1:40.70)(voltage1:3.72)(vols1:2311.00)(pitch1:-95)(roll1:-95)(pitch2:86)(roll2:-2)(pitch3:-95)(roll3:-95)(pitch4:84)(roll4:3)')
s.close()
