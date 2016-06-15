import base64
import datetime
import ssl
import sys
import re
import time
import traceback
import urllib2

from modules import basemodule
from requests.auth import HTTPBasicAuth

class DDWRTStatus(basemodule.SensorModule):
    def __init__(self):
        self.routerip = 'https://192.168.0.1'
        self.username = 'admin'
        self.password = 'password'

    def trigger_device_discovery(self):
        print 'Starting to run discovery job for ' + self.module_name()
        timestamp = time.time()

        data = []
        response = self.make_request()
        if response.code == 200:
            print "Found router"
            data.append(('Router', timestamp))
        print 'Discovery job done'
        print ''
        return data
 

    def trigger_device_check(self):
        print 'Starting to run query job for ' + self.module_name()
        data = [] 
        timestamp = time.time()
        try:
            print "Querying router at " + datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
            up_traffic = 0
            down_traffic = 0
            page = self.make_request().read()
            parsed_data = re.findall(r'\{([^}]*)\}',page)
            data.append(('Router', parsed_data[12], parsed_data[11], timestamp))
            print 'Device data gathered'
            
        except:
            print 'Error connecting to WeMo'
            print '-'*20
            traceback.print_exc(file=sys.stdout)
            print '-'*20
        print 'Query job done'
        print ''
        return data
    
    def make_request(self):
        request = urllib2.Request(self.routerip + '/Status_Internet.live.asp')
        gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1) 
        base64string = base64.encodestring('%s:%s' % (self.username, self.password)).replace('\n', '')
        request.add_header("Authorization", "Basic %s" % base64string)   
        result = urllib2.urlopen(request, context=gcontext)
        return result

    @staticmethod
    def module_name():
        return 'ddwrt_status'
    
    @staticmethod
    def discovery_timer():
        return 600

    @staticmethod
    def check_timer():
        return 300

    @staticmethod
    def data_format():
        return [('device_name', 'text'), ('up_traffic', 'text'), ('down_traffic', 'text'), ('date', 'integer')];

    @staticmethod
    def database_version():
       return 1
