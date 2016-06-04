#Sensor Station

Sensor Station is a set of Python scripts that enables you easily to gather data periodically from multiple sources.The core of Sensor Station is the server and it's capability to load modules. Each module encapsulates the logic to retrieve information, currently there are modules for getting data from the WeMo Insight and the DD-WRT router.

Running the server
-------------------

You will need to have Python 2.7, this has only been tested on a raspberry pi running raspbian.

To run the server you can do:

`
python server.py
` 

If you want to run the server on a separate terminal you can use `screen` to create a new terminal and then you can use `CTRL+A, D` to detach from that terminal.

The server will gather data based on the enabled modules and then store it in a local SQLite database. If you want to enable the API you can run the command

`
python api.py
`

The API script will enable the JSON endpoint for the data as well as a dashboard written in HTML that shows the latest 24 hours of the data for the enabled modules. When using the default settings you can go to `IP-ADDRESS:9999` for displaying the HTML dashboard and `IP-ADDRESS:9999/data`  

You can change a few a few settings in the sensor_station.cfg file.

Design
-------

Sensor station works by loading Python modules that inherit from the BaseModule. The modules can implement more methods as long as the base methods have been overwritten.

`trigger_device_discovery(self)` 

This method allows  the server to check if the device is actually online. This method returns an array with the devices that are online.

`trigger_device_check(self)`

This method will be called by the server to poll the devices and retrieve information. Here is where you would usually define your code to access and parse the data. This method returns an array with a tuple containing all the information retrieved. The tuple should have the same format that is defined in the  `data_format()` method.

`module_name()`

Return a string that is the name of module. This is used by the server as a table name in the database. 

`discovery_timer()`

Return an integer that defines how often should the server poll the devices.

`check_timer()`

Return an integer that defines how often should the server check which devices are still online.

`data_format()`

Return an array with 2-tuple that define the format on which the data will be returned. The first element in the tuple is a column name and the second element is a SQLite data primitive, the most commonly used are `integer` and `string`.
