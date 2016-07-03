import datetime
import time
import traceback
import sys

from modules import basemodule
from ouimeaux.environment import Environment

class WemoInsightSwitch(basemodule.SensorModule):
    def __init__(self):
        self.env = Environment(switch_callback=self.on_switch, motion_callback=self.on_motion, with_cache=False)
        self.env.start()
        self.devices = []

    def trigger_device_discovery(self):
        self.env.discover(seconds=10)
        self.env.list_switches()
        devices_found = self.env.list_switches()
    
        timestamp = time.time()
        data = []
        self.devices = []
        for device_name in devices_found:
            data.append((device_name, timestamp))
            self.devices.append(device_name)
        return data
 

    def trigger_device_check(self):
        devices = self.devices
        data = [] 
        timestamp = time.time()
        for device_name in devices:
            try:
                insight = self.env.get_switch(device_name)
                tkwh = insight.today_kwh
                cp = insight.current_power
                tot =  insight.today_on_time
                of = insight.on_for
                lc = insight.last_change
                tsbt = insight.today_standby_time
                ot = insight.ontotal
                tmw = insight.totalmw
                data.append((device_name, tkwh, cp, tot, of, lc, tsbt, ot, tmw, timestamp))
            except:
                print 'Error connecting to WeMo'
                print '-'*20
                traceback.print_exc(file=sys.stdout)
                print '-'*20
        return data

    @staticmethod
    def discovery_timer():
        return 900

    @staticmethod
    def check_timer():
        return 30

    @staticmethod
    def data_format():
        return [('device_name', 'text'), ('today_kwh', 'integer'), ('current_power', 'integer'), ('today_on_time', 'integer'), ('on_for', 'integer'), ('last_change', ' integer'), ('today_standby_time', 'integer'), ('ontotal', 'integer'), ('totalmw', 'integer'), ('date', 'integer')];

    @staticmethod
    def database_version():
       return 1

    def on_switch(self, switch):
        print "Switch found!", switch.name

    def on_motion(self, motion):
        print "Motion found!", motion.name
