from tkinter import messagebox as mb
from tkinter import *
from tkinter import ttk
from functools import partial
import psycopg2
from tkinter import Widget

def database():
  try:
    connection = psycopg2.connect(user="postgres",password="Root@123",host="127.0.0.1",port="5002",database="postgres")
    cursor = connection.cursor()
    print('CONNECTION DONE')
    return connection,cursor
  except Exception as e:
    print("THERE IS SOME PROBLEM",e)
    return None,None

connection,cursor=database()

main=Tk()

def f1():
  frame1.pack_forget()
def f2():
  frame1.pack()
def f3():
  print('THIRD')
def f4():
  exit(0)
  
def  add_location(main):
  global frame3,frame2,frame1
  try:
    print(type(frame2))
    frame2.pack_forget()
  except Exception as e:
    print("IN FRAME",e)
    
  try:
   frame3.pack_forget()
  except Exception as e:
    print("IN FRAME",e)
    
  frame1 = Frame(main, width=100, height=100)
  frame1.pack()
  name=Label(frame1,text="NODE NAME",pady=10,padx=10)
  tname=Entry(frame1)
  location=Label(frame1,text="NODE LOCATION",pady=10,padx=10)
  tlocation=Entry(frame1)
  node_id=Label(frame1,text="NODE ID",pady=10,padx=10)
  tnode=Entry(frame1)
  remark=Label(frame1,text="REMARK",pady=10,padx=10)
  tremark=Entry(frame1)
  cbutton=Button(frame1,text="NODE",pady=10)
  
  
  
  name.grid(row=0)
  tname.grid(row=0,column=1)
  location.grid(row=1)
  tlocation.grid(row=1,column=1)
  node_id.grid(row=2)
  tnode.grid(row=2,column=1)
  remark.grid(row=3)
  tremark.grid(row=3,column=1)
  cbutton.grid(row=4,column=1)
  cbutton.bind('<Button-1>', insert_data)

frame1,frame2,frame3=None,None,None

def insert_data(event):
  text=event.widget.cget('text')
  parentName = event.widget.winfo_parent()
  parent     = event.widget._nametowidget(parentName)
  list_value=[]
  for child in parent.winfo_children():
    print(child)
    print(type(child))
    if type(child) == Entry:
      list_value.append(child.get())  
    if type(child) == ttk.Combobox:
      list_value.append(child.get())  
  
  print(list_value)
  if text == "NODE":
    s1=list_value[0]
    s2=list_value[1]
    s3=list_value[2]
    s4=list_value[3]
    try:
      postgres_insert_query = 'INSERT INTO node(name,location,node_id,remark) VALUES (%s,%s,%s,%s)'
      record_to_insert = [s1,s2,s3,s4]
      cursor.execute(postgres_insert_query,record_to_insert)
      connection.commit()
      count = cursor.rowcount
      if count==1:
        print (count, "Record inserted successfully into Node table")
        mb.showerror("Query Status", "Record inserted successfully")
            
      else:
        mb.showerror("Query Status", "Record not inserted successfully")
          
    except Exception as e:
      print(e)  
  if text == "TYPE":
    try:
      s1=list_value[0]
      postgres_insert_query = 'INSERT INTO sensor_list(sensor_name) VALUES (%s)'
      record_to_insert = [s1]
      cursor.execute(postgres_insert_query,record_to_insert)
      connection.commit()
      count = cursor.rowcount
      if count==1:
        print (count, "Record inserted successfully into Node table")
        mb.showerror("Query Status", "Record inserted successfully")
            
      else:
        mb.showerror("Query Status", "Record not inserted successfully")
          
    except Exception as e:
      print(e)
  if text == "PLACE":
    s1_type=list_value[0]
    s2_node=list_value[1]
    depth=list_value[2]
    remark=list_value[3]
    list_1=0
    
    try:
      prequery="select sensor_id from sensor_info where sensor_type='"+s1_type+"' and node_id='"+s2_node+"' order by sensor_id desc "
      print(prequery)
      cursor.execute(prequery)
      node_records = cursor.fetchall()
      print(prequery)
      for row in node_records:
        list_1=int(row[0][-1])
        print(list_1)
        print(type(list_1))
        break;
      list_1=list_1+1
      sensor_id=s2_node+'_'+s1_type[0:2]+str(list_1)
      print(sensor_id)
      
      postgres_insert_query = 'INSERT INTO sensor_info(sensor_id,sensor_type,node_id,depth,remark) VALUES (%s,%s,%s,%s,%s)'
      record_to_insert = [sensor_id,s1_type,s2_node,int(depth),remark]
      
      cursor.execute(postgres_insert_query,record_to_insert)
      connection.commit()
      count = cursor.rowcount
      if count==1:
        print (count, "Record inserted successfully into Node table")
        mb.showerror("Query Status", "Record inserted successfully")
                
      else:
        mb.showerror("Query Status", "Record not inserted successfully")
              
    except Exception as e:
      print(e)

def add_sensor_type(main):
  global frame1,frame3,frame2
  try:
      frame1.pack_forget()
  except Exception as e:
    print("IN FRAME",e)
      
  try:
     frame3.pack_forget()
  except Exception as e:
    print("IN FRAME",e)
    
    
  frame2 = Frame(main, width=100, height=100)
  frame2.pack()
  sensor_name=Label(frame2,text="SENSOR_NAME",pady=10,padx=10)
  tsensor_name=Entry(frame2)
  cbutton=Button(frame2,text="TYPE",pady=10)
  cbutton.bind('<Button-1>', insert_data)
  
  
  sensor_name.grid(row=0)
  tsensor_name.grid(row=0,column=1)
  cbutton.grid(row=1,column=1)
  


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


def place_sensor(main):
  global frame1,frame2,frame3
  try:
   frame1.pack_forget()
  except Exception as e:
    print("IN FRAME",e)
      
  try:
    frame2.pack_forget()
  except Exception as e:
   print("IN FRAME",e)
  frame3 = Frame(main, width=100, height=100)
  frame3.pack()
  
  list_node=fetch("select node_id from node")   
  sensor_list=fetch("select distinct sensor_type from sensor_info")
  
  sensor_type=Label(frame3,text="TYPE",pady=10)
  tsensor_type=ttk.Combobox(frame3,values=sensor_list,width=17)
  tsensor_type.current(0)
  
  parent_name=Label(frame3,text="NODE",pady=10)
  tparent_name=ttk.Combobox(frame3,values=list_node,width=17)
  tparent_name.current(0)
  
  depth=Label(frame3,text="DEPTH",pady=10)
  tdepth=Entry(frame3)
  
  sensor_remark=Label(frame3,text="REMARK",pady=10)
  tsensor_remark=Entry(frame3)
  
  
  cbutton=Button(frame3,text="PLACE",pady=10)
  
  sensor_type.grid(row=0)
  tsensor_type.grid(row=0,column=1)
  parent_name.grid(row=1)
  tparent_name.grid(row=1,column=1)
  depth.grid(row=2)
  tdepth.grid(row=2,column=1)
  sensor_remark.grid(row=3)
  tsensor_remark.grid(row=3,column=1)
  cbutton.grid(row=4,column=1)
  cbutton.bind('<Button-1>', insert_data)


menubar=Menu(main)

menu_first=Menu(menubar, tearoff=0)
menu_first.add_command(label="ADD TYPE",command=partial(add_sensor_type,main))
menu_first.add_command(label="ADD LOACTION",command=partial(add_location,main))
menu_first.add_command(label="PLACE SESNOR",command=partial(place_sensor,main))
menu_first.add_command(label="EXIT",command=f4)

menubar.add_cascade(label="ADD", menu=menu_first)
main.config(menu=menubar)



def f1(event):
    frame1.pack_forget()



main.mainloop()
