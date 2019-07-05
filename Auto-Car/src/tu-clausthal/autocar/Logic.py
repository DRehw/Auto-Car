"""
Hallo
"""
from math import hypot, sin, cos, radians, copysign

import zones
import KeyController
from CurrentData import CurrentData
import test_papa_pytest


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

    def hindernisse(self):
        lidar = CurrentData.get_value_from_tag_from_lidar("pcl")
        last_point = None
        print("\n")
        count = 0
        level = 0
        for i, point in enumerate(lidar):
            x, y = self._get_local_coords_from_lidar(point[1], point[2])
            if last_point:
                distance_to_last_point = hypot(x - last_point[0], y - last_point[1])
                supposed_distance = 0.15 * last_point[2]
                if distance_to_last_point > supposed_distance:
                    if point[2] > last_point[2]:
                        level += 1
                        print("({}) Beginning at pos: {},{}".format(level, x, y))
                    else:
                        level -= 1
                        print("({}) Ending at pos: {},{}".format(level, last_point[0], last_point[1]))
                    count += 1
            last_point = [x, y, point[2]]
        print(str(count) + "\n")
        return

    def get_steer_dir_obstacle_evasion(self, lidar):
        changes = []
        last_point = None
        for i, point in enumerate(lidar):
            point = lidar[i]
            x, y = self._get_local_coords_from_lidar(point[1], point[2])
            if last_point is None:
                last_point_lidar = lidar[len(lidar)][2]
                x, y = self._get_local_coords_from_lidar(last_point_lidar[1], last_point_lidar[2])
                last_point = [x, y, last_point_lidar[2]]
            distance_to_last_point = hypot(x - last_point[0], y - last_point[1])
            supposed_distance = 0.15 * last_point[2]
            if distance_to_last_point > supposed_distance:
                if i == 0:
                    index = len(lidar)
                else:
                    index = i
                if point[2] > last_point[2]:
                    changes.append([index, 1])
                else:
                    changes.append([index, -1])
            last_point = [x, y, point[2]]
        if len(changes) >= 2:
            if changes[0][0] > len(lidar) - changes[len(changes)][0]:
                return "left"
            else:
                return "right"

    def get_steer_obstacle_evasion(self):
        look_forward_dist_mm = 1000
        lidar = CurrentData.get_value_from_tag_from_lidar("pcl")
        score = 0
        for point in lidar:
            if 0 <= point[1] <= 60 or 300 <= point[1] <= 360:
                x, y = self._get_local_coords_from_lidar(point[1], point[2])
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
        min_dist = 50000
        for lidar in CurrentData.get_value_from_tag_from_lidar("pcl"):
            if lidar[1] < 10 or lidar[1] > 350:
                dist = lidar[2] * cos(radians(lidar[1]))
                side_dist = lidar[2] * sin(radians(lidar[1]))
                if dist < min_dist and abs(side_dist) <= 150:
                    min_dist = dist
        return min_dist

    def main_logic(self):
        test_papa_pytest.current_speed = self.get_current_speed()
        # test_papa_pytest.current_steer = self.get_currrent_steer()
        if not self.__stop:
            if not self.__manual_control:
                if self.__autopilot_control:
                    """
                        testmodus
                    """
                    self.__current_steer = zones.is_object_close_to_side_lidar()
                    self.__current_speed = zones.distance_speed_control()
                    self.send_command_logic()
                    # test_papa_pytest.test_emergencybrake()
                    # test_papa_pytest.test_right_side_distance()
                    test_papa_pytest.test_left_side_distance()

                    """
                        normal mode
                    """
                    """
                    if not self.__drive_backwards:
                        object_evasion_steering = self.get_steer_obstacle_evasion()
                        if object_evasion_steering != 90:
                            # print("Using object evasion steering: {}".format(object_evasion_steering))
                            self.__current_steer = object_evasion_steering
                        else:
                            self.__current_steer = zones.is_object_close_to_side_lidar()
                        self.__current_speed = zones.distance_speed_control()
                        if self.__current_speed == 90:
                        # (self.__current_steer > 95 or self.__current_steer < 85) and
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

                        if self.get_front_dist_lidar() > 1250 or zones.is_object_in_backside_red_zone_us():
                            self.__drive_backwards = False
                            self.__current_steer = 90
                            self.__current_speed = 90
                    self.send_command_logic()
                    """

                else:   # here is room to test autopilot functions with manual control (no button red)
                    if zones.is_object_in_red_zone_us_dynamic(self.__current_speed):
                        self.__current_speed = 90
                        self.send_command_logic()
                        """elif zones.isObjectInYellowZoneUSDynamic(self.__current_speed):
                        self.__current_speed = 84
                        self.send_command_logic()"""
                    else:
                        speed, steer = KeyController.get_cur_speed_and_steer()
                        self.__current_speed_slider = 90 - speed
                        self.__current_steer_slider = 90 - steer
                        self.send_command_manual()
            else:
                self.send_command_manual()
        else:
            self.send_stop()
