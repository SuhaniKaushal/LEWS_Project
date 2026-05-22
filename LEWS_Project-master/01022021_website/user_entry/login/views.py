import random
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
import mimetypes
import csv
import base64
from io import BytesIO
import pandas as pd



from datetime import datetime
from functools import wraps

matplotlib.use('Agg')


# Decorator to prevent browser caching of authenticated pages
def no_cache(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        response = view_func(request, *args, **kwargs)
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate, private'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        return response
    return wrapper

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
  global check, name
  check = ''
  name = ''
  return redirect('landing')
  

#23.10.2020

def f1(email):
  print('i have called')
  query="select distinct(sensor_type) from sensor_info"   
  cursor.execute(query)
  node_records = cursor.fetchall()
  
  sensor_icons = {
      'all': 'fas fa-layer-group',
      'rain guage': 'fas fa-cloud-rain',
      'pitch': 'fas fa-drafting-compass',
      'pressure': 'fas fa-tachometer-alt',
      'voltage': 'fas fa-bolt',
      'rainfall': 'fas fa-cloud-showers-heavy',
      'vols': 'fas fa-heartbeat',
      'roll': 'fas fa-sync-alt',
      'moisture': 'fas fa-tint'
  }
  
  order = ['all', 'rain guage', 'pitch', 'pressure', 'voltage', 'rainfall', 'vols', 'roll', 'moisture']
  db_sensors = [row[0] for row in node_records]
  
  ordered_sensors = []
  for item in order:
      if item == 'all' or item in db_sensors:
          ordered_sensors.append(item)
          
  sensor = ""
  for item in ordered_sensors:
      icon_class = sensor_icons.get(item, 'fas fa-microchip')
      display_name = 'RAIN GUAGE' if item == 'rain guage' else item.upper()
      is_all = (item == 'all')
      input_id = 'allsen' if is_all else item
      input_val = 'all' if is_all else item
      
      sensor += f"""
      <div class="sensor-card">
          <label class="sensor-card-label" for="{input_id}">
              <div class="checkbox-container">
                  <input type="checkbox" id="{input_id}" name="st" value="{input_val}" class="sensor-checkbox-input">
                  <span class="custom-checkbox"></span>
              </div>
              <div class="sensor-icon">
                  <i class="{icon_class}"></i>
              </div>
              <span class="sensor-name">{display_name}</span>
          </label>
      </div>
      """

  query="select node_id,location,name from node where node_id in (select node_id from node,u_status where node.location=u_status.location and email_id='"+email+"')"   
  cursor.execute(query)
  node_records = cursor.fetchall()
  
  # Sort to match the exact reference image layout order
  location_order = ['all', 'kerela_n5', 'kerela_n3', 'kerela_n1', 'kerela_n8', 'kerela_n6', 'kerela_n7', 'kerela_n4', 'kerela_n0', 'kerela_n9', 'kerela_n2']
  records_dict = {row[0]: row for row in node_records}
  
  ordered_records = []
  for n_id in location_order:
      if n_id == 'all':
          ordered_records.append('all')
      elif n_id in records_dict:
          ordered_records.append(records_dict[n_id])
  
  for n_id, row in records_dict.items():
      if n_id not in location_order:
          ordered_records.append(row)
          
  location = ""
  for row in ordered_records:
      if row == 'all':
          input_id = 'allloc'
          input_val = 'all'
          display_name = 'All'
          icon_class = 'fas fa-th-large'
          card_class = 'location-card location-all-card'
      else:
          input_id = row[0]
          input_val = row[0]
          display_name = f"{row[1].upper()}@{row[2].upper()}"
          icon_class = 'fas fa-map-marker-alt'
          card_class = 'location-card'
          
      location += f"""
      <div class="{card_class}">
          <label class="location-card-label" for="{input_id}">
              <div class="location-left">
                  <div class="checkbox-container">
                      <input type="checkbox" id="{input_id}" name="loc" value="{input_val}" class="location-checkbox-input">
                      <span class="custom-checkbox"></span>
                  </div>
                  <div class="location-icon">
                      <i class="{icon_class}"></i>
                  </div>
                  <span class="location-name">{display_name}</span>
              </div>
              <div class="location-right">
                  <i class="fas fa-chevron-right location-arrow"></i>
              </div>
          </label>
      </div>
      """
  return sensor, location

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
  
  

@no_cache
def fetch_info(request):
  num1=[]
  num2=[]
  ty=request.POST['val']
  num1 = request.POST.getlist('st')
  num2 = request.POST.getlist('loc')

  if len(num1)==0 or len(num2)==0:
    sensor,location=f1(name)
    return render(request,'sensor-selection.html',{'sensor':sensor,'location':location,'user_name':name,'message_sp':"<font color='RED'>PLEASE SELECT THE VALUES </font>"})

  # Get user's tenant_id from user_list table
  tenant_query = "SELECT tenant_id FROM user_list WHERE email_id = %s"
  cursor.execute(tenant_query, (name,))
  tenant_result = cursor.fetchone()
  tenant_id = tenant_result[0] if tenant_result else None

  # Get user's allowed node_ids based on u_status table (location-based access control)
  allowed_nodes_query = """
    SELECT DISTINCT node.node_id FROM node
    INNER JOIN u_status ON node.location = u_status.location
    WHERE u_status.email_id = %s
  """
  if tenant_id:
    allowed_nodes_query += " AND node.tenant_id = %s"
    cursor.execute(allowed_nodes_query, (name, tenant_id))
  else:
    cursor.execute(allowed_nodes_query, (name,))
  allowed_nodes_result = cursor.fetchall()
  allowed_node_ids = [row[0] for row in allowed_nodes_result]

  # If user selected 'all' locations, use all their allowed nodes
  if 'all' in num2:
    node_id = allowed_node_ids
  else:
    # Filter selected nodes to only include those the user has access to
    node_id = [n for n in num2 if n in allowed_node_ids]

  # If no valid nodes after filtering, show error
  if len(node_id) == 0:
    sensor,location=f1(name)
    return render(request,'sensor-selection.html',{'sensor':sensor,'location':location,'user_name':name,'message_sp':"<font color='RED'>NO VALID LOCATIONS SELECTED </font>"})

  # Build query for sensors filtered by tenant_id and allowed node_ids
  query = "SELECT DISTINCT sensor_id FROM sensor_info WHERE "
  conditions = []
  params = []

  # Filter by tenant_id
  if tenant_id:
    conditions.append("tenant_id = %s")
    params.append(tenant_id)

  # Filter by sensor type if not 'all'
  if len(num1) != 0 and 'all' not in num1:
    type_placeholders = ','.join(['%s'] * len(num1))
    conditions.append("sensor_type IN (" + type_placeholders + ")")
    params.extend(num1)

  # Filter by allowed node_ids
  if len(node_id) != 0:
    node_placeholders = ','.join(['%s'] * len(node_id))
    conditions.append("node_id IN (" + node_placeholders + ")")
    params.extend(node_id)

  query += " AND ".join(conditions)
  cursor.execute(query, params)
  node_records = cursor.fetchall()

  sensor_id=[]
  for row in node_records:
    for col in row:
      sensor_id.append(col)

  sensor_id_list=""
  count=1
  for row in sensor_id:
    sensor_id_list=sensor_id_list+"<li class='list-group-item rounded-0'><div class='custom-control custom-checkbox'>"
    sensor_id_list=sensor_id_list+"<input class='custom-control-input' id='"+row+"' name='sensor_list_id' type='checkbox' value='"+row+"'>"
    sensor_id_list=sensor_id_list+"<label class='cursor-pointer font-italic d-block custom-control-label' for='"+row+"'>"+row.upper()+"</label></div></li>"
  if ty=="app":
    return render(request,'inter.html',{'sensor_id':sensor_id_list,'hidden_value':'app'})

  return render(request,'sensor-data-selection.html',{
    'sensor_id':sensor_id_list,
    'hidden_value':'browser',
    'user_name': name if name else 'User'
  })


def index(request):
  # Landing page - check if user is logged in
  global check, name
  context = {'user_name': name if check == "credit" else None}
  return render(request,'index.html', context)

def login_form(request):
  return render(request,'login.html')

def register_form(request):
  return render(request,'register.html')




count_app=100

name=''
def login_page(request):
  global count_app
  global name
  global check

  # Handle GET request - show login form
  if request.method != 'POST':
    return render(request, 'regis.html')

  # Handle POST request - process login
  print(type(request.POST))
  name=request.POST['t11']
  print(name)
  password=request.POST['t12']
  print(password)
  status=request.POST['web']
  if request.POST.__contains__('count_app'):
   count_app=request.POST['count_app']

  query="select uname,email_id,user_type from user_list where(email_id='"+name+"' and upassword='"+password+"' and status='accepted')"
  try:
    cursor.execute(query)
    result=cursor.fetchall()
    print(len(result))
    if len(result) != 0:
      check="credit"
      if status == "app":
        sensor,location=f1(name)
        print("count_app",count_app)
        if count_app == "0":
          print("YESrt")
          count_app=10
          print(result[0][0]+"#"+result[0][1]+"#"+sensor+"#"+location)
          return HttpResponse(result[0][0]+"#"+result[0][1]+"#"+sensor+"#"+location);

        else:
          return redirect('home')
      else:
        # Redirect to home page (PRG pattern) instead of calling home() directly
        return redirect('home')
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


@no_cache
def home(request,web=None,amessage=''):
  try:
    global check
    # Determine if request is from app or web browser
    # If web parameter not provided, check if it's a GET request (browser redirect)
    if web is None:
      web = "web" if request.method == "GET" else "app"
    print('in home',web)
    if check != "credit":
      # If not logged in, redirect to login page
      return redirect('signin')
    else:
       sensor,location=f1(name)
       print('i have come here ')
       print(sensor,location)
       if web=="app":
         print('last check')
         return render(request,'check.html',{'sensor':sensor,'location':location})
       else:
        print('new DATA',amessage)
        return render(request,'sensor-selection.html',{
          'sensor':sensor,
          'location':location,
          'user_name': name if name else 'User',
          'admin_message':amessage
        })
  except Exception as e:
    print('I AM IN EXCEPT',e)
    if web=="app":
      return HttpResponse("YOU ARE NOT A VALID USER..");
    else:
       return render(request,'login',{'message':"YOU ARE NOT A VALID USER......."})

def dateFix(date):
    if len(date) == 0:
      x = datetime.now()
      date = str(x)[0:10]
      print(date)
      return date
    else:
      return date


def dateFormat(request, date, x):
  from_hr = request.POST['from_hr']
  from_min = request.POST['from_min']
  to_hr = request.POST['to_hr']
  to_min = request.POST['to_min']
  if x=='f':
    format = str(date) + ' ' + from_hr + ':' + from_min + ':00'
  else:
    format = str(date) + ' ' + to_hr + ':' + to_min + ':00'
  print(date)
  return format


def queryExec(query):
  # print(query)
  cursor.execute(query)
  result = cursor.fetchall()
  return result


def preQuery(sensor_id):
  pre_query = "select distinct(sensor_type),sensor_id from sensor_info where "
  pre_query = pre_query + prepareQuery('sensor_id', sensor_id)
  node_records_pre = queryExec(pre_query)
  return node_records_pre


def prepQuery(charttype, sensor_id, to_format, from_format):
  if charttype == 'bar':
    query = "select sensor_data.sensor_id,avg(sensor_value),sensor_type from sensor_data,sensor_info where "
    if len(sensor_id) != 0:
      query = query + prepareQuery('sensor_data.sensor_id', sensor_id)
      query = query + ' and '
      query += "receive_time <= (to_timestamp('" + to_format + "','yyyy-mm-dd hh24:mi:ss')) and receive_time >= (to_timestamp('" + from_format + "', 'yyyy-mm-dd hh24:mi:ss'))"
      query = query + 'and sensor_data.sensor_id=sensor_info.sensor_id group by sensor_type,sensor_data.sensor_id order by sensor_type'
      return query
  else:
    print('Timeseries')

    query = "select sensor_data.sensor_id,sensor_value,RECEIVE_TIME,sensor_type from sensor_data,sensor_info  where sensor_data.sensor_id=sensor_info.sensor_id and "
    query_second = "select sensor_id,sensor_value,DATE_TRUNC('second',receive_time ) from sensor_data where (sensor_id,sensor_value) in ( select sensor_id  ,max(sensor_value) from sensor_data where "

    query = query + prepareQuery('sensor_data.sensor_id', sensor_id)
    query_second = query_second + prepareQuery('sensor_id', sensor_id)

    query = query + ' and '
    query_second = query_second + ' and '

    query += "receive_time < (to_timestamp('" + to_format + "','yyyy-mm-dd hh24:mi:ss')) and receive_time > (to_timestamp('" + from_format + "', 'yyyy-mm-dd hh24:mi:ss'))"
    query_second += "receive_time < (to_timestamp('" + to_format + "','yyyy-mm-dd hh24:mi:ss')) and receive_time > (to_timestamp('" + from_format + "', 'yyyy-mm-dd hh24:mi:ss'))"

    query = query + ' order by sensor_data.sensor_id,receive_time'
    query_second += 'group by sensor_id)'

    return query


dbtitle = ['voltage', 'pressure', 'roll', 'pitch', 'moisture']
ch_ytitle = ['Voltage (V)', 'Pressure (kPa)', 'Displacement (deg)', 'Displacement (deg)', 'Moisture (%)']


def ySet(x, li1, li2):
  for i in range(5):
    if x == li1[i]:
      x = li2[i]
  return x


def setData(records):
  data = []
  for row in records:
    data.append(row)
  return data


def sensorDict(data):
  Dict = {}
  Dict["sensorid"] = unique([row[0] for row in data])
  Dict["sensorid"].sort()
  Dict["sensorval"] = [row[1] for row in data]
  Dict["datelist"] = [row[2] for row in data]
  Dict["sensortype"] = unique([row[3] for row in data])
  return Dict


def getPre(records):
  ty = [row[0] for row in records]
  set_ty = set(ty)
  set_ty = list(ty)
  set_ty = sorted(ty)
  return set_ty


def tempData(table, sensor_id, row):
  flag = False
  y_temp = []
  for col in range(0, len(table)):
    if table[col][0] == sensor_id:
      countd = col
      #print(sensor_id, row)
      if table[col][3]=='pressure':
      #if sensor_id[row] == 'nt_n4_pr1' or sensor_id[row] == 'nt_n4_pr1_f' or sensor_id[row] == 'nt_n4_pr1_r' or \
              #sensor_id[row] == 'nt_n2_pr1_r' or sensor_id[row] == 'ng_n1_pr1':
        #change = ((float(table[countd][1]) / 1000 - 0.2) / 4.5) * 100
        change = (float(table[countd][1]))
        y_temp.append([table[countd][3], change, table[countd][2]])
        continue
     
      if table[col][3]=='moisture':
      #if sensor_id[row] == 'nt_n1_ms1' or sensor_id[row] == 'nt_n3_ms1' or sensor_id[row] == 'nt_n1_ms1_f':
        change = (73 - float(table[countd][1]))
        y_temp.append([table[countd][3], change, table[countd][2]])
        continue

      y_temp.append([table[countd][3], table[countd][1], table[countd][2]])

  return y_temp





def qThree(sensor_id):
  query = "select sensor_id, remark from sensor_info where "
  query = query + prepareQuery('sensor_id', sensor_id)
  return query


def labelDict(sensor_id):
  Dict = {}
  query = qThree(sensor_id)
  remark_Record = queryExec(query)
  for d in remark_Record:
    Dict[d[0]] = d[1]
  return Dict


def getPlotValues(data, pre, dic):
  for aa in data:
    if aa[0] == pre[0]:
      dic['oy'].append(aa[1])
      dic['ox'].append(aa[2])
    if len(pre) >= 2 and aa[0] == pre[1] and aa[0] != pre[0]:
      dic['ty'].append(aa[1])
      dic['tx'].append(aa[2])
    if len(pre) >= 3 and aa[0] == pre[2] and aa[0] != pre[0]:
      dic['thy'].append(aa[1])
      dic['thx'].append(aa[2])
  return dic


def get_graph(plot):
  buffer = BytesIO()
  plot.savefig('login/testplot.png')
  plot.savefig(buffer, format='png')
  buffer.seek(0)
  image_png = buffer.getvalue()
  graph = base64.b64encode(image_png)
  graph = graph.decode('utf-8')
  buffer.close()
  return graph


def firstPart(request):
  try:
    
    sensor_id = request.POST.getlist('sensor_list_id')
    from_date = request.POST['from_date']
    chart_type = request.POST['chart_type']
    to_date = request.POST['to_date']
    from_date = dateFix(from_date)
    from_format = dateFormat(request, from_date, 'f')
    to_date = dateFix(to_date)
    to_Format = dateFormat(request, to_date, 't')
    query = prepQuery(chart_type, sensor_id, to_Format, from_format)
    return query
  except:
    return None




@no_cache
def secondPartNew(request):
  Dict = {}
  Labels = {}
  plt.switch_backend('AGG')
  q = firstPart(request)
  node_records = queryExec(q)
  data = setData(node_records)
  sensor_id = request.POST.getlist('sensor_list_id')
  duration = request.POST['duration']
  query_type=request.POST.get('query_type',None)
  Labels.update(labelDict(sensor_id))
  Dict.update(sensorDict(data))
  set_ty = getPre(preQuery(sensor_id))
  i = -1
  drawlist={}  
  num_cols = 2
  num_rows=(len(Dict["sensorid"]) +num_cols  - 1)
  # Determine the size of each subplot based on the number of columns and rows
  subplot_width = 8  # Adjust this as needed
  subplot_height = 6  # Adjust this as needed
  # Calculate the total figure size
  fig_width = subplot_width * num_cols
  fig_height = subplot_height * num_rows
  figure, axes = plt.subplots(num_rows, num_cols,figsize=(fig_width, fig_height))
  for row in range(0, len(Dict["sensorid"])):
    i += 1
    fy, fx, sy, sx, ty, tx = ([] for _ in range(6))
    first_chartdic = {}
    first_chartdic['ox'] = fx
    first_chartdic['oy'] = fy
    first_chartdic['tx'] = sx
    first_chartdic['ty'] = sy
    first_chartdic['thx'] = tx
    first_chartdic['thy'] = ty
    Val = {}
    temp_data = tempData(data, Dict["sensorid"][i], row)
    Val.update(getPlotValues(temp_data, set_ty, first_chartdic))
    for aa in temp_data:
      dataset=drawlist.get(Dict["sensorid"][i],{})
      x=dataset.get('x',[])
      y=dataset.get('y',[])
      value=aa[0]
      y.append(aa[1])
      x.append(aa[2])
      drawlist[Dict["sensorid"][i]]={'x':x,'y':y,'value':value}
  keys=list(drawlist.keys())
  counter=0
  if query_type=="0":
    with BytesIO() as b:
      writer = pd.ExcelWriter(b, engine='xlsxwriter')
      for key in keys:
        data=drawlist[key]
        df=pd.DataFrame({'Time':data['x'],'values':data['y']})
        df.to_excel(writer, sheet_name=key)
      writer.close()
      filename = 'django_simple.xlsx'
      response = HttpResponse(
          b.getvalue(),
          content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
      )
      response['Content-Disposition'] = 'attachment; filename=%s' % filename
      return response
  else:
    for key in keys:
      rows = counter // num_cols
      cols = counter % num_cols
      ax = axes[rows, cols]
      counter=counter+1
      data=drawlist[key]
      formatter = mdates.DateFormatter("%d-%m-%y ")
      locator = mdates.HourLocator(interval=int(duration))
      
      ax.plot(data['x'],data['y'])
      ax.xaxis.set_major_formatter(formatter)
      ax.xaxis.set_major_locator(locator)
      ax.set_xlabel('Time')
      
      try:
        final_label=data['value']+"  ("+key+") "
        ax.set_ylabel(ySet(final_label,key,key))
      except:
        pass
      
    try: 
      for i in range(len(Dict["sensorid"]), num_rows * num_cols):
        row = i // num_cols
        col = i % num_cols
        figure.delaxes(axes[row, col])
    except:
      pass
    plt.tight_layout()
    chart = get_graph(figure)
    from datetime import datetime
    now = datetime.now()
    return render(request, 'data-visualization.html', {
      'chart': chart,
      'current_date': now.strftime('%B %d, %Y'),
      'current_time': now.strftime('%I:%M %p')
    })
  

        



      
  

def secondPart(request):

  Dict = {}
  Labels = {}
  plt.switch_backend('AGG')
  fig, ax = plt.subplots(figsize=(10,6))
  fig.subplots_adjust(right=0.75)

  flag=False
  flag1=False
  ab = True

  q = firstPart(request)
  node_records = queryExec(q)

  data = setData(node_records)
  sensor_id = request.POST.getlist('sensor_list_id')
  duration = request.POST['duration']

  Labels.update(labelDict(sensor_id))
  Dict.update(sensorDict(data))
  set_ty = getPre(preQuery(sensor_id))

  color_line = ['red', 'blue', 'green', 'black']
  markers = ['<', 'o', 'v', 'x', 'X', 'D', '|', '>', '+', '.', ',']

  i = -1

  # print(Labels)
  # print(data)
  # print(set_ty)

  for row in range(0, len(Dict["sensorid"])):
    # print('help')
    i += 1
    fy, fx, sy, sx, ty, tx = ([] for _ in range(6))
    first_chartdic = {}
    first_chartdic['ox'] = fx
    first_chartdic['oy'] = fy
    first_chartdic['tx'] = sx
    first_chartdic['ty'] = sy
    first_chartdic['thx'] = tx
    first_chartdic['thy'] = ty
    Val = {}
    # print('hello')
    temp_data = tempData(data, Dict["sensorid"][i], row)

    
    

    Val.update(getPlotValues(temp_data, set_ty, first_chartdic))

    for aa in temp_data:
      
      if aa[0] == set_ty[0]:
        fy.append(aa[1])
        fx.append(aa[2])
        flag = False

      if len(set_ty) >= 2 and aa[0] == set_ty[1]:
        sy.append(aa[1])
        sx.append(aa[2])
        flag = True
        flag1 = False

      if len(set_ty) >= 3 and aa[0] == set_ty[2]:  # only 3
        ty.append(aa[1])
        tx.append(aa[2])
        flag = True
        flag1 = True

    label = Labels[Dict["sensorid"][row]]
    # print('hekkio')
    # print(flag)
    formatter = mdates.DateFormatter("%d-%m-%y")
    ax.xaxis.set_major_formatter(formatter)
    locator = mdates.HourLocator(interval=int(duration))
    ax.xaxis.set_major_locator(locator)
    color_line = ['red', 'blue', 'green', 'black']
    p1, = ax.plot(fx, fy, label=label, color=color_line[i % 10], linewidth=.5, marker=markers[i % 6], markersize=.1)
    ax.set_xlabel('Time')
    ax.set_ylabel(ySet(set_ty[0],dbtitle,ch_ytitle))

    # print(set_ty)

    if len(set_ty) >= 2 and flag and ab:
      ax2 = ax.twinx()
      formatter = mdates.DateFormatter("%d-%m-%y ")
      ax2.xaxis.set_major_formatter(formatter)
      locator = mdates.HourLocator(interval=int(duration))
      ax2.xaxis.set_major_locator(locator)
      if len(sx) > 0:
        p2, = ax2.plot(sx, sy, label=label, color=color_line[i % 10], linewidth=.91, marker=markers[(6 - i) % 6],
                   markersize=.11)

        ax2.set_xlabel('Time')
        ax2.set_ylabel(ySet(set_ty[1], dbtitle, ch_ytitle))
      ab = False
      sx = []
      sy = []
      for tick in ax2.get_xticklabels():
        tick.set_rotation(60)
        tick.set_fontsize(10)
    if len(set_ty) >= 2 and flag and flag1:
       ax3 = ax.twinx()
       ax3.spines.right.set_position(("axes", 1.2))
       formatter = mdates.DateFormatter("%d-%m-%y ")
       ax3.xaxis.set_major_formatter(formatter)
       locator = mdates.HourLocator(interval=int(duration))
       ax3.xaxis.set_major_locator(locator)
       p3, =ax3.plot(tx, ty, label=label, color=color_line[i % 10], linewidth=.3, marker=markers[(6 - i) % 6],
                markersize=.1)

       ax3.set_xlabel('Time')
       ax3.set_ylabel(ySet(set_ty[2], dbtitle, ch_ytitle))
  if len(set_ty)<2:
    ax.legend(handles=[p1], loc='upper right')
  elif len(set_ty)<3 and len(set_ty)>2:
    ax.legend(handles=[p1, p2], loc='upper right')
  else:
    ax.legend(handles=[p1, p2, p3], loc='upper right')

  chart = get_graph(fig)
  if len(set_ty) == 1:
    with open('data.csv','w+',newline='') as file:
      writer = csv.writer(file)
      writer.writerows(data)
  else:
    csv_file = open('data.csv','w+')
    csv_file.close()
  return render(request, 'results.html', {'chart': chart})
  
def download(request):
  filename = "data.csv"
  filepath = "data.csv"
  csv_file = open("data.csv", 'rb')
  mime_type, _ = mimetypes.guess_type(filepath)
  response = HttpResponse(csv_file, content_type = mime_type)
  response['Content-Disposition'] = "attachment; filename = %s" %filename
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


# New view functions for additional pages
def about(request):
    """Render the About Us page"""
    # Check if user is logged in by checking the global check variable
    global check, name
    context = {'user_name': name if check == "credit" else None}
    return render(request, 'about.html', context)

def mission(request):
    """Render the Mission page"""
    # Check if user is logged in by checking the global check variable
    global check, name
    context = {'user_name': name if check == "credit" else None}
    return render(request, 'mission.html', context)

def contact(request):
    """Render the Contact page"""
    # Check if user is logged in by checking the global check variable
    global check, name
    context = {'user_name': name if check == "credit" else None}
    return render(request, 'contact.html', context)

def coming_soon(request):
    """Render the Coming Soon page"""
    # Check if user is logged in by checking the global check variable
    global check, name
    context = {'user_name': name if check == "credit" else None}
    return render(request, 'coming-soon.html', context)

