"""
Hallo
"""
from math import hypot, sin, cos, radians, copysign, inf
from traceback import print_exc

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
        self.__drive_backwards = False
        self.__temp_steer = 90
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
        # print("{}, {}\n".format(self.__current_speed_slider, self.__current_steer_slider))

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

    def _get_local_coords_from_lidar(self, angle, distance):
        if angle and distance:
            x = distance * sin(radians(angle))
            y = distance * cos(radians(angle))
            return x, y

    def get_steer_obstacle_evasion(self):
        look_forward_dist_mm = 1200
        lidar = CurrentData.get_value_from_tag_from_lidar("pcl")
        score = 0
        for point in lidar:
            if 0 <= point[1] <= 60 or 300 <= point[1] <= 360:
                local_coords = self._get_local_coords_from_lidar(point[1], point[2])
                if local_coords is not None:
                    x, y = local_coords
                    if abs(x) <= 200 and y <= look_forward_dist_mm:
                        # print("x: {}, y: {}".format(x, y))
                        score += copysign(look_forward_dist_mm / y, x)
        # print("         score: " + str(score))
        if score > 0:
            return 60
        elif score < 0:
            return 120
        else:
            return 90

    def get_front_dist_lidar(self):
        min_dist = inf
        for lidar in CurrentData.get_value_from_tag_from_lidar("pcl"):
            if lidar[1] < 45 or lidar[1] > 315:
                dist = lidar[2] * cos(radians(lidar[1]))
                side_dist = lidar[2] * sin(radians(lidar[1]))
                if dist < min_dist and abs(side_dist) <= 150:
                    min_dist = dist
        return min_dist

    def main_logic(self):
        if not self.__stop:
            if not self.__manual_control:
                if self.__autopilot_control:

                    """
                    if zones.speed_control():
                        print("84")
                        self.__current_speed = 84
                        self.send_command_logic()
                    else:
                        print("80")
                        self.__current_speed = 80
                        self.send_command_logic()
                    """
                    # example test:
                    # self.__current_steer = zones.is_object_close_to_side_us()
                    if not self.__drive_backwards:
                        object_evasion_steering = self.get_steer_obstacle_evasion()

                        if object_evasion_steering != 90:
                            # print("Using object evasion steering: {}".format(object_evasion_steering))
                            self.__current_steer = object_evasion_steering
                        else:
                            self.__current_steer = zones.is_object_close_to_side_lidar()
                        self.__current_speed = zones.distance_speed_control(self.__current_steer)
                        if self.__current_speed == 90:
                            self.__drive_backwards = True
                            self.__temp_steer = self.__current_steer
                    if self.__drive_backwards:
                        if self.__temp_steer >= 90:
                            self.__current_steer = 60
                        elif self.__temp_steer < 90:
                            self.__current_steer = 120
                        else:
                            self.__current_steer = 90
                        self.__current_speed = 97

                        if zones.is_object_in_red_zone_steering_dynamic(self.__current_steer) > 1250 \
                                or zones.is_object_in_backside_red_zone_us():
                            self.__drive_backwards = False
                            self.__current_steer = 90
                            self.__current_speed = 90
                    self.send_command_logic()
                    """
                    if zones.is_object_in_red_zone_us_dynamic(self.__current_speed):
                        self.__current_speed = 90
                        self.send_command_logic()
                        #print("90")
                    elif zones.is_object_in_yellow_zone_lidar():
                        self.__current_speed = 83
                        self.send_command_logic()
                        #print("84")
                    elif zones.is_object_in_side_zone_lidar():
                        self.__current_speed = 81
                        self.send_command_logic()
                        #print("82")
                    else:
                        self.__current_speed = 79
                        self.send_command_logic()
                        #print("80")
                    """
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
            self.send_stop()
