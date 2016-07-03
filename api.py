from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
import ConfigParser
import json
import os
import sqlite3
import time
import urlparse

DATABASE_NAME = ''
DEVICE_TABLE_NAME = ''
MODULES = []

class CustomHTTPHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        parsed_path = urlparse.urlparse(self.path)
        print 'Request ' + parsed_path.path
        content = ""
        if parsed_path.path == '/':
            print "HTML request started"
            self.send_response(200)
            self.send_header('Content-type','text/html')
            self.end_headers()
            with open('dashboard.html', 'r') as htmlFile:
                data=htmlFile.read()
            content = data
        elif parsed_path.path == '/data':
            print "API request started"
            connection = sqlite3.connect(DATABASE_NAME)
            cursor = connection.cursor()
            devices = [] 
            print "Devices found:"
            for row in cursor.execute ("SELECT * FROM " + DEVICE_TABLE_NAME):
                device = {}
                device['table_name'] = row[1]
                device['device_name'] = row [0]
                device['last_discovered'] = row[2]
                devices.append(device)
                print device

            timestamp = time.time() - (60 * 60 * 24)
            for device in devices:
                print "Retrieving data for " + device['device_name']
                data_array = []
                table_name = device['table_name']
                for row in cursor.execute ("SELECT * FROM " + table_name + " WHERE date>=? and device_name=? ORDER BY date DESC", (timestamp,device['device_name'])):
                    properties = list(map(lambda x: x[0], cursor.description))
                    data_point = {}
                    for i in range(len(properties)):
                        prop = properties[i]
                        data_point[prop] = row[i]
                    data_array.append(data_point)
                device['data'] = data_array
            content = json.dumps(devices)   
            self.send_response(200)
            self.send_header('Content-type','application/json')
            self.end_headers()
        else: 
            print "Unkown request"
            self.send_response(404)
            self.end_headers()
        print "Request ended"
        self.wfile.write(content)

if __name__ == "__main__":
    config = ConfigParser.RawConfigParser()
    config.read('sensor_station.cfg')

    DATABASE_NAME = config.get('Global', 'database_file_path')
    DEVICE_TABLE_NAME = config.get('Global', 'database_devices_table')
    PORT = config.getint('API', 'port')
    HOST = config.get('API', 'host')
    mods = config.get('Global', 'modules').split(",")

    if not isinstance(mods, list):
        MODULES = [mods]
    else:
        MODULES = mods

    # Create the server, binding to localhost on port 9999
    server = HTTPServer((HOST, PORT), CustomHTTPHandler)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
