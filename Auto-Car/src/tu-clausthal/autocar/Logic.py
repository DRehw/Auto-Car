"""
Hallo
"""
import zones
from CurrentData import CurrentData


class Logic:

    def __init__(self, mqtt_connection):
        self.mqtt_connection = mqtt_connection
        CurrentData.register_method_as_observer(self.on_data_change)
        self.controller = None
        self.__manual_control = False
        self.__autopilot_control = False
        self.__stop = False
        self.__current_speed = 90
        self.__current_speed_slider = 90
        self.__current_steer = 90
        self.__current_steer_slider = 90
        return

    def set_controller(self, controller):
        self.controller = controller

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

    def set_autopilot_control(self, ac = True):
        self.__autopilot_control = ac
        return

    def get_manual_control(self):
        return self.__manual_control

    def get_autopilot_control(self):
        return self.__autopilot_control

    def get_current_speed(self):
        return self.__current_speed

    def get_currrent_steer(self):
        return self.__current_steer

    def set_speed_slider(self, val):
        self.__current_speed_slider = val

    def set_steer_slider(self, val):
        self.__current_steer_slider = val

    def send_command_manual(self):
        self.mqtt_connection.send_car_command(self.__current_speed_slider, self.__current_steer_slider)

    def send_command_logic(self):
        self.controller.show_autopilot_speed_steer(self.__current_speed, self.__current_steer)
        self.mqtt_connection.send_car_command(self.__current_speed, self.__current_steer)

    def on_data_change(self, changed_data_str):
        '''if changed_data_str == "lidar":
            lidar = CurrentData.get_value_from_tag_from_lidar("pcl")
            max = 0
            for data in lidar:
                if data[2] > max:
                    max = data[2]
            print(max)
            print(str(lidar[0][2]) + "\n")'''
        if changed_data_str == "lidar" or changed_data_str == "sensor":
            self.main_logic()
        return

    def main_logic(self):
        if not self.__stop:
            if not self.__manual_control:
                if self.__autopilot_control:
                    """
                    put speed control here
                    """
                    # example test:
                    # self.__current_steer = zones.is_object_close_to_side_us()
                    self.__current_steer = zones.is_object_close_to_side_lidar()
                    if zones.is_object_in_red_zone_us_dynamic(self.__current_speed):
                        self.__current_speed = 90
                        self.send_command_logic()
                        #print("90")
                    elif zones.is_object_in_yellow_zone_lidar():
                        self.__current_speed = 84
                        self.send_command_logic()
                        #print("84")
                    elif zones.is_object_in_side_zone_lidar():
                        self.__current_speed = 82
                        self.send_command_logic()
                        #print("82")
                    else:
                        self.__current_speed = 80
                        self.send_command_logic()
                        #print("80")
                else:   # here is room to test autopilot functions with manual control (no button red)
                    if zones.is_object_in_red_zone_us_dynamic(self.__current_speed):
                        self.__current_speed = 90
                        self.send_command_logic()
                        """elif zones.isObjectInYellowZoneUSDynamic(self.__current_speed):
                        self.__current_speed = 84
                        self.send_command_logic()"""
                    else:
                        self.send_command_manual()
            else:
                self.send_command_manual()
        else:
            self.send_stop()
