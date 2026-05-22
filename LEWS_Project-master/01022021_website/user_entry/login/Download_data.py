import psycopg2
import tkinter as tk
from tkcalendar import DateEntry
from tkinter import messagebox as mb
from tkinter import *
from tkinter import ttk
from functools import partial
from tkinter import Widget
import csv
import datetime
from decimal import *

def fetch_dataset(sensor_id,from_date,to_date,):
   
  sensor_data=""
  if len(sensor_id)==0:
    print('any value is missing')
    return
  
  for i in sensor_id:
    sensor_data=sensor_data+"'"+i+"',"
  sensor_data=sensor_data[0:len(sensor_data)-1]
  
 
  
  query="select node.node_id,receive_time,sensor_info.sensor_id,sensor_data.sensor_value from sensor_data , sensor_info ,node where sensor_data.sensor_id=sensor_info.sensor_id and sensor_info.node_id=node.node_id and receive_time between '"+str(from_date)+"' and '"+str(to_date)+"' and sensor_info.sensor_id in ("+sensor_data+")  order by receive_time desc"
  print(query)
  cursor.execute(query)
  temp_data=[]
  node_records = cursor.fetchall()
  temp=0
  i=0
  dict_data=[]
  f=open('data.csv', 'w', newline='')
  writer = csv.writer(f)
  writer.writerow(['NODE_NAME','roll1','roll1_f','roll2','roll2_f','roll3','roll3_f','roll4','roll4_f','pitch1','pitch1_f','pitch2','pitch2_f','pitch3','pitch3_f','pitch4','pitch4_f','presure1','presure1_f','presure2','presure2_f','presure3_f','presure3','presure4','presure4_f','moisture','voltage1','voltage1_f','volts1','volts','T'])
  temp=['','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','']
  count_date=0
  date_data=None
  temp_data=None
  index=-1
  for row in node_records:
    col_data=[]                
    for col in row:
      #print(type(col))
      
      if count_date>1 and ((temp_data-date_data).total_seconds()>10):
      #print((temp_data-date_data).total_seconds())
        temp[30]=temp_data	
        temp_data=date_data
        writer.writerow(temp)
        print(temp)
        temp=['','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','']
      
      if isinstance(col,Decimal):
        #print(index,'  ',col,end=' ')
        temp[index]=col
        #print(temp)
      
      
      if isinstance(col,datetime.datetime) and count_date>0:
       date_data=col
       count_date=count_date+1
       
      if isinstance(col,datetime.datetime) and count_date==0:
        temp_data=col
        count_date=count_date+1
      
      
      
      if isinstance(col,str):
        u_in=col.rindex('_')
        temp_col=col[:u_in]
        col=col[u_in+1:]
        
              
        if col=="n1" or col=="n2" or col=="n3" or col=="n4" or col=="n5":
          #print('i am here')
          temp[0]=col
        
        if col=="ro1":
          index=1
        if col=="ro2":
          index=3
        if col=="ro3":
          index=5
        if col=="ro4":
          index=7
          
        if col=="pi1":
          index=9
        if col=="pi2":
          index=11
        if col=="pi3":
          index=13
        if col=="pi4":
          index=15
        
        
        
        if col=="pr1":
          index=17
        if col=="pr2":
          index=19
        if col=="pr3":
          index=21
        if col=="pr4":
          index=23
        
        
        
        if col=='ms1':
          index=25
        
        if col=='voltage1':
          index=26
          
        if col=='vols1':
          index=28
        
        if col=='f':
          u_in=temp_col.rindex('_')
          col=temp_col[u_in+1:]
          
          if col=="ro1":
            index=2
          if col=="ro2":
            index=4
          if col=="ro3":
            index=6
          if col=="ro4":
            index=8
 
          if col=="pi1":
            index=10
          if col=="pi2":
            index=12
          if col=="pi3":
            index=14
          if col=="pi4":
           index=16



          if col=="pr1":
            index=18
          if col=="pr2":
            index=20
          if col=="pr3":
            index=22
          if col=="pr4":
            index=24



          if col=='voltage1':
            index=27

          if col=='vols1':
            index=29


    
  
  print("CODE OVER")
  

def opendatabase():
   try:
     connection = psycopg2.connect(user="postgres",password="Root@1234A",host="127.0.0.1",port="5432",database="postgres")
     cursor = connection.cursor()
     return connection,cursor
   except Exception:
     print("THERE IS SOME PROBLEM",Exception)


connection,cursor=opendatabase()


def f1():
  s=cal.get_date()
  print(cal.get_date())
  print(type(cal.get_date()))
  
def fetch(query):
  list=[]
  try:
    cursor.execute(query)
    node_records = cursor.fetchall()
    
    for row in node_records:
      a=row[0]
      list.append(a)
    return list     
  except Exception as e :
      print("PROBLEM IN FETCH",e)
      return None;
  
  
