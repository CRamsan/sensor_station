from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
import urlparse
import sqlite3
import time
import json

HOST = ''
PORT = 9999
DATABASE_NAME = 'data.db'
DEVICE_TABLE_NAME = 'devices'
DATA_TABLE_NAME = 'insight'

PROPERTIES = ['device_name', 'today_kwh', 'current_power', 'today_on_time', 'on_for', 'last_change', 'today_standby_time', 'ontotal', 'totalmw', 'date']

class CustomHTTPHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        parsed_path = urlparse.urlparse(self.path)
        print 'Request ' + parsed_path.path
        if not parsed_path.path == '/data':
            return

        self.send_response(200)
        self.send_header('Content-type','application/json')
        self.end_headers()
        content = ""
        connection = sqlite3.connect(DATABASE_NAME)
        cursor = connection.cursor()

        devices = []
        for row in cursor.execute ("SELECT * FROM devices"):
            device = {}
            device['device_name'] = row [0]
            device['last_discovered'] = row[1]
            devices.append(device)

        timestamp = time.time() - (60 * 60 * 24)
        for device in devices:
            data_array = []
            for row in cursor.execute ("SELECT * FROM insight WHERE date>=? and device_name=?", (timestamp,device['device_name'])):
                data_point = {}
                for i in range(len(PROPERTIES)):
                    prop = PROPERTIES[i]
                    data_point[prop] = row[i]
                data_array.append(data_point)
            device['data'] = data_array
        content = json.dumps(devices)    
        self.wfile.write(content)

if __name__ == "__main__":

    # Create the server, binding to localhost on port 9999
    server = HTTPServer((HOST, PORT), CustomHTTPHandler)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
