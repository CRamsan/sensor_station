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
    module_name = module.__class__.__name__
    print "Starting device check method for " + module_name
    try:
        connection = sqlite3.connect(DATABASE_NAME)
        cursor = connection.cursor()
        data = module.trigger_device_check()
        if not isinstance(data, list):
            '''Data is not an array, it should be an array containing device states'''
            raise
        for device in data:
            print "Device: " + str(device)
            db_format = module.data_format
            db_command = "INSERT INTO " + module_name + " VALUES ("
            for i in range(len(device)):
                db_command += "?"
                if not i == len(device) - 1:
                    db_command += ", "
            db_command += ")"
            cursor.execute(db_command, device)
        connection.commit()
        connection.close()
    except:
        print 'Error triggering discovery for module ' + module_name
        print '-' * 20
        traceback.print_exc(file=sys.stdout)
        print '-' * 20
 
    print "Device check method for " + module_name + " ended"
    sem.release()
    callback = create_check_devices_callback(module)
    threading.Timer(module.check_timer(), callback).start()

def discover_devices(module):
    sem.acquire()
    module_name = module.__class__.__name__
    print "Starting discovery method for " + module_name
    try:
        devices = module.trigger_device_discovery()
        if not isinstance(devices, list):
            '''module.trigger_device_discovery() returned something that is not a list of devices'''
            raise
        connection = sqlite3.connect(DATABASE_NAME)
        cursor = connection.cursor()
        for device in devices:
            if (len(device) != 2):
                '''Device is a tuple with a size other than 2, a device should be tuple (device_name,timestamp)'''
                raise
            print "Found " + device[0]
            cursor.execute("INSERT OR REPLACE INTO devices (device_name, module_name, last_discovered) VALUES (?,?,?)", (device[0], module_name, device[1]))
        connection.commit()
        connection.close()
    except:
        print 'Error triggering discovery for module ' + module_name
        print '-' * 20
        traceback.print_exc(file=sys.stdout)
        print '-' * 20
    print "Discovery method for " + module_name + " ended"
    sem.release()
    callback = create_discover_devices_callback(module)
    threading.Timer(module.discovery_timer(), callback).start()

def handle_module(module_name):
    sem.acquire()
    print "Starting module " + module_name
    somemodule = importlib.import_module('modules.' + module_name)
    targetClass = getattr(somemodule, module_name)
    module = targetClass()

    verify_module(module)
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    if not table_exists(module_name, c):
        db_format = "CREATE TABLE " + module_name  + " ("
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
    sem.release()
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
    print 'Discovery time interval: ' + str(module.discovery_timer())
    print 'Check time interval: ' + str(module.check_timer())
    print 'Data format: ' + str(module.data_format())
    print 'Database version: ' + str(module.database_version())
 
print "Reading config file"
config = ConfigParser.RawConfigParser()
config.read('sensor_station.cfg')

DATABASE_NAME = config.get('Global', 'database_file_path')
print "DATABASE_NAME = " + DATABASE_NAME
DATABASE_DEVICES_TABLE = config.get('Global', 'database_devices_table')
print "DATABASE_DEVICES_TABLE = " + DATABASE_DEVICES_TABLE
MODULES = config.get('Global', 'modules').split(",")  
print "MODULES = " + str(MODULES);

scheduler = sched.scheduler(time.time, time.sleep)
sem = threading.Semaphore()

if isinstance(MODULES, list):
    for module in MODULES:
        handle_module(module)
else:
    handle_module(MODULES)
