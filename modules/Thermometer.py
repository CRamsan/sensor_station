import time
import Adafruit_MCP9808.MCP9808 as MCP9808

from modules import basemodule
# Define a function to convert celsius to fahrenheit.
def c_to_f(c):
	return c * 9.0 / 5.0 + 32.0

class Thermometer(basemodule.SensorModule):
    def __init__(self):
        self.sensor = MCP9808.MCP9808()
        self.sensor.begin()
    
    def trigger_device_discovery(self): 
        timestamp = time.time() 
        data = [['Local RaspberryPi Sensor', timestamp]]
        return data
        
    def trigger_device_check(self):
        data = []
        timestamp = time.time()
        temp = self.sensor.readTempC()
        print('Temperature: {0:0.3F}*C / {1:0.3F}*F'.format(temp, c_to_f(temp)))
        data = [("RaspberryPi Sensor", temp, timestamp)]
        return data

    @staticmethod
    def discovery_timer():
        return 60

    @staticmethod
    def check_timer():
        return 60
    
    @staticmethod
    def data_format():
        return [('device_name', 'text'), ('temperature', 'integer'), ('date', 'integer')];
    
    @staticmethod
    def database_version():
        return 0
