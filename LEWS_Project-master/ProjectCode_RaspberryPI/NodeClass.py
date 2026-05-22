from time import sleep
import os
import sys
from datetime import datetime
import random
import Send_sms

class ContentFromClient:
  #time_th=21600
  time_th=1800
  initial=[True,True,True,True]
  temp_pressure=[[200,200,200,200,200],[200,200,200,200,200],[200,200,200,200,200],[200,200,200,200,200],[200,200,200,200,200],[200,200,200,200,200],[200,200,200,200,200]] # This is four node and five sensor in every node
  temp_roll=[[1200,1200,1200,1200],[1200,1200,1200,1200],[1200,1200,1200,1200],[1200,1200,1200,1200],[1200,1200,1200,1200],[1200,1200,1200,1200],[1200,1200,1200,1200]]
  temp_pitch=[[45.2,45.2,45.2,42.2,42.2,42.2,42.2],[45.2,45.2,45.2,45.2,45.2,45.2,45.2],[45.2,45.2,45.2,45.2,45.2,45.2,45.2],[45.2,45.2,45.2,45.2,45.2,45.2,45.2]] # pitch is a special case in which a list represent similar pitch like p1 p1 p1 p1
  temp_moisture=[50,50,50,50,50,50,50]
  flag=[False,False,False,False]
  demo_min=52
  demo_max=39
  m_min=[46,56,43,52,demo_min,demo_min]
  m_max=[34,41,39,39,demo_max,demo_max]
  #r=[[],[],[],[],[],[],[]]
  temp_date=[datetime.now(),datetime.now(),datetime.now(),datetime.now()]

  def __init__(self,content):
    self.content=content.lower()
    print(content)
  
  def getTotalNodes(self):
    count = 0
    for i in self.content:
      count += 1
    return count
      
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
    try:
      all1=[]
      temp=self.getlocationName()
      coordinator_name=self.getCordinatorName()
      node_name=self.getNodeName()
      index=self.content.find(')',1)
      now=datetime.now()
      index_node=-1
      if node_name=='n1':
        index_node=0;
      if node_name=='n2':
        index_node=1;
      if node_name=='n3':
        index_node=2;
      if node_name=='n4':
        index_node=3
      if node_name=='n5':
        index_node=4
      if node_name=='n6':
        index_node=5
      if node_name=='n7':
        index_node=6
      if node_name=='n8':
        index_node=7
      if node_name=='n9':
        index_node=8
      difference=(now-ContentFromClient.temp_date[index_node]).total_seconds()   
      sms='Possibility of landsliding at '+coordinator_name+' , '+node_name+' at '+now.strftime("%m/%d/%Y, %H:%M:%S")+' . Sensors Values are:' 
      while(index!=-1):
        #print(index)
        id=''
        temp=self.content[1:index]
        if(temp.startswith('pressure')):
          indexofcolon=self.content.find(':')
          name=self.content[1:indexofcolon]
          value=self.content[indexofcolon+1:index]
          self.content=self.content[index+1:]
          if name=='pressure1':
            index_pr=0;
          if name=='pressure2':
            index_pr=1;
          if name=='pressure3':
            index_pr=2  
          if value=="nan":
              index=self.content.find(')',1)
              continue;
          pressure_value=float(value)
          if((abs((abs(ContentFromClient.temp_pressure[index_node][index_pr])-abs(pressure_value)))>=12) and (difference>=ContentFromClient.time_th or ContentFromClient.initial[index_node])):
            ##print('i am in pre')
            #sms=sms
            ContentFromClient.flag[index_node]=True
            
            #print('THERE IS A POSSSIBILITY OF LANDSLIDE AT '+coordinator_name+'  '+node_name+'. SENSOR name IS '+name+' having value is '+value+' At time '+now.strftime("%m/%d/%Y, %H:%M:%S"))  
          ContentFromClient.temp_pressure[index_node][index_pr]=pressure_value
          
            
        #print(id)
          

        if(temp.startswith('moisture')):
          indexofcolon=self.content.find(':')
          name=self.content[1:indexofcolon]
          value=self.content[indexofcolon+1:index]
          self.content=self.content[index+1:]
        #id=node_id+'_'+'ms'+name[len(name)-1]
        #print(value)
          if value=="nan":
              index=self.content.find(')',1)
              continue;
          moisture_value=float(value)
          moisture_percentage=100*(abs(ContentFromClient.m_min[index_node]-moisture_value))/(abs(abs(ContentFromClient.m_min[index_node])-abs(ContentFromClient.m_max[index_node])))
          #print(moisture_percentage)
          if(((abs(moisture_percentage))>=70) and (difference>=ContentFromClient.time_th or ContentFromClient.initial[index_node])):
            #print('i am in MOISTURE')
            #ms=sms+' \n ' +name+' : '+str(moisture_percentage)
            ContentFromClient.flag[index_node]=True
            #print('THERE IS A POSSSIBILITY OF LANDSLIDE AT '+coordinator_name+'  '+node_name+'. SENSOR name IS '+name+' having value is '+value+' At time '+now.strftime("%m/%d/%Y, %H:%M:%S"))  
          ContentFromClient.temp_moisture[index_node]=moisture_value


        if(temp.startswith('roll')):
          indexofcolon=self.content.find(':')
          name=self.content[1:indexofcolon]
          value=self.content[indexofcolon+1:index]
          self.content=self.content[index+1:]
        #print(value)
          if name=='roll1':
            index_roll=0
          if name=='roll2':
            index_roll=1
          if name=='roll3':
            index_roll=2
          if name=='roll4':
            index_roll=3
          if value=="nan":
              index=self.content.find(')',1)
              continue;
          roll_value=float(value)
          if(abs((abs(ContentFromClient.temp_roll[index_node][index_roll])-abs(roll_value)))>=2 and (difference>=ContentFromClient.time_th or ContentFromClient.initial[index_node])):
            #print('i am in roll')
            #sms=sms+' \n '+name+' : '+value
            #sms=sms
            ContentFromClient.flag[index_node]=True
            #print('THERE IS A POSSSIBILITY OF LANDSLIDE AT '+coordinator_name+'  '+node_name+'. SENSOR name IS '+name+' having value is '+value+' At time '+now.strftime("%m/%d/%Y, %H:%M:%S"))  
          ContentFromClient.temp_roll[index_node][index_roll]=roll_value        


        if(temp.startswith('pitch')):
          indexofcolon=self.content.find(':')
          name=self.content[1:indexofcolon]
          value=self.content[indexofcolon+1:index]
          self.content=self.content[index+1:]
        #print(value)
          if value=="nan":
              index=self.content.find(')',1)
              continue;
        
          pitch_value=float(value)
          
          if name=='pitch1':
            index_pitch=0
          if name=='pitch2':
            index_pitch=1
          if name=='pitch3':
            index_pitch=2
          if name=='pitch4':
            index_pitch=3

          if(abs((abs(ContentFromClient.temp_pitch[index_pitch][index_node])-abs(pitch_value)))>=2 and (difference>=ContentFromClient.time_th or ContentFromClient.initial[index_node])):
            #print('i am in pitch')
            #sms=sms
            ContentFromClient.flag[index_node]=True
            #print('THERE IS A POSSSIBILITY OF LANDSLIDE AT '+coordinator_name+'  '+node_name+'. SENSOR name IS '+name+' having value is '+value+' At time '+now.strftime("%m/%d/%Y, %H:%M:%S"))  
          ContentFromClient.temp_pitch[index_pitch][index_node]=pitch_value        
        
        
        if(temp.startswith('voltage')):
          indexofcolon=self.content.find(':')
          name=self.content[1:indexofcolon]
          value=self.content[indexofcolon+1:index]
          self.content=self.content[index+1:]
        #print(value)
        
          if value=="nan":
              index=self.content.find(')',1)
              continue;
          if(float(value)>=10000):
            pass
            #Send_sms.send_sms('VOLTAGE VALUE IS CROSSING THRESOLD '+value)  
          #Send.send_msg('lews.sailab@gmail.com','rjvkmr80@gmail.com','Roll VALUE IS CROSSING THRESOLD '+value)  
        #print(id)
        


        if(temp.startswith('vols')):
          indexofcolon=self.content.find(':')
          name=self.content[1:indexofcolon]
          value=self.content[indexofcolon+1:index]
          self.content=self.content[index+1:]
        #print(value)
          if value=="nan":
              index=self.content.find(')',1)
              continue;
        
          if(float(value)>=10000):
            pass
            #Send_sms.send_sms('VOLS VALUE IS CROSSING THRESOLD '+value)  
          #Send.send_msg('lews.sailab@gmail.com','rjvkmr80@gmail.com','PITCH VALUE IS CROSSING THRESOLD '+value)  

        index=self.content.find(')',1)
      #print(ContentFromClient.flag[index_node])
      #print(ContentFromClient.flag)
      #if ContentFromClient.flag[index_node]:
          
       # Send_sms.send_sms(sms)
        #print(sms)
        #print(ContentFromClient.flag)
        #print('SMS SENT')
        #ContentFromClient.temp_date[index_node]=now
        #ContentFromClient.initial[index_node]=False
        #ContentFromClient.flag[index_node]=False
             
      #print(ContentFromClient.flag)  
    except Exception as e:
        print("ANY ERROR",e)
    

if __name__ == "__main__":
  c=ContentFromClient("c1@netala@n2(moisture1:50.45)(voltage1:7.20)(vols1:4095.00)(pitch1:-6)(roll1:43)(pressure1:176.56)")
  c.sensorvalues()
  sleep(4)
  c=ContentFromClient("c1@netala@n2(moisture1:43.5)(voltage1:7.20)(vols1:4095.00)(pitch1:-6)(roll1:43)(pressure1:176.56)")
  c.sensorvalues()
  '''
  sleep(3)
  print('first')
  c=ContentFromClient("c1@netala@n1(moisture1:50.55)(voltage1:4.25)(vols1:2637.00)(pitch1:-4)(roll1:31)(pitch1:45.2)")
  c.sensorvalues()
  sleep(25)
  c=ContentFromClient("c1@netala@n1(moisture1:35.55)(voltage1:4.25)(vols1:2637.00)(pitch1:-4)(roll1:31)(pitch1:45.2)")
  c.sensorvalues()
  sleep(25)
  c.sensorvalues()
  #sleep(3)
  print('second')
  c=ContentFromClient("c1@netala@n3(moisture1:52.55)(voltage1:3.85)(vols1:2189.00)(pressure1:195.98)")
  c.sensorvalues()
  #sleep(3)
  print('THIRD')
  
  c=ContentFromClient("c1@netala@n1(moisture1:40.26)(voltage1:4.25)(vols1:2637.00)(pitch1:-4)(roll1:31)(pitch45.2:-6)")
  c.sensorvalues()
  sleep(3)
  print('fourth')
  
  
  c=ContentFromClient("c1@netala@n2(moisture1:56.48)(voltage1:3.66)(vols1:2269.00)(pitch1:-85)(roll1:-12)(pitch2:24)(roll2:-68)(pitch3:86)(roll3:1)(pitch4:1)(roll4:84)")
  c.sensorvalues()
  
  sleep(3)
  
  c=ContentFromClient("c1@netala@n2(moisture1:56.48)(voltage1:3.66)(vols1:2269.00)(pitch1:-85)(roll1:-12)(pitch2:24)(roll2:-68)(pitch3:86)(roll3:1)(pitch4:1)(roll4:84)")
  c.sensorvalues()'''
  
  #c1@netala@n4(moisture1:52.15)(voltage1:3.43)(vols1:2126.00)(pressure1:nan)(pressure2:134.67)
  

  
  
  
  print('DONE')
  pass
  

