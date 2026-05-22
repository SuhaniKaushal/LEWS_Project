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

def fetch_dataset():
  node_name = [tnode_name.get(idx) for idx in tnode_name.curselection()]
  
  
  values = [tsensor_type.get(idx) for idx in tsensor_type.curselection()]

  
  from_date=from_cal.get_date()
  to_date=to_cal.get_date()
  #print(node_name,values,from_date,to_date)
  
  node_data=""
  if len(node_name)==0:
    print('any value is missing')
    return
  
  for i in node_name:
    node_data=node_data+"'"+i+"',"
  node_data=node_data[0:len(node_data)-1]
  
  data=""
  if len(values)==0:
    print('any value is missing')
    return
  
  for i in values:
    data=data+"'"+i+"',"
  data=data[0:len(data)-1]
  
  
  query="select node.node_id,receive_time,sensor_info.sensor_id,sensor_data.sensor_value from sensor_data , sensor_info ,node where sensor_data.sensor_id=sensor_info.sensor_id and sensor_info.node_id=node.node_id and receive_time between '"+str(from_date)+"' and '"+str(to_date)+"' and sensor_info.node_id in ("+node_data+") and sensor_type in ("+data+") order by receive_time desc"
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
  
  
root = tk.Tk()


frame1 = tk.Frame(root, width=100, height=100)
frame1.pack()

list_node=fetch("select node_id from node")
sensor_list=fetch("select distinct sensor_type from sensor_info")

name=Label(frame1,text="NODE NAME",pady=10,padx=10)
tnode_name=Listbox(frame1,selectmode = "multiple",exportselection=0)

for each_item in range(len(list_node)):     
  tnode_name.insert(END, list_node[each_item]) 


sensor_type=Label(frame1,text="Sensor_type",pady=10,padx=10)
tsensor_type =Listbox(frame1, selectmode = "multiple",exportselection=0)


for each_item in range(len(sensor_list)):     
  tsensor_type.insert(END, sensor_list[each_item]) 
  
  
from_label=Label(frame1,text="FROM",pady=10,padx=10)
from_cal = DateEntry(frame1, width=12, year=2019, month=6, day=22,background='darkblue', foreground='white', borderwidth=2,selectmode='day',cursor="hand1")

to_label=Label(frame1,text="TO",pady=10,padx=10)
to_cal = DateEntry(frame1, width=12, year=2019, month=6, day=22,background='darkblue', foreground='white', borderwidth=2,selectmode='day',cursor="hand1")

cbutton=Button(frame1,text="NODE",pady=10, command=fetch_dataset)
  

name.grid(row=0)
tnode_name.grid(row=0,column=1)
sensor_type.grid(row=1)
tsensor_type.grid(row=1,column=1)
from_label.grid(row=2)
from_cal.grid(row=2,column=1)
to_label.grid(row=3)
to_cal.grid(row=3,column=1)
cbutton.grid(row=4,column=1)



root.mainloop()


'''print('DONE')

query="select node_id from node"
print(query)
result=cursor.execute(query)
node_records = cursor.fetchall()
print(node_records[0][0])'''
