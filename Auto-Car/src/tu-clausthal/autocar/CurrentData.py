import ast


"""
Class CurrentData
This class is a singleton and is used to give access to the current dataset from the car.
To use it you can call the static methods "get_value_from_tag_from_lidar(tag_str)" and 
    "get_value_from_tag_from_sensor(tag_str)" to get the data you need.
You can also call "register_method_as_observer(method)" to register the given method for a callback whenever
    new data is received. The callback method gets just one Parameter, which is a string. This string is either
    "lidar" or "sensor" depending on which data was updated.

"""


class CurrentData:

    """
    Private inner class of CurrentData, used to implement the singleton behaviour in python.
    It is stored in a static variable in the outer class.
    """

    class __CurrentData:

        def __init__(self):
            self.__lidar_json = None
            self.__sensor_json = None
            self.__observer_methods = []

        def set_lidar_json(self, lidar_json):
            self.__lidar_json = lidar_json

        def get_lidar_json(self):
            return self.__lidar_json

        def set_sensor_json(self, sensor_json):
            self.__sensor_json = sensor_json

        def get_sensor_json(self):
            return self.__sensor_json

        def get_observer_methods(self):
            return self.__observer_methods

        def add_observer_method(self, method):
            self.__observer_methods.append(method)

    """
    Static variable (no "self." before it) used to store the only instance of the inner class "__CurrentData"
    """
    instance = None

    """
    Constructor of CurrentData which ensures, that there is only one instance of __CurrentData
    """
    def __init__(self):
        if not CurrentData.instance:
            CurrentData.instance = CurrentData.__CurrentData()
        return

    """
    Called whenever either new lidar or sensor data is passed via
        "set_lidar_json" or "set_sensor_json" by MqttConnection.
    It then calls every registered method.
    """
    @staticmethod
    def __on_data_change(changed_data_str):
        if CurrentData.instance:
            for method in CurrentData.instance.get_observer_methods():
                #print("method to run: " + str(method))
                method(changed_data_str)
        return

    """
    Used to register a method to get a callback whenever new data is received
    """
    @staticmethod
    def register_method_as_observer(method):
        if CurrentData.instance:
            CurrentData.instance.add_observer_method(method)

    """
    Not for usual use. Only called by MqttConnection when new data arrives.
    It sets the data and triggers the callback
    """
    @staticmethod
    def set_lidar_json(lidar_json):
        if CurrentData.instance:
            CurrentData.instance.set_lidar_json(lidar_json)
            CurrentData.__on_data_change("lidar")

    """
    Internal method to get the lidar json from the instance
    """
    @staticmethod
    def __get_lidar_json():
        if CurrentData.instance:
            return CurrentData.instance.get_lidar_json()

    """
    Not for usual use. Only called by MqttConnection when new data arrives.
    It sets the data and triggers the callback
    """
    @staticmethod
    def set_sensor_json(sensor_json):
        if CurrentData.instance:
            CurrentData.instance.set_sensor_json(sensor_json)
            CurrentData.__on_data_change("sensor")

    """
    Internal method to get the sensor json from the instance
    """
    @staticmethod
    def __get_sensor_json():
        if CurrentData.instance:
            return CurrentData.instance.get_sensor_json()

    """
    Used to get a value form the lidar data which is in json format. You just have to provide it with a
    tag in form of a string.
    """
    @staticmethod
    def get_value_from_tag_from_lidar(tag_str):
        if CurrentData.instance:
            return CurrentData.get_value_from_tag_from_json(CurrentData.__get_lidar_json(), tag_str)

    """
    Used to get a value form the sensor data which is in json format. You just have to provide it with a
    tag in form of a string.
    """
    @staticmethod
    def get_value_from_tag_from_sensor(tag_str):
        if CurrentData.instance:
            return CurrentData.get_value_from_tag_from_json(CurrentData.__get_sensor_json(), tag_str)

    """
    Helper method to get a value from a given json-tag and given json object.
    You can obtain a json object by calling json.loads(json_as_string) for example.
    """
    @staticmethod
    def get_value_from_tag_from_json(json_obj, tag_str):
        res = None
        for key, value in json_obj.items():
            if key == tag_str:
                res = ast.literal_eval(str(value))
                break
        return res