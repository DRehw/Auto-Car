"""
This class (together with the imported methods from the module zones.py) is used to control the movements of the vehicle.
It contains various methods essential for maneuvering the vehicle correctly through an obstacle course.
Especially the method 'main_logic' maintains the overall behaviour of the vehicle using the actuators.
"""
from math import hypot, sin, cos, radians, copysign, inf

import zones
from CurrentData import CurrentData


class Logic:

    def __init__(self, mqtt_connection):
        self.mqtt_connection = mqtt_connection
        CurrentData.register_method_as_observer(self.on_data_change)
        self.controller = None
        self.__manual_control = False       # toggles the manual control mode in debugging view
        self.__autopilot_control = False    # toggles the autopilot control mode
        self.__stop = False                 # used for emergency stop
        self.__current_speed = 90           # 60-89 forwards, 90 stop, 91-120 backwards
        self.__current_speed_slider = 90    # used for the manual control mode
        self.__current_steer = 90           # 60-89 left, 90 straight, 91-120 right
        self.__current_steer_slider = 90    # used for the manual control mode
        self.__drive_backwards = False      # toggles backwards driving in main_logic
        self.__temp_steer = 90              # used for backing up and turning
        return

    def set_controller(self, controller):
        self.controller = controller

    def set_stop(self, stop=True):
        # sets stop to True, activating the emergency brake in next call of main_logic / send_stop
        self.__stop = stop
        if self.__stop:
            self.send_stop()
        return

    def get_stop(self):
        return self.__stop

    def send_stop(self):
        # stops the car as quick as possible
        self.mqtt_connection.send_car_command(90, 90)
        return

    def set_manual_control(self, mc=True):
        # sets the manual_control flag true, using this mode in the next call of main_logic
        self.__manual_control = mc
        return

    def set_autopilot_control(self, ac=True):
        # sets the autopilot_control flag true, using this mode in the next call of main_logic
        self.__autopilot_control = ac
        return

    def get_manual_control(self):
        return self.__manual_control

    def get_autopilot_control(self):
        return self.__autopilot_control

    def get_current_speed(self):
        return self.__current_speed

    def get_current_steer(self):
        return self.__current_steer

    def set_speed_slider(self, val):
        # sets the speed slider value for advanced debugging GUI
        self.__current_speed_slider = val

    def set_steer_slider(self, val):
        # sets the steer slider value for advanced debugging GUI
        self.__current_steer_slider = val

    def send_command_manual(self):
        # used in manual control mode with user input speed and steer values (only advanced debugging GUI)
        self.mqtt_connection.send_car_command(self.__current_speed_slider, self.__current_steer_slider)

    def send_command_logic(self):
        # sending standard autopilot command using calculated speed and steer values
        self.controller.show_autopilot_speed_steer(self.__current_speed, self.__current_steer)
        self.mqtt_connection.send_car_command(self.__current_speed, self.__current_steer)

    def on_data_change(self, changed_data_str):
        # calls the main_logic method when new sensor or lidar data has been received
        if changed_data_str == "lidar" or changed_data_str == "sensor":
            self.main_logic()
        return

    def _get_local_coords_from_lidar(self, angle, distance):
        """ Calculates a two dimensional point relative to the vehicle.
            - the x-axis is parallel to the front bumper
            - the y-axis is orthogonal to the front bumper
        """
        if angle and distance:
            x = distance * sin(radians(angle))
            y = distance * cos(radians(angle))
            return x, y

    def get_steer_obstacle_evasion(self):
        """ Decides whether to evade an obstacle in front of the vehicle on the right or left side.
            - Uses the lidar, distances in millimeter
            - This decision is based on a score.
            - The score is influenced by
                - the distance of all obstacle-points measured parallel to the front bumper
                and
                - how far these points are on the left or right relative to the center of the vehicle
            - Returns a steering value to the side on which are less obstacles located near the vehicle.
        """
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
        """ Returns the smallest distance measured from the front of the vehicle to a possible obstacle.
            - Uses the lidar, distances in millimeter
            - Distances are parallel to the front bumper and
              only relevant if they are inside the straight driving path.
            """
        min_dist = inf
        for lidar in CurrentData.get_value_from_tag_from_lidar("pcl"):
            if lidar[1] < 45 or lidar[1] > 315:
                dist = lidar[2] * cos(radians(lidar[1]))
                side_dist = lidar[2] * sin(radians(lidar[1]))
                if dist < min_dist and abs(side_dist) <= 150:
                    min_dist = dist
        return min_dist

    def main_logic(self):
        """ This is the central method controlling the movement of the vehicle.
            - Maintains 4 driving modes:
                1. Stop
                2. Manual Control
                3. Autopilot Control
                4. Code Test Mode
        """
        if not self.__stop:
            if not self.__manual_control:
                if self.__autopilot_control:
                    """ --- Autopilot Control ---
                            - Is activated via the button in the GUI.
                            - Allows the vehicle to move completely autonomous avoiding obstacles
                              by adjusting the speed and steering.
                    """
                    if not self.__drive_backwards:
                        # driving forwards
                        object_evasion_steering = self.get_steer_obstacle_evasion()

                        if object_evasion_steering != 90:
                            # using object_evasion_steering for obstacles in front
                            self.__current_steer = object_evasion_steering
                        else:
                            # using is_object_close_to_side_lidar for obstacles on the sides
                            self.__current_steer = zones.is_object_close_to_side_lidar()
                        # set the speed
                        self.__current_speed = zones.distance_speed_control(self.__current_steer)

                        # if the autopilot wants to stop, we want the vehicle to back up und turn around
                        if self.__current_speed == 90:
                            self.__drive_backwards = True
                            self.__temp_steer = self.__current_steer    # last steering direction needed for turning
                    if self.__drive_backwards:
                        # driving backwards and turning in the opposite direction of the last steering command
                        if self.__temp_steer >= 90:
                            self.__current_steer = 60
                        elif self.__temp_steer < 90:
                            self.__current_steer = 120
                        else:
                            self.__current_steer = 90
                        self.__current_speed = 97   # set a low speed for backing up

                        """ stop driving backwards if:
                                - The vehicle can steer in the other direction again and
                                  drive without hitting anything for at least 1.25 meters
                                or
                                - An obstacle is close to the rear bumper"""
                        if zones.is_object_in_red_zone_steering_dynamic(self.__current_steer) > 1250 \
                                or zones.is_object_in_backside_red_zone_us():
                            self.__drive_backwards = False
                            self.__current_steer = 90
                            self.__current_speed = 90
                    self.send_command_logic()
                else:
                    # here is room to test autopilot functions with manual control (no button red)
                    self.send_command_logic()
            else:
                self.send_command_manual()
        else:
            self.send_stop()
