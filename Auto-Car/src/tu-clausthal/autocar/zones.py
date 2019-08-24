"""
Created on May 12, 2019

This is a module and does not function as a class.
It contains various methods used in Logic.py.
These methods are essential for calculating the right operation command for the vehicle.
"""

import math
from CurrentData import CurrentData


def is_object_in_backside_red_zone_us():
    """ Returns the boolean value TRUE if an obstacle is near the rear of the vehicle.
        - Input: Distance values (in centimeters) of 3 ultrasonic sensors located inside the rear bumper facing backwards.
        - Extracts the relevant sensors from the sensors-json-string
        - A decent amount of false values are in the range from 0 to 2.
          Because of that the TRUE-returning condition is defined '2 < dist < 15'

        returns:
            TRUE if  at least one of the sensors has a distance value between 2 and 15 cm.
            FALSE if none of the sensors has a distance value between 2 and 15 cm.
    """
    us_data = CurrentData.get_value_from_tag_from_sensor("us")
    us_data = us_data[6:9]
    for dist in us_data:
        if 2 < dist < 15:
            return True
    return False


def is_object_in_red_zone_steering_dynamic(current_steering):
    """ Returns the curved distance to the nearest obstacle located inside a predicted driving path.
        - This path varies with the current steering angle of the front axle
          and represents the room the vehicle would take up driving forward
          if the steering value does not change.
        - Returns a non curved distance if the vehicle does not steer.
        - This method allows the vehicle to speed up while cornering if there are no obstacle in the predicted path.
        - The raw distance input values are measured by the lidar.
        - Distances are scaled in millimeter
    """
    current_steering -= 90
    if current_steering != 0:
        back_axle_offset = (0, -420)
        front_axle_offset = (0, -40)
        wheel_side_offset = 150
        lidar_offset = (0, -70)
        axle_dif_len = 360
        if current_steering < 0:
            current_steering += 5
        elif current_steering > 0:
            current_steering -= 3
        current_steering *= 0.8
        dist_back_ax_to_front_bumper = 450
        rel_x_coord_circ_center_to_wheel = axle_dif_len / math.sin(math.radians(current_steering)) \
                                              * math.sin(math.radians(90-current_steering))
        steering_circle_center = (back_axle_offset[0] + rel_x_coord_circ_center_to_wheel,
                                  back_axle_offset[1])
        outer_circle_radius = math.hypot(abs(steering_circle_center[0]) + wheel_side_offset, axle_dif_len) + 50
        inner_circle_radius = math.hypot(abs(steering_circle_center[0]) - wheel_side_offset, axle_dif_len) - 50
        middle_circle_radius = (outer_circle_radius + inner_circle_radius) / 2
        # Transposing the equation for the arc of a circle (Gleichung für die Länge eines Kreibogens) to get the angle
        hypot = math.hypot(inner_circle_radius, dist_back_ax_to_front_bumper)
        car_look_start_angle = math.asin(dist_back_ax_to_front_bumper / hypot) * 180 / math.pi

        min_distance = math.inf
        for scan in CurrentData.get_value_from_tag_from_lidar("pcl"):
            if 270 <= scan[1] or scan[1] <= 90:
                local_x = scan[2] * math.sin(math.radians(scan[1])) + lidar_offset[0]
                local_y = scan[2] * math.cos(math.radians(scan[1])) + lidar_offset[1]
                distance_to_circle_center = math.hypot(steering_circle_center[0] - local_x, steering_circle_center[1] - local_y)

                if inner_circle_radius <= distance_to_circle_center <= outer_circle_radius:
                    point_offset_form_cricle_x = local_x - steering_circle_center[0]
                    point_offset_form_cricle_y = local_y - steering_circle_center[1]
                    angle = math.asin(point_offset_form_cricle_y / distance_to_circle_center) * 180 / math.pi
                    if point_offset_form_cricle_y >= 0:
                        if point_offset_form_cricle_x >= 0:
                            if current_steering < 0:
                                q = 1
                            else:
                                q = 2
                        else:
                            if current_steering < 0:
                                q = 2
                            else:
                                q = 1
                    else:
                        if point_offset_form_cricle_x >= 0:
                            if current_steering < 0:
                                q = 4
                            else:
                                q = 3
                        else:
                            if current_steering < 0:
                                q = 3
                            else:
                                q = 4
                    if q % 2 == 0:
                        angle = 90 - angle
                    angle += (q-1) * 90

                    distance_on_circle = ((angle - car_look_start_angle) / 360) * 2 * math.pi * distance_to_circle_center
                    if distance_on_circle < min_distance:
                        min_distance = distance_on_circle

        return min_distance
    else:
        min_distance = math.inf
        for dataset in CurrentData.get_value_from_tag_from_lidar("pcl"):
            if dataset[1] < 50 or dataset[1] > 310:
                dataset_distance = dataset[2] * math.cos(math.radians(dataset[1]))
                dataset_side_distance = dataset[2] * math.sin(math.radians(dataset[1]))
                if dataset_distance < min_distance and abs(dataset_side_distance) <= 150:
                    min_distance = dataset_distance
        return min_distance


def distance_speed_control(current_steer):
    """ Is used to control the speed of the vehicle smoothly.
            - The returned speed value depends on the distance to the next obstacle in the front driving path.
            - min_speed_distance: from this value to 0 the vehicle will stop
            - max_speed_distance: from this value and greater the car will drive about one third of its
              possible maximum speed.
            - If the minimum distance is between these two values,
              the car will speed up when the distance becomes greater
              and slow down when the distance to an obstacle gets smaller.
            - The raw distance input values are measured by the lidar.
            - Distances are scaled in millimeter
    """
    min_speed_distance = 350
    max_speed_distance = 4000
    speed_distance_diff = max_speed_distance - min_speed_distance
    min_distance = is_object_in_red_zone_steering_dynamic(current_steer)
    # find smallest distance facing forwards
    # calculate and return speed value
    if min_distance < min_speed_distance:
        return 90
    elif min_distance > max_speed_distance:
        return 80
    else:
        return min(90 - round(min_distance - min_speed_distance) // (round(speed_distance_diff / 10)), 83)


def is_object_close_to_side_lidar():
    """ Makes the car steer away from obstacles located at the sides smoothly.
            - min_steer_distance: from this value to 0 steering is maximized
            - max_steer_distance: from this value and greater the car will not steer
            - If the side distance is between these two values,
              the car will steer more when it comes closer to the obstacle
              and lesser when it veers away from the obstacle.
            - Returns an integer value between 60 and 120.
              (60 steering max left, 90 steering straight, 120 steering max right)
    """
    min_steer_distance = 50
    max_steer_distance = 200
    steer_change_interval_len = max_steer_distance - min_steer_distance
    left_side_minimal = False
    right_side_minimal = False
    cur_min_distance_to_objects = 50000
    # find smallest distance on left OR right side
    for dataset in CurrentData.get_value_from_tag_from_lidar("pcl"):
        if 60 < dataset[1] < 80:
            dataset_distance = dataset[2] * math.cos(math.radians(dataset[1]))
            if dataset_distance < cur_min_distance_to_objects:
                cur_min_distance_to_objects = dataset_distance
                right_side_minimal = True
                left_side_minimal = False
        if 280 < dataset[1] < 300:
            dataset_distance = dataset[2] * math.cos(math.radians(dataset[1]))
            if dataset_distance < cur_min_distance_to_objects:
                cur_min_distance_to_objects = dataset_distance
                right_side_minimal = False
                left_side_minimal = True
    # calculate and return steering value
    if left_side_minimal:
        if cur_min_distance_to_objects < min_steer_distance:
            return 120
        elif cur_min_distance_to_objects > max_steer_distance:
            return 90
        else:
            a = 90 + round((1 - ((cur_min_distance_to_objects - min_steer_distance) / steer_change_interval_len)) * 30)
            return a

    if right_side_minimal:
        if cur_min_distance_to_objects < min_steer_distance:
            return 60
        elif cur_min_distance_to_objects > max_steer_distance:
            return 90
        else:
            a = 90 - round((1 - ((cur_min_distance_to_objects - min_steer_distance) / steer_change_interval_len)) * 30)
            return a
