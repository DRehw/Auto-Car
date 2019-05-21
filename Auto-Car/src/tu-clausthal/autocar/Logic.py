"""
Hallo
"""
import json
import ast
import zones
from CurrentData import CurrentData


class Logic:

    def __init__(self, mqtt_connection):
        self.mqtt_connection = mqtt_connection
        CurrentData.register_method_as_observer(self.on_data_change)
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

    def send_command_manual(self):
        self.mqtt_connection.send_car_command(self.__current_speed_slider, self.__current_steer_slider)

    def send_command_logic(self):
        print("self command logic")
        self.mqtt_connection.send_car_command(self.__current_speed, self.__current_steer)

    def on_data_change(self, changed_data_str):
        if changed_data_str == "lidar" or changed_data_str == "sensor":
            self.main_logic()
        return

    def main_logic(self):
        if ~self.__stop:
            if ~self.__manual_control:
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
                    if zones.isObjectInRedZoneUSDynamic(self.__current_speed):
                        self.__current_speed = 90
                        self.send_command_logic()
                    elif zones.isObjectInYellowZoneUSDynamic(self.__current_speed):
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
