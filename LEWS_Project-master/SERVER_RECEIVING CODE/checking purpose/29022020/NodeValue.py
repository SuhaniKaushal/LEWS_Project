# This is the latest code till 28/02/2020
from Sensorinformation import Sensorinformation
import os
import sys
import psycopg2
from datetime import datetime
import random
import Send

class ContentFromClient:
  a=20
  connection=None
  cursor=None
  def __init__(self,content):
    self.content=content.lower()
    #print(content)
    
  def opendatabase():
    try:
      connection = psycopg2.connect(user="postgres",password="Root@123",host="127.0.0.1",port="5002",database="postgres")
      cursor = connection.cursor()
      return connection,cursor
    except Exception:
      print("THERE IS SOME PROBLEM",Exception)
  
  
  connection,cursor=opendatabase()
  
  #print('i am')
  def close():
    cursor.close()
    connection.close()
    
    
  def get_node_id(self,cname,name):
    try:
      #print(ContentFromClient.a)
      query="select node_id from node where name='"+name+"' and location='"+cname+"'"
      cursor=ContentFromClient.cursor
      #print(query)
      cursor.execute(query)
      node_records = cursor.fetchall()
      node_id=node_records[0][0]
      #print('here',node_id)
      return node_id
      
    except Exception as e:
      print("PROBLEM IN FETCH node ID",e)
      return None
  
  def getTotalNodes():
    for i in content:
      pass
      
      
  def  getlocationName(self):
    indexofname=self.content.find('@')
    name=self.content[0:indexofname]
    self.content=self.content[indexofname+1:]
    return name
    
  def  getCordinatorName(self):
      indexofname=self.content.find('@')
      name=self.content[0:indexofname]
      self.content=self.content[indexofname+1:]
      return name
    
    
  def  getNodeName(self):
    indexofname=self.content.find('(')
    name=self.content[0:indexofname]
    self.content=self.content[indexofname:]
    return name
    
      
  def sensorvalues(self):
    all1=[]
    temp=self.getlocationName()
    coordinator_name=self.getCordinatorName()
    node_name=self.getNodeName()
    
    node_id=self.get_node_id(coordinator_name,node_name)
    if node_id == None:
      print('cant insert ')
      return;
    index=self.content.find(')',1)
    
    while(index!=-1):
      id=''
      temp=self.content[1:index]
      
      if(temp.startswith('pressure')):
        indexofcolon=self.content.find(':')
        name=self.content[1:indexofcolon]
        print("name is"+name)
        value=self.content[indexofcolon+1:index]
        print(value)
        self.content=self.content[index+1:]
        s=Sensorinformation(name,value,'presure',coordinator_name)
        #id='rl'+name[len(name)-1]+'_'+node_id
        id=node_id+'_'+'pr'+name[len(name)-1]
        print(id)
        if(float(value)>=20000):
          Send.send_msg('lews.sailab@gmail.com','rjvkmr80@gmail.com','Presure VALUE IS CROSSING THRESOLD '+value)  
        #print(id)


      if(temp.startswith('moisture')):
        indexofcolon=self.content.find(':')
        name=self.content[1:indexofcolon]
        value=self.content[indexofcolon+1:index]
        self.content=self.content[index+1:]
        s=Sensorinformation(name,value,'moisture',coordinator_name)
        #id=node_id+'_'+'ms'+name[len(name)-1]
        id=node_id+'_'+'ms1'
        if(float(value)>=50000):
          Send.send_msg('lews.sailab@gmail.com','rjvkmr80@gmail.com','MOISTURE VALUE IS CROSSING THRESOLD '+value)  
        #print(id)


      if(temp.startswith('roll')):
        indexofcolon=self.content.find(':')
        name=self.content[1:indexofcolon]
        value=self.content[indexofcolon+1:index]
        self.content=self.content[index+1:]
        s=Sensorinformation(name,value,'roll',coordinator_name)
        id=node_id+'_'+'ro'+name[len(name)-1]
        if(float(value)>=20000):
          Send.send_msg('lews.sailab@gmail.com','rjvkmr80@gmail.com','Roll VALUE IS CROSSING THRESOLD '+value)  
        #print(id)
       
       
      if(temp.startswith('voltage')):
        indexofcolon=self.content.find(':')
        name=self.content[1:indexofcolon]
        value=self.content[indexofcolon+1:index]
        self.content=self.content[index+1:]
        s=Sensorinformation(name,value,'voltage',coordinator_name)
        id=node_id+'_'+'voltage'+name[len(name)-1]
        if(float(value)>=20000):
          Send.send_msg('lews.sailab@gmail.com','rjvkmr80@gmail.com','Roll VALUE IS CROSSING THRESOLD '+value)  
        #print(id)

      if(temp.startswith('vols')):
        print('in VOLS')
        indexofcolon=self.content.find(':')
        name=self.content[1:indexofcolon]
        value=self.content[indexofcolon+1:index]
        print(name,value)
        self.content=self.content[index+1:]
        s=Sensorinformation(name,value,'vols',coordinator_name)
        id=node_id+'_'+'vols'+name[len(name)-1]
        if(float(value)>=20000):
          Send.send_msg('lews.sailab@gmail.com','rjvkmr80@gmail.com','Roll VALUE IS CROSSING THRESOLD '+value) 


      if(temp.startswith('pitch')):
        indexofcolon=self.content.find(':')
        name=self.content[1:indexofcolon]
        value=self.content[indexofcolon+1:index]
        self.content=self.content[index+1:]
        s=Sensorinformation(name,value,'pitch',coordinator_name)
        id=node_id+'_'+'pi'+name[len(name)-1]
        #print(id)
        if(float(value)>=2000):
          Send.send_msg('lews.sailab@gmail.com','rjvkmr80@gmail.com','PITCH VALUE IS CROSSING THRESOLD '+value)  
      s5=datetime.now()
      
      try:
        postgres_insert_query = 'INSERT INTO sensor_data (sensor_id,sensor_value,receive_time) VALUES (%s,%s,%s)'
        record_to_insert = (id,value,s5)
        print('pair is',id,value,s5)
        print("id is")
        if value=="nan" or id==None:
          print("YES")
          index=self.content.find(')',1)
          continue
        ContentFromClient.cursor.execute(postgres_insert_query,record_to_insert)
        ContentFromClient.connection.commit()
        print("ENTERED IN DATABASE")
      except Exception as e:
        print('DATA CANT INSERT IN DATABASE DUE TO ',e)
        
        ContentFromClient.connection.close()
        ContentFromClient.cursor.close() 
        ContentFromClient.connection,ContentFromClient.cursor=ContentFromClient.opendatabase()
      #query_insert="insert into sensor_data values(?,?,?)"
      index=self.content.find(')',1)
    
    

if __name__ == "__main__":
  print('hi')
  c=ContentFromClient("c1@netala@n1(moisture1:581.02)(pitch10:-75)(roll1:-4)(pitch2:-95)(roll2:-95)(pitch3:-95)(roll3:-95)(pitch4:-95)(roll4:-95)")
  #c=ContentFromClient("c1@tangni@n1(moisture1:39.99)(pitch1:-4)(roll1:-17)(pitch2:1)(roll2:-36)(pitch3:0)(roll3:-64)(pitch4:5)(roll4:-85)")
  #c=ContentFromClient("c1@tangni@n4(moisture1:52.75)(pressure:nan)")
  c=ContentFromClient("&c1@netala@n2(moisture1:55.69)(voltage1:3.41)(vols1:2118.00)")

  
  
  c.sensorvalues()
  print('DONE')
  #pass
  
