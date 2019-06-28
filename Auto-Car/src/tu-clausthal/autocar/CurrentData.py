from ast import literal_eval
from traceback import print_exc
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
            self.sensor_data_list = []  # list of sensor data elements of the Form [[timestamp,position[],euler]]

        def add_sensor_data_to_list(self):
            # adds sensor data from CurrentData to self.sensor_data_list

            sensor_timestamp = CurrentData.get_value_from_tag_from_sensor("timestamp")
            sensor_position = [CurrentData.get_value_from_tag_from_sensor("position")[0],
                               CurrentData.get_value_from_tag_from_sensor("position")[1]]
            sensor_euler = CurrentData.get_value_from_tag_from_sensor("euler")[0]
            self.sensor_data_list.append([sensor_timestamp, sensor_position, sensor_euler])
            if len(self.sensor_data_list) > 20:
                del self.sensor_data_list[0]
            # print(CurrentData.get_value_from_tag_from_sensor("euler")[0])

        def set_lidar_json(self, lidar_json):
            parsed_lidar_data = CurrentData.get_value_from_tag_from_json(lidar_json, "pcl")

            filtered_lidar_data = [data for data in parsed_lidar_data if not (data[0] <= 10)]  # and data[2] < 1920.5
            lidar_json["pcl"] = filtered_lidar_data
            self.__lidar_json = lidar_json

        def get_lidar_json(self):
            return self.__lidar_json

        def set_sensor_json(self, sensor_json):
            parsed_euler_data = CurrentData.get_value_from_tag_from_json(sensor_json, "euler")
            parsed_position_data = CurrentData.get_value_from_tag_from_json(sensor_json, "position")

            for i in range(parsed_position_data):
                if parsed_position_data[i] == -1:
                    parsed_position_data[i] == self.sensor_data_list[len(self.sensor_data_list) -1 ][1][i]

            corrected_euler_data = parsed_euler_data
            corrected_euler_data[0] += 180
            sensor_json["euler"] = corrected_euler_data
            self.__sensor_json = sensor_json
            # print("set_senor_json worked")

            self.add_sensor_data_to_list(CurrentData.get_value_from_tag_from_json(sensor_json, "timestamp"), CurrentData.get_value_from_tag_from_json(sensor_json, "position"), CurrentData.get_value_from_tag_from_json(sensor_json, "euler"))

        def get_sensor_json(self):
            return self.__sensor_json

        def get_observer_methods(self):
            return self.__observer_methods

        def add_observer_method(self, method):
            self.__observer_methods.append(method)

        def remove_observer_method(self, method):
            self.__observer_methods.remove(method)

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
        # print("new data")
        # pos = CurrentData.get_value_from_tag_from_sensor("position")
        # euler = CurrentData.get_value_from_tag_from_sensor("euler")
        # print("Pos: [{}, {}], Euler: {}".format(int(round(pos[0] / 10)), int(round(pos[1] / 10)), euler[0]))
        if CurrentData.instance:
            for method in CurrentData.instance.get_observer_methods():
                # print("method to run: " + str(method))
                try:
                    method(changed_data_str)
                except(Exception) as e:
                    if method is not None:
                        print_exc()
        return

    """
    Used to register a method to get a callback whenever new data is received
    """
    @staticmethod
    def register_method_as_observer(method):
        if CurrentData.instance:
            print("Adding {} as a observer!".format(str(method)))
            CurrentData.instance.add_observer_method(method)

    """
    Used to remove a method as an observer
    """
    @staticmethod
    def remove_method_as_observer(method):
        if CurrentData.instance:
            CurrentData.instance.remove_observer_method(method)

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
    def get_lidar_json():
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
    def get_sensor_json():
        if CurrentData.instance:
            return CurrentData.instance.get_sensor_json()

    """
    Used to get a value form the lidar data which is in json format. You just have to provide it with a
    tag in form of a string.
    """
    @staticmethod
    def get_value_from_tag_from_lidar(tag_str):
        if CurrentData.instance:
            return CurrentData.get_value_from_tag_from_json(CurrentData.get_lidar_json(), tag_str)

    """
    Used to get a value form the sensor data which is in json format. You just have to provide it with a
    tag in form of a string.
    """
    @staticmethod
    def get_value_from_tag_from_sensor(tag_str):
        if CurrentData.instance:
            return CurrentData.get_value_from_tag_from_json(CurrentData.get_sensor_json(), tag_str)

    """
    Helper method to get a value from a given json-tag and given json object.
    You can obtain a json object by calling json.loads(json_as_string) for example.
    """
    @staticmethod
    def get_value_from_tag_from_json(json_obj, tag_str):
        res = None
        for key, value in json_obj.items():
            if key == tag_str:
                if "str" in str(type(value)):
                    res = literal_eval(value)
                else:
                    res = value
                # res = value
                break
        return res
