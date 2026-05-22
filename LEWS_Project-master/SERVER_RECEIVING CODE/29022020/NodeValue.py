# This is the latest code till 28/02/2020
from Sensorinformation import Sensorinformation
import os
import sys
import psycopg2
from datetime import datetime
import random
import threading
import Send

DB_USER = "postgres"
DB_PASSWORD = "Root@1234A"
DB_HOST = "127.0.0.1"
DB_PORT = "5432"
DB_NAME = "netala_database"

# Thread lock for database access since Net.py now processes data in worker threads
_db_lock = threading.Lock()
# Thread lock for print calls to prevent interleaved/garbled output across threads
_print_lock = threading.Lock()


def _log(msg):
  """Thread-safe log for NodeValue."""
  with _print_lock:
    print('[%s] %s' % (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), msg), flush=True)


def _open_database():
  try:
    connection = psycopg2.connect(user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT, database=DB_NAME)
    cursor = connection.cursor()
    return connection, cursor
  except Exception as e:
    _log("[ERROR] DB connection failed: %s" % e)
    return None, None


class ContentFromClient:
  a = 20
  connection, cursor = _open_database()

  def __init__(self, content, receive_time=None):
    self.content = content.lower()
    self.receive_time = receive_time or datetime.now()

  @staticmethod
  def _ensure_db():
    """Reconnect to database if the connection is closed or broken."""
    try:
      if ContentFromClient.connection is None or ContentFromClient.connection.closed:
        ContentFromClient.connection, ContentFromClient.cursor = _open_database()
        return
      # Test if connection is still alive
      ContentFromClient.cursor.execute("SELECT 1")
      ContentFromClient.cursor.fetchone()
    except Exception:
      try:
        ContentFromClient.connection.close()
      except Exception:
        pass
      ContentFromClient.connection, ContentFromClient.cursor = _open_database()

  def get_node_id(self, cname, name, tenantId):
    try:
      query = "SELECT node_id FROM node WHERE name=%s AND location=%s AND tenant_id=%s"
      cursor = ContentFromClient.cursor
      cursor.execute(query, (name, cname, tenantId))
      node_records = cursor.fetchall()
      node_id = node_records[0][0]
      return node_id
    except Exception as e:
      _log("[ERROR] Node ID lookup failed: %s" % e)
      return None

  def getTotalNodes():
    for i in content:
      pass

  def getTenantId(self):
    return "2"

  def getlocationName(self):
    indexofname = self.content.find('@')
    name = self.content[0:indexofname]
    self.content = self.content[indexofname + 1:]
    return name

  def getCordinatorName(self):
    indexofname = self.content.find('@')
    name = self.content[0:indexofname]
    self.content = self.content[indexofname + 1:]
    return name

  def getNodeName(self):
    indexofname = self.content.find('(')
    name = self.content[0:indexofname]
    self.content = self.content[indexofname:]
    return name

  def sensorvalues(self):
    all1 = []
    tenantId = self.getTenantId()

    temp = self.getlocationName()
    coordinator_name = self.getCordinatorName()
    node_name = self.getNodeName()
    _log('[PROCESS] %s > %s | tenant=%s | pi_time=%s' % (coordinator_name, node_name, tenantId, self.receive_time))

    with _db_lock:
      ContentFromClient._ensure_db()

      node_id = self.get_node_id(coordinator_name, node_name, tenantId)
      if node_id is None:
        _log('[SKIP] Unknown node: %s @ %s' % (node_name, coordinator_name))
        return

      # Collect all inserts, then commit once at the end
      records_to_insert = []

      index = self.content.find(')', 1)
      value = ''
      while index != -1:
        id = ''
        temp = self.content[1:index]

        if temp.startswith('pressure'):
          indexofcolon = self.content.find(':')
          name = self.content[1:indexofcolon]
          value = self.content[indexofcolon + 1:index]
          self.content = self.content[index + 1:]
          s = Sensorinformation(name, value, 'presure', coordinator_name)
          id = node_id + '_' + 'pr' + name[len(name) - 1]
          if float(value) >= 20000:
            threading.Thread(target=Send.send_msg, args=('lews.sailab@gmail.com', 'rjvkmr80@gmail.com', 'Presure VALUE IS CROSSING THRESOLD ' + value), daemon=True).start()

        if temp.startswith('moisture'):
          indexofcolon = self.content.find(':')
          name = self.content[1:indexofcolon]
          value = self.content[indexofcolon + 1:index]
          self.content = self.content[index + 1:]
          s = Sensorinformation(name, value, 'moisture', coordinator_name)
          id = node_id + '_' + 'ms1'
          if float(value) >= 50000:
            threading.Thread(target=Send.send_msg, args=('lews.sailab@gmail.com', 'rjvkmr80@gmail.com', 'MOISTURE VALUE IS CROSSING THRESOLD ' + value), daemon=True).start()

        if temp.startswith('roll'):
          indexofcolon = self.content.find(':')
          name = self.content[1:indexofcolon]
          value = self.content[indexofcolon + 1:index]
          self.content = self.content[index + 1:]
          s = Sensorinformation(name, value, 'roll', coordinator_name)
          id = node_id + '_' + 'ro' + name[len(name) - 1]
          if float(value) >= 20000:
            threading.Thread(target=Send.send_msg, args=('lews.sailab@gmail.com', 'rjvkmr80@gmail.com', 'Roll VALUE IS CROSSING THRESOLD ' + value), daemon=True).start()

        if temp.startswith('voltage'):
          indexofcolon = self.content.find(':')
          name = self.content[1:indexofcolon]
          value = self.content[indexofcolon + 1:index]
          self.content = self.content[index + 1:]
          s = Sensorinformation(name, value, 'voltage', coordinator_name)
          id = node_id + '_' + 'voltage' + name[len(name) - 1]
          if float(value) >= 20000:
            threading.Thread(target=Send.send_msg, args=('lews.sailab@gmail.com', 'rjvkmr80@gmail.com', 'Roll VALUE IS CROSSING THRESOLD ' + value), daemon=True).start()

        if temp.startswith('vols'):
          indexofcolon = self.content.find(':')
          name = self.content[1:indexofcolon]
          value = self.content[indexofcolon + 1:index]
          self.content = self.content[index + 1:]
          s = Sensorinformation(name, value, 'vols', coordinator_name)
          id = node_id + '_' + 'vols' + name[len(name) - 1]
          if float(value) >= 20000:
            threading.Thread(target=Send.send_msg, args=('lews.sailab@gmail.com', 'rjvkmr80@gmail.com', 'Roll VALUE IS CROSSING THRESOLD ' + value), daemon=True).start()

        if temp.startswith('pitch'):
          indexofcolon = self.content.find(':')
          name = self.content[1:indexofcolon]
          value = self.content[indexofcolon + 1:index]
          self.content = self.content[index + 1:]
          s = Sensorinformation(name, value, 'pitch', coordinator_name)
          id = node_id + '_' + 'pi' + name[len(name) - 1]
          if float(value) >= 2000:
            threading.Thread(target=Send.send_msg, args=('lews.sailab@gmail.com', 'rjvkmr80@gmail.com', 'PITCH VALUE IS CROSSING THRESOLD ' + value), daemon=True).start()

        # Use Pi's receive_time (when sensor was actually read) not server time
        if value != "nan" and id is not None and id != '':
          records_to_insert.append((id, value, self.receive_time, tenantId))

        index = self.content.find(')', 1)

      # Single commit for all sensor values in this packet
      if records_to_insert:
        try:
          postgres_insert_query = 'INSERT INTO sensor_data (sensor_id,sensor_value,receive_time,tenant_id) VALUES (%s,%s,%s,%s)'
          for record in records_to_insert:
            ContentFromClient.cursor.execute(postgres_insert_query, record)
          ContentFromClient.connection.commit()
          _log('[DB] Inserted %d records for %s > %s' % (len(records_to_insert), coordinator_name, node_name))
        except Exception as e:
          _log('[ERROR] DB insert failed: %s' % e)
          try:
            ContentFromClient.connection.rollback()
          except Exception:
            pass
          ContentFromClient._ensure_db()


if __name__ == "__main__":
  print('hi')
  # Test with explicit receive_time (simulating Pi timestamp)
  c = ContentFromClient("2@c1@kerala@n1(moisture1:581.02)(pitch10:-75)(roll1:-4)(pitch2:-95)(roll2:-95)(pitch3:-95)(roll3:-95)(pitch4:-95)(roll4:-95)", datetime.now())
  c.sensorvalues()
  print('DONE')
