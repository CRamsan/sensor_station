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
