"""
Hallo
"""
import json
import ast
import zones


class Logic:

    def __init__(self, mqtt_connection):
        self.mqtt_connection = mqtt_connection
        self.mqtt_connection.set_callback_methods(on_message=self.on_mqtt_message)
        self.lidar_json = None
        self.sensor_json = None
        self.__manual_control = False
        self.__stop = False
        self.__current_speed = 90
        self.__current_speed_slider = 90
        self.__current_steer = 90
        self.__current_steer_slider = 90
        return

    def set_stop(self, stop=True):
        self.__stop = stop
        if self.__stop:
            self.send_stop()
        return

    def get_stop(self):
        return self.__stop

    def send_stop(self):
        self.mqtt_connection.send_car_command(90, 90)
        return

    def set_manual_control(self, mc=True):
        self.__manual_control = mc
        return

    def get_manual_control(self):
        return self.__manual_control

    def set_speed_slider(self, val):
        self.__current_speed_slider = val
        if ~self.__stop and self.__manual_control:
            self.send_command_manual()

    def set_steer_slider(self, val):
        self.__current_steer_slider = val
        if ~self.__stop and self.__manual_control:
            self.send_command_manual()

    def on_mqtt_message(self, client, userdata, message):
        a = 0
        if message.topic == "aadc/lidar":
            self.lidar_json = json.loads(str(message.payload.decode("utf-8")))
            a += 1
        elif message.topic == "aadc/sensor":
            self.sensor_json = json.loads(str(message.payload.decode("utf-8")))
            a += 1
        if a > 0:
            self.main_logic()
        return

    def get_value_from_json_tag(self, json_obj, tag_str):
        res = None
        for key, value in json_obj.items():
            if key == tag_str:
                res = ast.literal_eval(str(value))
                break
        return res

    def send_command_manual(self):
        self.mqtt_connection.send_car_command(self.__current_speed_slider, self.__current_steer_slider)

    def send_command_logic(self):
        self.mqtt_connection.send_car_command(self.__current_speed, self.__current_steer)

    def main_logic(self):
        print("logic")
        if ~self.__stop:
            if ~self.manual_control:
                if False:
                #if self.lidarNew and self.sensorNew:
                    if zones.isObjectInRedZoneLidar(self.lidarData):
                        self.__current_speed = 0
                    else:
                        self.send_command()
                    #elsif zones.isObjectInYellowZoneUSDynamic(self.lidarData):
                    # currentSpeed = 83
                        #self.sendCommand()
                else:
                    if zones.isObjectInRedZoneUSDynamic(self.sensor_json, self.__current_speed):
                        self.__current_speed = 90
                        self.send_command_logic()
                    elif zones.isObjectInYellowZoneUSDynamic(self.sensor_json, self.__current_speed):
                        self.__current_speed = 84
                        self.send_command_logic()
                    else:
                        pass
                        #self.send_command_manual()
            else:
                pass
                #self.send_command_manual()
        else:
            self.send_stop()
