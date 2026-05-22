from django.http import FileResponse
import matplotlib.font_manager as font_manager
from matplotlib import colors
from django.shortcuts import render
from django.template.loader import render_to_string
# Create your views here.
from django.http import HttpResponse
from django.http import HttpRequest
from django.core import serializers
import psycopg2
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import matplotlib.dates as mdates
from matplotlib.dates import AutoDateFormatter, AutoDateLocator
from django.contrib.auth.tokens import PasswordResetTokenGenerator
import six
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from . import Download_data
from django.core.mail import EmailMessage
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import View, UpdateView
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
#from core.tokens import account_activation_token




from datetime import datetime
matplotlib.use('Agg')

class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            six.text_type(user.pk) + six.text_type(timestamp) +
            six.text_type(user.is_active)
        )
account_activation_token = TokenGenerator()


def opendatabase():
  try:
    connection = psycopg2.connect(user="postgres",password="Root@1234A",host="127.0.0.1",port="5432",database="netala_database")
    cursor = connection.cursor()
    return connection,cursor
  except Exception as e:
    print("THERE IS SOME PROBLEM",e)
  
  
connection,cursor=opendatabase()
  
def unique(list1):
  x = np.array(list1) 
  return np.unique(x).tolist() 


def logout(request):
  check=''
  return render(request,'regis.html',{'message':"YOU HAVE SUCCESSFULLY LOGOUT"})
  

#23.10.2020

def f1():
  print('i have called')
  query="select distinct(sensor_type) from sensor_info"   
  cursor.execute(query)
  node_records = cursor.fetchall()
  sensor="<input type='checkbox' name='st' id='st_id' value='all'>ALL<br>"
  count=1
  for row in node_records:
    sensor=sensor+"<input type='checkbox' name='"
    for col in row:
      sensor=sensor+"st' value='"+col+"'>"+col.upper()+"<br>"
  count=count+1  


  query="select node_id,location,name from node"   
  cursor.execute(query)
  node_records = cursor.fetchall()
  location="<input type='checkbox' name='loc' id='loc_id' value='all'>ALL<br>"
  count=1
  for row in node_records:
    location=location+"<input type='checkbox' name='"
    location=location+"loc' value='"+row[0]+"'>"+row[1].upper()+'@'+row[2].upper()+"<br>"
    count=count+1
  return sensor,location

def prepareQuery(word,data):
  content=word+' in ('
  for temp in data:
    content=content+'\''+temp+'\''+','
  content=content[:len(content)-1]
  content=content+')'
  return content

def f2():
  query="select email_id,uname from user_list where verify='yes' and status != 'accepted'"   
  cursor.execute(query)
  node_records = cursor.fetchall()
  if len(node_records)==0:
    s1="NO RECORD TO VALIDATE"
    return s1
  s1="<table border=1><tr><td>EMAIL</td><td>NAME</td><td>CLICK FOR YES</td></tr>"
  for row in node_records:
    s1=s1+"<tr><td>"+row[0]+"</td><td>"+row[1]+"</td> <td> <input type='checkbox' name='user' value='"+row[0]+"'></td></tr>"
  s1=s1+"</table>"
  return s1
  
def allow(request):
  s1=f2();
  return render(request,'allow.html',{'list':s1})

def insert(request):
  #print(request.POST)
  list_user=request.POST.getlist('user')
  global check
  check="credit"
  connection = psycopg2.connect(user="postgres",password="Root@1234A",host="127.0.0.1",port="5432",database="netala_database")
  cursor = connection.cursor()
  for item in list_user:
    query="update user_list set status='accepted' where email_id='"+item+"'"   
    print(query)
    cursor.execute(query)
    connection.commit()
  connection.close()
  cursor.close()
  return home(request,'web','<a href=allow.html>ALLOW USERS</a>')
  
  

def fetch_info(request):
  num1=[]
  num2=[]
  print(request.POST)
  print(type(request.POST))
  ty=request.POST['val']  
  
  
  num1 = request.POST.getlist('st')
  num2 = request.POST.getlist('loc')
    
  if len(num1)==0 or len(num2)==0: 
    sensor,location=f1()
    return render(request,'home.html',{'sensor':sensor,'location':location,'message_sp':"<font color='RED'>PLEASE SELECT THE VALUES </font>"})
  if 'all' in num2:
    query2="select node_id from node"
  else:
    query2="select node_id from node where "
    query2=query2+prepareQuery('node.node_id',num2)
  print(query2)
  cursor.execute(query2)
  node_records = cursor.fetchall()
  node_id=[]
  for row in node_records:
    for col in row:
      node_id.append(col)
  query="select distinct(sensor_id) from sensor_info"
  if len(num1) !=0 and  'all' not in num1:
    query=query+" where "+prepareQuery('sensor_type',num1) 
    query=query+' and '
  if len(node_id) !=0:
    if "where" not in query:
      query=query+" where "
    query=query+prepareQuery('sensor_info.node_id',node_id)
            #query=query+' and '
  print(query)
  cursor.execute(query)
  node_records = cursor.fetchall()
    
  sensor_id=[]
  for row in node_records:
    for col in row:
      sensor_id.append(col)
          
  sensor_id_list=""
  count=1
  for row in sensor_id:
    sensor_id_list=sensor_id_list+"<input type='checkbox' name='"
    sensor_id_list=sensor_id_list+"sensor_list_id' value='"+row+"'>"+row.upper()+"<br>"
  if ty=="app":
    return render(request,'inter.html',{'sensor_id':sensor_id_list,'hidden_value':'app'})  

  return render(request,'inter.html',{'sensor_id':sensor_id_list,'hidden_value':'browser'})


def index(request):
  return render(request,'regis.html')




count_app=100  


def login_page(request):
  global count_app
  print(type(request.POST))
  name=request.POST['t11']
  password=request.POST['t12']
  status=request.POST['web']
  if request.POST.__contains__('count_app'):
   count_app=request.POST['count_app']
  
  query="select uname,email_id,user_type from user_list where(email_id='"+name+"' and upassword='"+password+"' and status='accepted')"
  global check;
  try:
    cursor.execute(query)
    result=cursor.fetchall()
    print(len(result))
    if len(result) != 0:
      check="credit"
      if status == "app":
        sensor,location=f1()
        print("count_app",count_app)
        if count_app == "0":
          print("YESrt")
          count_app=10
          print(result[0][0]+"#"+result[0][1]+"#"+sensor+"#"+location)
          return HttpResponse(result[0][0]+"#"+result[0][1]+"#"+sensor+"#"+location);
           
        else:
          return home(request,status)
      else:
        if result[0][2]=='SUPERVISOR':
          return home(request,status,'<a href=allow.html>ALLOW USERS</a>')  
        return home(request,status)
    else:
      if status =="app":
        return HttpResponse("credidentals is not correct");     
      else:
        return render(request,'regis.html',{'message':"credidentals are not correct"})
      
  except Exception as e:
    print("ANY ERROR",e)
    if status == "web":
      return render(request,'regis.html',{'message':"INVALID USER"})
    else:
      return HttpResponse("credidentals is not correct"); 



check=""



def home(request,web="app",amessage=''):
  try:
    global check
    print('in home',web)
    if check != "credit":
      if web=="app":
        return HttpResponse("credidentals are not correct"); 
      else:
       return render(request,'home.html',{'message':"YOU ARE NOT A VALID USER"})
    else:
       sensor,location=f1()
       check=""
       print('i have come here ')
       print(sensor,location)
       if web=="app":
         print('last check')
         return render(request,'check.html',{'sensor':sensor,'location':location})
       else:
        print('new DATA',amessage)
        return render(request,'home.html',{'sensor':sensor,'location':location,'admin_message':amessage})
  except Exception as e:
    print('I AM IN EXCEPT',e)
    if web=="app":
      return HttpResponse("YOU ARE NOT A VALID USER.."); 
    else:
       return render(request,'login',{'message':"YOU ARE NOT A VALID USER......."})
    
def add(request):
  a=request.POST["tt"];
  sensor_id=request.POST.getlist('sensor_list_id')
  from_date=request.POST['from_date']
  if len(from_date) == 0:
    x=datetime.now()
    from_date=str(x)[0:10]
    print(from_date)
  from_hr=request.POST['from_hr']
  from_min=request.POST['from_min']
  from_format=str(from_date)+' '+from_hr+':'+from_min+':00'
  to_date=request.POST['to_date']
  if len(to_date) == 0:
    x=datetime.now()
    to_date=str(x)[0:10]
    print(to_date)
  to_hr=request.POST['to_hr']
  to_min=request.POST['to_min']
  to_format=str(to_date)+' '+to_hr+':'+to_min+':00' 
  num3=from_format
  chart_type=request.POST['chart_type']
  duration=request.POST['duration']
  #duration=24
  ott=''
  hyper_data=''
  if request.POST.__contains__('download'):
    ott=request.POST['download']
    Download_data.fetch_dataset(sensor_id,from_date,to_date)
    csv_file = open("data.csv", 'rb')
    response = FileResponse(csv_file)
    hyper_data="<a href='data.csv'>DOWNLOAD</a>"
    #return response
    

  
    
  print(chart_type)
  if chart_type == 'bar': 
    query="select sensor_data.sensor_id,avg(sensor_value),sensor_type from sensor_data,sensor_info where "
    if len(sensor_id) !=0:
      query=query+prepareQuery('sensor_data.sensor_id',sensor_id) 
      query=query+' and '
    query+="receive_time <= (to_timestamp('" +to_format+ "','yyyy-mm-dd hh24:mi:ss')) and receive_time >= (to_timestamp('"+from_format+"', 'yyyy-mm-dd hh24:mi:ss'))"
    query=query+'and sensor_data.sensor_id=sensor_info.sensor_id group by sensor_type,sensor_data.sensor_id order by sensor_type'
    print(query)
      #(to_timestamp('16-05-2011 15:36:38', 'dd-mm-yyyy hh24:mi:ss'))
    cursor.execute(query)
    node_records = cursor.fetchall()
       
    data=[]
    for row in node_records:
      data.append(row)
    print(data)
    if len(data) == 0:
      sensor,location=f1()
      return render(request,'home.html',{'sensor':sensor,'location':location,'message':'NO DATA FOUND'})
    
    x=[row[0] for row in data]
    y=[round(float(row[1]),3) for row in data]
    z=[row[2] for row in data]
    print(row)
    print(x)
    print(y)
    print(z)
    labels = x
    men_means = y
      
    x = np.arange(len(labels))  # the label locations
    width = 0.20  # the width of the bars
    color=['b','g','r','c','m','k', 'tab:brown']
    fig, ax = plt.subplots()
    rects1 = ax.bar(x - width/2, men_means, width)
    for i in range(0,len(rects1)):
      if i>6: i=0;
      rects1[i].set_color(color[i]) 
      
      
      # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel('SENSOR VALUE(AVG')
    ax.set_title('AVG VALUES')
    ax.set_xticks(x)
    ax.set_xticklabels(labels,rotation=90)
    ax.legend(loc='upper center')

    def autolabel(rects):
      for rect in rects:
        height = rect.get_height()
        ax.annotate('{}'.format(height),
        xy=(rect.get_x() + rect.get_width() / 2, height),
        xytext=(0, 3),  # 3 points vertical offset
        textcoords="offset points",
        ha='center', va='bottom')
      
      
    autolabel(rects1)
    fig.tight_layout()

    image_path="'static/testplot.png'"
    plt.savefig('login/testplot.png')
    sensor,location=f1()
      #plt.show()
    #print('HI')
    #print("base is",a)
    if a != "app":
      return render(request,'home.html',{'image_path':image_path,'sensor':sensor,'location':location,'message':'<font color="RED">DATA FOUND</font>'})  
    return render(request,'check.html',{'image_path':image_path,'sensor':sensor,'location':location,'message':'<font color="RED">DATA FOUND</font>'})   
  else:
    print('i m in TIME')
    pre_query="select sensor_type,sensor_id from sensor_info where "
    pre_query=pre_query+prepareQuery('sensor_id',sensor_id)
    print(pre_query)
    cursor.execute(pre_query)
    node_records_pre = cursor.fetchall()
    ty=[row[0] for row in node_records_pre]
    #print(ty)
    set_ty=set(ty)
    set_ty=list(set_ty)
    set_ty=sorted(set_ty)
    print(type(set_ty))
    if len(set_ty)>3:
      sensor,location=f1()
      if a != "app":
        print('i am not app')
        return render(request,'home.html',{'image_path':'','sensor':sensor,'location':location,'message':'<font color="RED">SELECT TWO TYPES AT A TIME</font>','table_data':''})  
      return render(request,'check.html',{'image_path':'','sensor':sensor,'location':location,'message':'YOU CAN ONLY SELECT TWO TYPES AT A TIME','table_data':''})     
    
     
    
    query="select sensor_data.sensor_id,sensor_value,RECEIVE_TIME,sensor_type from sensor_data,sensor_info  where sensor_data.sensor_id=sensor_info.sensor_id and "
    query_second="select sensor_id,sensor_value,DATE_TRUNC('second',receive_time ) from sensor_data where (sensor_id,sensor_value) in ( select sensor_id  ,max(sensor_value) from sensor_data where "
    query_third="select sensor_id , remark from sensor_info where "
    query=query+prepareQuery('sensor_data.sensor_id',sensor_id)
    query_second=query_second+prepareQuery('sensor_id',sensor_id)
    
    query_third=query_third+prepareQuery('sensor_id',sensor_id)
    
    query=query+' and '
    query_second=query_second+' and '
    
    query+="receive_time < (to_timestamp('" +to_format+ "','yyyy-mm-dd hh24:mi:ss')) and receive_time > (to_timestamp('"+from_format+"', 'yyyy-mm-dd hh24:mi:ss'))"
    query_second+="receive_time < (to_timestamp('" +to_format+ "','yyyy-mm-dd hh24:mi:ss')) and receive_time > (to_timestamp('"+from_format+"', 'yyyy-mm-dd hh24:mi:ss'))"
    
    
    query=query+' order by sensor_data.sensor_id,receive_time'
    query_second+='group by sensor_id)'
    
    
    print(query)
    #print(query_second)
    #print(query_third)
    cursor.execute(query)
    node_records = cursor.fetchall()
    
    cursor.execute(query_second)
    node_records_second = cursor.fetchall()
    
    cursor.execute(query_third)
    node_records_third = cursor.fetchall()
    #print(node_records_second)
    
    
    label_dict={}
    for d in node_records_third:
      label_dict[d[0]]=d[1]
    
    
    
    table_data=''
    if len(node_records_second)!=0:
      table_data="<div id='t_data'><table border=1>"
      table_data=table_data+"<tr><td>SENSOR ID</td><td>MAX</td><td>DATE</td></tr>"
      for in_row in node_records_second:
      
        table_data=table_data+"<tr>"
        for in_col in in_row:
          table_data=table_data+"<td>"+str(in_col)+"</td>"
        table_data=table_data+"</tr>"    
      table_data=table_data+"</table></div>"
    if len(node_records)==0:
      sensor,location=f1()
      print('entered')
      if a != "app":
        print('i am not app')
        return render(request,'home.html',{'image_path':'','sensor':sensor,'location':location,'message':'<font color="RED">DATA NOT FOUND</font>','table_data':''})  
      return render(request,'check.html',{'image_path':'','sensor':sensor,'location':location,'message':'DATA NOT FOUND','table_data':''})     
    print('i am executed till here')       
    print(set_ty)
    data=[]
    
    
    for row in node_records:        
      data.append(row)
    sensor_id=unique([row[0] for row in data])
    print(sensor_id)
    sensor_id.sort()
    sensor_value=[row[1] for row in data]
    date_list=[row[2] for row in data]
    sensor_type=unique([row[3] for row in data])
    l1=set_ty[0]
    
    if l1 in 'voltage':
      l1='Voltage(v)'
    if l1 in 'pressure':
      l1='Pressure in Kpa'
    
    if l1 in 'roll':
      l1='Displacement in deg'
    
    if l1 in 'pitch':
      l1='Displacement in deg'
    if l1 in 'moisture':
      l1='Moisture value in %'
    
    #print(data)       
    countd=0
    final_data=[]
    #print('ok31')
      
    fig, ax1 = plt.subplots()
    color = 'tab:red'
    ax1.set_xlabel('time',fontsize=8)
    
    ax1.set_ylabel(l1, fontsize=8,color=color)
    
    if len(set_ty) >=2:  
      ax2 = ax1.twinx()
      ax2.tick_params(axis='y', labelsize=8)
    
    if len(set_ty) >=3:  
      
      ax3 = ax1.twinx()
      ax3.spines["right"].set_position(("axes", 1.15))
      ax3.tick_params(axis='y', labelsize=8)
    ax1.tick_params(axis='y', labelsize=8)
     
      
    color = 'tab:red'
    if len(set_ty)>=3:
      l2=set_ty[1]
      l3=set_ty[2]
      if l2 in 'voltage':
        l2='Voltage(v)'
      if l2 in 'pressure':
        l2='Pressure in Kpa'
      
      if l2 in 'roll':
        l2='Displacement in deg'
      
      if l2 in 'pitch':
        l2='Displacement in deg'
      if l2 in 'moisture':
        l2='Moisture value in %'
        
      if l3 in 'pressure':
        l3='Pressure in Kpa'
            	
      if l3 in 'roll':
        l3='Displacement in deg'
            
      if l3 in 'pitch':
         l3='Displacement in deg'
      if l3 in 'moisture':
         l3='Moisture value in %'
      if l3 in 'voltage':
        l3='Voltage(V)'
      ax2.set_ylabel(l2, fontsize=8,color=color)  # we already handled the x-label with ax1
    #ax2.plot(t, data2, color=color)
      ax3.set_ylabel(l3, fontsize=8,color=color)  # we already handled the x-label with ax1
    #plt.xlabel('DAY',rotation=0)
    #plt.ylabel('SENSOR VALUE',rotation=90)
    
    
    i=-1
    markers = ['<','o', 'v', 'x', 'X', 'D', '|','>', '+', '.', ',']
    count_first=0
    
    for row in range(0,len(sensor_id)):
      flag=False
      flag1=False
      ab=True
      i=i+1
      fy=[]
      fx=[]
      fz=[]
      sy=[]
      sx=[]
      sz=[]
      tx=[]
      ty=[]
      print(sensor_id[row],'NAME OF ID IS')
      sum=0
      y_temp=[]
      for col in range(0,len(data)):
        if data[col][0] == sensor_id[row]:
       	  countd=col
       	  
       	  
       	  # this is special case of pressure only for netala
       	  
          if sensor_id[row]=='nt_n4_pr1' or sensor_id[row]=='nt_n4_pr1_f' or sensor_id[row]=='nt_n4_pr1_r' or sensor_id[row]=='nt_n2_pr1_r':
            change=((float(data[countd][1])/1000-0.2)/4.5)*100
            y_temp.append([data[countd][3],change,data[countd][2]])
            continue;
          if sensor_id[row]=='nt_n1_ms1' or sensor_id[row]=='nt_n3_ms1' or sensor_id[row]== 'nt_n1_ms1_f':
            change=(float(data[countd][1])-11)
            y_temp.append([data[countd][3],change,data[countd][2]])
            continue;
          
          #helpif data[countd][3]=='moisture':
            #helpq="select 100*(min_value-"+str(data[countd][1])+")/(min_value-max_value) from sensor_thresold where sensor_id in ('"+sensor_id[row]+"')"
            #print(q)
            #helpcursor.execute(q)
            #helptemp_sensor = cursor.fetchall()
            #helpy_temp.append([data[countd][3],temp_sensor[0][0],data[countd][2]])
            #helpcontinue
          
          y_temp.append([data[countd][3],data[countd][1],data[countd][2]])
          #x.append(data[countd][2])
          #sum=sum+data[countd][1]
          #z.append(sum)
      
      #print(sensor_id[row])
      #print(y_temp)
      for aa in y_temp:
        if aa[0]==set_ty[0]:
          #print('FIRST SENSOR')
          fy.append(aa[1])
          fx.append(aa[2])
          flag=False
          
        if len(set_ty)>=2 and aa[0]==set_ty[1]:#2,3
          #print('second sensor')
          sy.append(aa[1])
          sx.append(aa[2])
          flag=True
          flag1=False
          
        if len(set_ty)>=3 and aa[0]==set_ty[2]:# only 3
          #print('tird sensor')
          ty.append(aa[1])
          tx.append(aa[2])
          flag=True
          flag1=True 
          
      label=label_dict[sensor_id[row]]
      print("\n\n\n\n\n\n")
      #print(fy)
      #print(sy)
      #print(len(fy))
      #print(len(sy))	
      
      font = font_manager.FontProperties(family='Comic Sans MS',
                                         weight='bold',
                                         style='normal', size=8)
      
      color_line=['red','green','tab:brown','pink','silver','navy','cyan','violet','tab:pink','tab:gray']
      if not(flag):      
        formatter = mdates.DateFormatter("%d-%m-%y")	
        #formatter = mdates.DateFormatter("%d-%m-%Y")
        ax1.xaxis.set_major_formatter(formatter)
        locator = mdates.HourLocator(interval=int(duration))
        #locator = mdates.HourLocator(interval=96)
        #locator = AutoDateLocator()
        ax1.xaxis.set_major_locator(locator)
        
                
        print("firstprint")
        color_line=['red','blue','green','black']
        ax1.plot(fx,fy,label=label,color=color_line[i%10],linewidth=.5,marker=markers[i%6],markersize=.1)
        #ax1.scatter(fx, fy,5)
        #helpax1.legend(bbox_to_anchor=(0,1.25), loc='upper center', prop=font)   
        ax1.legend(loc='upper right', prop=font)
        #ax1.legend(bbox_to_anchor=(.50,1.25), loc='upper right', prop=font)
        #ax1.legend(prop=font)
        
        
        
        # change here for ticks,just two lines  min,max,interval
        #ax1.set_yticks(np.arange(-2.1, -1.7, .1 ))
        #ax2.set_yticks(np.arange(-96, -94, .1))
        #ax1.set_yticks([85.1,85.5, 86.2,86.01,86.02,86.03,86.04,86.05])
        #ax1.set_ylim(top=None,ymin=0,ymax= 119) FOR SOIL MOISTURE
        ax1.set_ylim(-40,4)
        #ax2.set_ylim(0.3, 4.5)
        #ax3.set_ylim(2.8, 4.5)
        for tick in ax1.get_xticklabels(): 
          tick.set_rotation(60)
          tick.set_fontsize(8)
      
      
      print(flag)
      print(ab)
      if len(set_ty)>=2 and flag and ab:
        
        print('came')
        
        formatter = mdates.DateFormatter("%d-%m-%y")
        #formatter = mdates.DateFormatter("d%-%m-Y% ")	
        ax2.xaxis.set_major_formatter(formatter)
        locator = mdates.HourLocator(interval=int(duration))
        #locator = mdates.HourLocator(interval=96)
        #locator = AutoDateLocator()
        ax2.xaxis.set_major_locator(locator)
        
        if len(sx)>0:
          ax2.plot(sx,sy,label=label,color=color_line[i%10],linewidth=.91,marker=markers[(6-i)%6],markersize=.11)
        #ax2.plot(sx,sy,label=label)
        #ax2.scatter(sx, sy,5)
        ax2.legend(prop=font)
        #helpax2.legend(bbox_to_anchor=(.50,1.25), loc='upper center', prop=font,ncol=2)   
        ax2.legend( loc='upper center', prop=font,ncol=1)
        #ax2.xaxis.set_major_locator(locator)
        ab=False
        sx=[]
        sy=[]
        for tick in ax2.get_xticklabels(): 
          tick.set_rotation(60)
          tick.set_fontsize(8)

      
      print('came over')
      if len(set_ty)>=2 and flag and  flag1:
        print("thirdddd sensor")
        formatter = mdates.DateFormatter("%d-%m-%y")
        ax3.xaxis.set_major_formatter(formatter)
        locator = mdates.HourLocator(interval=int(duration))
        ax3.xaxis.set_major_locator(locator)
        print('error2ax3')
        
        ax3.plot(tx,ty,label=label,color=color_line[i%10],linewidth=.5,marker=markers[(6-i)%6],markersize=.09)
        
        print('error1ax3')
        ax3.legend(prop=font)
        ax3.legend(loc='upper left', prop=font)   
        for tick in ax3.get_xticklabels(): 
          tick.set_rotation(60)
          tick.set_fontsize(8)
        for tick in ax3.get_yticklabels(): 
	  #tick.set_rotation(60)
          tick.set_fontsize(8)
    try:
      plt.tight_layout()  
      image_path="'static/testplot.png'"
      plt.savefig('login/testplot.png')  
      print('last')  
        #plt.show()
      plt.close()
      print('nothing')
      sensor,location=f1()
            #plt.show()
      print('last1')
      if a != "app":
        return render(request,'home.html',{'image_path':image_path,'sensor':sensor,'location':location,'message':'DATA FOUND','table_data':table_data,'hyper_data':hyper_data})  
      return render(request,'check.html',{'image_path':image_path,'sensor':sensor,'location':location,'message':'DATA FOUND','table_data':table_data,'hyper_data':hyper_data})   
    except Exception as e:
      print('I AM IN EXCEPTION OK?',e)
      pass
  
def download(request):
  csv_file = open("data.csv", 'rb')
  response = FileResponse(csv_file)
  return response

def activate(request, uidb64, token):
  print('HAS CAME HERE')
  try:
    uid = force_text(urlsafe_base64_decode(uidb64))
    user = User.objects.get(pk=uid)
    print(user.username)
    
  except(TypeError, ValueError, OverflowError, User.DoesNotExist):
    user = None
    print(user)
    print(account_activation_token.check_token(user, token))
  if user is not None and account_activation_token.check_token(user, token):
      #login(request)
    innerquery="update user_list set verify='yes' where uname='"+user.username+"'"
    cursor.execute(innerquery)
    connection.commit();  
    return HttpResponse("Thank you for your email confirmation. Now you can login your account after validate the admin YOU WILL GET THE CONFIRMATION MAIL WHEN ADMIN ALLOWS YOU.<a href='/regis.html'>CLICK HERE TO HOME</a>")
  else:
    return HttpResponse("Activation link is invalid!<a href='/regis.html'>CLICK HERE TO RETURN</a>")  
         #190720950
         
         
         
def registration(request):
  fmessage='PROBLY DUPLICATE USER'
  name=request.POST['t1']
  password=request.POST['t3']
  ph_no=request.POST['t4']
  email=request.POST['t5']
  utype=request.POST['t6']
  web=request.POST["web"]
  query="insert into user_list values('"+name+"','"+password+"','"+ph_no+"','"+email+"','"+utype+"','unaccepted')"
  try:
    print('OK')
    print(account_activation_token)
    
    user= User.objects.create_user(username=name,email=email,password=password)
    
    
    print(user.username)
    current_site = get_current_site(request)

    print(urlsafe_base64_encode(force_bytes(user)))
    print(account_activation_token.make_token(user))
    mail_subject = 'Activate your NMHS account.'
    message = render_to_string('acc_active_email.html',{
                'name': name,
                'domain': current_site.domain,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token':account_activation_token.make_token(user),
            })
    print('OK@')
    semail = EmailMessage(mail_subject, message, to=[email])
    semail.send()
    
    cursor.execute(query)
    connection.commit();
    fmessage="PLEASE CHECK YOUR EMAIL ID"
    print('OK1')
    print(web)
    if web == "app":
      return HttpResponse("PLEASE CONFIRM YOUR EMAIL ID"); 
    else:
      return render(request,'regis.html',{'message':" PLEASE CONFIEM YOUR EMAIL ID"})
  except Exception as e:
    #print("ANY ERROR",e)
    message='DATA HAS NOT BEEN INSERTED,SERVER ERROR'
     
    if web == "app":
      return HttpResponse("DATA HAS BEEN NOT SUBMITTED......"); 
    else:
      print('message is1',e)
      return HttpResponse("DATA HAS BEEN NOT SUBMITTED......"); 
  finally:
    if web=="app":
      return HttpResponse("PLEASE CONFIRM YOUR EMAIL ID"); 
    else:
      print('message is final')
      return render(request,'regis.html',{'message':fmessage})
     

  
  
  #return HttpResponse("DATA HAS BEEN NOT SUBMITTED");
    

