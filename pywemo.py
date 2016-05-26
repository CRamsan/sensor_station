import sys,traceback
import threading
import datetime
import sqlite3
import time
from ouimeaux.environment import Environment

DATABASE_NAME = 'data.db'
DEVICE_TABLE_NAME = 'devices'
DATA_TABLE_NAME = 'insight'
TIMER_QUERY = 30
TIMER_DISCOVERY = 600
DISCOVERY_TIME = 15
sem = threading.Semaphore()

def on_switch(switch):
    print "Switch found!", switch.name

def on_motion(motion):
    print "Motion found!", motion.name

def check_devices():
    sem.acquire()
    print 'Starting to run query job';
    timer = threading.Timer(TIMER_QUERY, check_devices)
    timer.start()
    devices = env.list_switches()
    
    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()
    timestamp = time.time()
    for device_name in devices:
        print "Querying " + device_name + " at " + datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
        try:
            insight = env.get_switch(device_name)
            tkwh = insight.today_kwh
            cp = insight.current_power
            tot =  insight.today_on_time
            of = insight.on_for
            lc = insight.last_change
            tsbt = insight.today_standby_time
            ot = insight.ontotal
            tmw = insight.totalmw
            cursor.execute("INSERT INTO insight VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (device_name, tkwh, cp, tot, of, lc, tsbt, ot, tmw, timestamp))
            print 'Device data gathered'
        except:
            print 'Error connecting to WeMo'
            print '-'*60
            traceback.print_exc(file=sys.stdout)
            print '-'*60
    connection.commit()
    connection.close()
    print 'Query job done'
    print ''
    sem.release()

def discover_devices():
    sem.acquire()
    print 'Starting to run discovery job';
    env.discover(seconds=10)
    env.list_switches()
    
    timer = threading.Timer(TIMER_DISCOVERY, discover_devices)
    timer.start()
    devices = env.list_switches()
    
    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()
    timestamp = time.time()
    for device_name in devices:
        print "Found " + device_name
        cursor.execute("INSERT OR REPLACE INTO devices (device_name, last_discovered) VALUES (?,?)", (device_name, timestamp))
    connection.commit()
    connection.close()
    print 'Discovery job done'
    print ''
    sem.release()

def verify_table_exists(table_name, cursor):
    tableExist = False
    print table_name
    for row in cursor.execute ("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,)):
        tableExist = True
    return tableExist

conn = sqlite3.connect(DATABASE_NAME)
c = conn.cursor()
if not verify_table_exists(DATA_TABLE_NAME, c):
    c.execute("CREATE TABLE insight (device_name text, today_kwh integer, current_power integer, today_on_time integer, on_for integer, last_change integer, today_standby_time integer, ontotal integer, totalmw integer, date integer)")
if not verify_table_exists(DEVICE_TABLE_NAME, c):
    c.execute("CREATE TABLE devices (device_name text PRIMARY KEY, last_discovered integer)")
conn.commit()
conn.close()

env = Environment(switch_callback=on_switch, motion_callback=on_motion, with_cache=False)
env.start()
discover_devices()
initial_timer = threading.Timer(DISCOVERY_TIME, check_devices)
initial_timer.start()
