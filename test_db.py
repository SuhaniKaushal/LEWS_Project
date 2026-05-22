import psycopg2
try:
    conn = psycopg2.connect(user='postgres',password='Root@1234A',host='127.0.0.1',port='5432',database='netala_database')
    cur = conn.cursor()
    cur.execute('select distinct(sensor_type) from sensor_info')
    print('Sensors:', [x[0] for x in cur.fetchall()])
    cur.execute("select node_id, location, name from node where location='kerela'")
    print('Kerala Nodes:', cur.fetchall())
    conn.close()
except Exception as e:
    print("Database error:", e)

