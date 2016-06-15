import ConfigParser
import datetime
import importlib
import sched
import sqlite3
import sys
import threading
import time
import traceback

from modules import *

'''
class SensorModule:
    def __init__(self):
        raise NotImplementedError

    def trigger_device_discovery(self):
        raise NotImplementedError

    def trigger_device_check(self):
        raise NotImplementedError

    @staticmethod
    def module_name():
        raise NotImplementedError

    @staticmethod
    def discovery_timer():
        raise NotImplementedError

    @staticmethod
    def check_timer():
        raise NotImplementedError

    @staticmethod
    def data_format():
        raise NotImplementedError

    @staticmethod
    def database_version():
        raise NotImplementedError
'''

def check_devices(module):
    sem.acquire()
    try:
        connection = sqlite3.connect(DATABASE_NAME)
        cursor = connection.cursor()
        data = module.trigger_device_check()
        module_name = module.__class__.__name__
        for device in data:
            db_format = module.data_format
            db_command = "INSERT INTO " + module_name + " VALUES ("
            for i in range(len(device)):
                db_command += "?"
                if not i == len(device) - 1:
                    db_command += ", "
            db_command += ")"
            print db_command
            cursor.execute(db_command, device)
        connection.commit()
        connection.close()
    except:
        print 'Error triggering discovery for module ' + module.module_name()
        print '-'*20
        traceback.print_exc(file=sys.stdout)
        print '-'*20

    sem.release()
    callback = create_check_devices_callback(module)
    threading.Timer(module.check_timer(), callback).start()

def discover_devices(module):
    sem.acquire()
    try:
        devices = module.trigger_device_discovery()
        connection = sqlite3.connect(DATABASE_NAME)
        cursor = connection.cursor()
        module_name = module.__class__.__name__
        for device in devices:
            print "Found " + device[0]
            cursor.execute("INSERT OR REPLACE INTO devices (device_name, module_name, last_discovered) VALUES (?,?,?)", (device[0], module_name, device[1]))
        connection.commit()
        connection.close()
    except:
        print 'Error triggering discovery for module ' + module.module_name()
        print '-'*20
        traceback.print_exc(file=sys.stdout)
        print '-'*20

    sem.release()
    callback = create_discover_devices_callback(module)
    threading.Timer(module.discovery_timer(), callback).start()

def handle_module(module_name):
    somemodule = importlib.import_module('modules.' + module_name.lower())
    print somemodule
    targetClass = getattr(somemodule, module_name)
    module = targetClass()

    verify_module(module)
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    classname = module_name
    if not table_exists(classname, c):
        db_format = "CREATE TABLE " + classname  + " ("
        db_schema = module.data_format()
        for i in range(len(db_schema)):
            column = db_schema[i]
            db_input = column[0] + " " + column[1]
            db_format += db_input
            if not i == len(db_schema) - 1:
                db_format += ", "
        db_format += ")"
        c.execute(db_format)

    if not table_exists(DATABASE_DEVICES_TABLE, c):
        c.execute('CREATE TABLE ' + DATABASE_DEVICES_TABLE + ' (device_name text PRIMARY KEY, module_name text, last_discovered integer)')
    conn.commit()

    discover_devices(module)
    callback = create_check_devices_callback(module)
    threading.Timer(module.check_timer(), callback).start()

def create_discover_devices_callback(module):
    return lambda : discover_devices(module)

def create_check_devices_callback(module):
    return lambda : check_devices(module)

def table_exists(table_name, cursor):
    for row in cursor.execute ("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,)):
        return True
    return False

def verify_module(module):
    print 'Checking module'
    print 'Name: ' + module.module_name()
    print 'Discovery time interval: ' + str(module.discovery_timer())
    print 'Check time interval: ' + str(module.check_timer())
    print 'Data format: ' + str(module.data_format())
    print 'Databaase version: ' + str(module.database_version())
 

config = ConfigParser.RawConfigParser()
config.read('sensor_station.cfg')

DATABASE_NAME = config.get('Global', 'database_file_path')
DATABASE_DEVICES_TABLE = config.get('Global', 'database_devices_table')
MODULES = config.get('Global', 'modules').split(",")  

scheduler = sched.scheduler(time.time, time.sleep)
sem = threading.Semaphore()

if isinstance(MODULES, list):
    for module in MODULES:
        handle_module(module)
else:
    handle_module(MODULES)
