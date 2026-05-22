# This is the latest code till 28/02/2020
from Sensorinformation import Sensorinformation
import os
import sys
from datetime import datetime
import random
import csv

class ContentFromClient:
  def __init__(self,content):
    self.content=content.lower()


  temp_data=['','','','','','','','','','','','','','','','','','','','','','','','']    
  
 
  def write_in_file(self):
    #f=open('data_log.csv', 'w', newline='')
    f=open('data_log.csv', 'w')
    writer = csv.writer(f)   
       
       writer.writerow(['location_name','co_ordinator_name','node_name','roll1','roll2','roll3','roll4','pitch1','pitch2','pitch3','pitch4','presure1','presure2','presure3','presure4','moisture','voltage','vols','year','month','day','hr','min','sec'])
    writer.writerow(self.temp_data)
    f.close()
  
  
  
  
  def  getlocationName(self):
    indexofname=self.content.find('@')
    name=self.content[0:indexofname]
    self.content=self.content[indexofname+1:]
    self.temp_data[0]=name
    return name
    
  def  getCordinatorName(self):
      indexofname=self.content.find('@')
      name=self.content[0:indexofname]
      self.content=self.content[indexofname+1:]
      self.temp_data[1]=name
      return name
    
    
  def  getNodeName(self):
    indexofname=self.content.find('(')
    name=self.content[0:indexofname]
    self.content=self.content[indexofname:]
    self.temp_data[2]=name
    return name
    
      
  def sensorvalues(self):
    all1=[]
    temp=self.getlocationName()
    coordinator_name=self.getCordinatorName()
    node_name=self.getNodeName()   
    index=self.content.find(')',1)
    while(index!=-1):
      id=''
      temp=self.content[1:index]
      
      if(temp.startswith('pressure')):
        indexofcolon=self.content.find(':')
        name=self.content[1:indexofcolon]
        value=self.content[indexofcolon+1:index]
        self.content=self.content[index+1:]
        if  name=="pressure1":
          self.temp_data[11]=value
        if  name=="pressure2":
          self.temp_data[12]=value
        if  value=="pressure1":
          self.temp_data[13]=value
        if  value=="pressure1":
          self.temp_data[14]=value  
                


      if(temp.startswith('moisture')):
        indexofcolon=self.content.find(':')
        name=self.content[1:indexofcolon]
        value=self.content[indexofcolon+1:index]
        self.content=self.content[index+1:]
        self.temp_data[15]=value  
        


      if(temp.startswith('roll')):
        indexofcolon=self.content.find(':')
        name=self.content[1:indexofcolon]
        value=self.content[indexofcolon+1:index]
        self.content=self.content[index+1:]
        if  name=="roll1":
          self.temp_data[3]=value
        if  name=="roll2":
          self.temp_data[4]=value
        if  name=="roll3":
          self.temp_data[5]=value
        if  name=="roll4":
          self.temp_data[6]=value        


      if(temp.startswith('voltage')):
        indexofcolon=self.content.find(':')
        name=self.content[1:indexofcolon]
        value=self.content[indexofcolon+1:index]
        self.content=self.content[index+1:]
        #print(type(value))
        self.temp_data[16]=value        
                

      if(temp.startswith('vols')):
        indexofcolon=self.content.find(':')
        name=self.content[1:indexofcolon]
        value=self.content[indexofcolon+1:index]
        self.content=self.content[index+1:]
        self.temp_data[17]=value           
      
        
      if(temp.startswith('pitch')):
        indexofcolon=self.content.find(':')
        name=self.content[1:indexofcolon]
        value=self.content[indexofcolon+1:index]
        self.content=self.content[index+1:]
        #print(type(value))
        if  name=="pitch1":
          self.temp_data[7]=value
        if  name=="pitch2":
          self.temp_data[8]=value
        if  name=="pitch3":
          self.temp_data[9]=value
        if  name=="pitch4":
          self.temp_data[10]=value
        
        
      index=self.content.find(')',1)        
      print(self.content)
    
    now=datetime.now()
    self.temp_data[18]=now.year
    self.temp_data[19]=now.month
    self.temp_data[20]=now.day
    self.temp_data[21]=now.hour
    self.temp_data[22]=now.minute
    self.temp_data[23]=now.second
      
      
    print("OPERTION EXECUTED")
    

if __name__ == "__main__":
  c=ContentFromClient("c1@tangni@n1(moisture1:581.02)(voltage1:20)(vols5:1986.00)(pitch1:-75)(pressure1:100)(roll1:-4)(pitch2:-95)(roll2:-95)(pitch3:-95)(roll3:-95)(pitch4:-95)(roll4:-95)")
  c.sensorvalues()
  c.write_in_file()
  #c=ContentFromClient("c1@tangni@n1(moisture1:39.99)(pitch1:-4)(roll1:-17)(pitch2:1)(roll2:-36)(pressure1:100)(pitch3:0)(roll3:-64)(pitch4:5)(roll4:-85)")
  #c=ContentFromClient("c1@tangni@n4(moisture1:52.75)(pressure:nan)")
  #c.sensorvalues()
  #c=ContentFromClient("c1@tangni@n1(moisture1:39.99)(pitch1:-4)(roll1:-17)(pitch2:1)(roll2:-36)(pitch3:0)(roll3:-64)(pitch4:5)(roll4:-85)")
  #c=ContentFromClient("c1@tangni@n2(moisture1:10)(voltage1:3)(vols1:1000.00)(pitch1:-95)(roll1:-95)(pitch2:-10)(roll2:73)(pitch3:-95)(roll3:-95)(pitch4:-95)(roll4:-95)")
  #c=ContentFromClient("c1@tangni@n5(moisture1:46.26)(voltage2:3.85)(vols1:2192.00)(pitch1:-95)(roll1:-95)(pitch2:-95)(roll2:-95)(pitch3:-6)(roll3:-55)(pitch4:-95)(roll4:-95)")
  file1 = open('LOG.txt', 'r') 
  lines = file1.readlines() 
  for line in lines: 
    pass
    #print(line)
    '''c=ContentFromClient(line)
    c.sensorvalues()
    c.write_in_file()'''
  print('DONE')
  #pass
  
