"""
Created on May 12, 2019
"""

import math
from CurrentData import CurrentData


def is_object_in_red_zone_lidar(lidar_data):
    for dataset in lidar_data:
        length_from_car_orientation = dataset[2]*math.cos(math.radians(dataset[1]))
        if dataset[0] > 10 and (dataset[1] < 20.0 or dataset[1] > 340.0) and length_from_car_orientation < 1000.0:
            # print("{}, {}, {}".format(dataset[0], dataset[1], dataset[2]))
            return True
    return False
"""
def isObjectInYellowZoneLidar():
    for dataset in CurrentData.get_value_from_tag_from_lidar("pcl"):
        if dataset[0] > 10 and (dataset[1] < 20.0 or dataset[1] > 340.0) and dataset[2]*math.cos(math.radians(dataset[1])) < 1500.0:
            #print("{}, {}, {}".format(dataset[0], dataset[1], dataset[2]))
            return True
    return False


def is_object_in_red_zone_us():
    us_data = CurrentData.get_value_from_tag_from_sensor("us")
    us_data = us_data[1:3]
    for dist in us_data:
        if 2 < dist < 150:
            # print(str(usData) + "True")
            return True
    # print(str(usData) + "False")
    return False


def is_object_in_backside_red_zone_us():
    us_data = CurrentData.get_value_from_tag_from_sensor("us")
    us_data = us_data[6:9]
    for dist in us_data:
        if 2 < dist < 15:
        # print(str(usData) + "True")
            return True
    # print(str(usData) + "False")
    return False


def define_red_zone_dynamic(current_speed):
    max_speed = 12
    min_speed = 6
    max_zone = 120
    min_zone = 15
    speed = convert_speed(current_speed)

    if speed >= max_speed:
        red_zone = max_zone
    elif speed <= min_speed:
        red_zone = min_zone
    else:
        red_zone = min_zone + (max_zone - min_zone)/((max_speed - min_speed)/(speed - min_speed))
    # print(redZone)
    return red_zone


def define_yellow_zone_dynamic(current_speed):
    max_speed = 12
    min_speed = 6
    max_zone = 300
    min_zone = 100
    speed = convert_speed(current_speed)

    if speed >= max_speed:
        red_zone = max_zone
    elif speed <= min_speed:
        red_zone = min_zone
    else:
        red_zone = min_zone + (max_zone - min_zone)/((max_speed - min_speed)/(speed - min_speed))
    # print(redZone)
    return red_zone


def is_object_in_red_zone_steering_dynamic(current_steering, current_speed):
    back_axle_offset = (-32, 0)
    fron_axle_offset = (4, 0)
    wheel_side_offset = 15
    lidar_offset = (0, 0)
    axle_dif_len = 30
    rel_x_coord_circ_center_right_wheel = math.tan(math.radians(current_steering)) / axle_dif_len
    steering_circle_center = (back_axle_offset[0] + wheel_side_offset + rel_x_coord_circ_center_right_wheel,
                              back_axle_offset[1])
    outer_circle_radius = math.hypot(abs(steering_circle_center[0]) + wheel_side_offset, axle_dif_len)
    inner_circle_radius = math.hypot(abs(steering_circle_center[0]) - wheel_side_offset, axle_dif_len)
    middle_radius = (outer_circle_radius + inner_circle_radius) / 2
    red_zone_dist = define_red_zone_dynamic(current_speed)
    # Transposing the equation for the arc of a circle (Gleichung für die Länge eines Kreibogens) to get the angle
    look_angle = (red_zone_dist * 180) / (math.pi * middle_radius)
    x_offset_form_circ_center = middle_radius * math.sin(math.radians(look_angle))
    y_offset_form_circ_center = middle_radius * math.cos(math.radians(look_angle))
    if x_offset_form_circ_center != 0:
        incline = y_offset_form_circ_center / x_offset_form_circ_center
    else:
        incline = math.inf
    if incline != math.inf:
        abs_term = steering_circle_center[1] - incline * steering_circle_center[0]

    for scan in CurrentData.get_value_from_tag_from_lidar("pcl"):
        local_x = scan[2] * math.sin(math.radians(scan[1])) + lidar_offset[0]
        local_y = scan[2] * math.cos(math.radians(scan[1])) + lidar_offset[1]
        if incline != math.inf:
            f = local_x * incline + abs_term
        if (incline != math.inf and ((incline < 0 and f <= local_y) or (incline >= 0 and f >= local_y))) \
                or (incline == math.inf and local_x >= steering_circle_center[0]):
            distance_to_circle_center = math.hypot(steering_circle_center[0] - local_x, steering_circle_center[1] - local_y)
            if inner_circle_radius <= distance_to_circle_center <= outer_circle_radius:
                return True

    return False


def is_object_in_red_zone_us_dynamic(current_speed):
    us_data = CurrentData.get_value_from_tag_from_sensor("us")
    us_data = us_data[2]
    """for dist in us_data:
        if 2 < dist < define_red_zone_dynamic(current_speed):
            # print(str(usData) + "True")
            return True
        else:
            return False
    """
    if us_data < define_red_zone_dynamic(current_speed):
        # print("{} < {}".format(us_data, define_red_zone_dynamic(current_speed)))
        return True
    else:
        return False
    # print(str(usData) + "False")



def is_object_in_yellow_zone_us_dynamic(current_speed):
    us_data = CurrentData.get_value_from_tag_from_sensor("us")
    us_data = us_data[0:3]
    for dist in us_data:
        if 2 < dist < define_yellow_zone_dynamic(current_speed):
            # print(str(usData) + "True")
            return True
        else:
            return False
    # print(str(usData) + "False")


def is_object_in_yellow_zone_lidar():
    for dataset in CurrentData.get_value_from_tag_from_lidar("pcl"):
        if dataset[0] > 10 and (dataset[1] < 20.0 or dataset[1] > 340.0) and dataset[2]*math.cos(math.radians(dataset[1])) < 2000.0:
            # print("{}, {}, {}".format(dataset[0], dataset[1], dataset[2]))
            return True
    return False

def is_object_in_side_zone_lidar():
    for dataset in CurrentData.get_value_from_tag_from_lidar("pcl"):

        if dataset[0] > 10 and (70.0 < dataset[1] < 90.0 or 290.0 > dataset[1] > 270.0) and dataset[2]*math.cos(math.radians(dataset[1])) < 800.0:
            # print("{}, {}, {}".format(dataset[0], dataset[1], dataset[2]))
            return True
    return False


def convert_speed(speed):
    speed = 15 - (speed - 75)
    return speed


def is_object_close_to_side_us():
    us_data = CurrentData.get_value_from_tag_from_sensor("us")
    us_data = us_data[4:6]
    # print("{}, {}".format(us_data[0], us_data[1]))
    if us_data[0] < 40:
        return 110
    elif us_data[1] < 40:
        return 70
    else:
        return 90


def distance_speed_control():
    min_speed_distance = 300
    max_speed_distance = 4000
    speed_distance_diff = max_speed_distance - min_speed_distance
    min_distance = math.inf
    # find smallest distance on left OR right side
    for dataset in CurrentData.get_value_from_tag_from_lidar("pcl"):
        if dataset[1] < 50 or dataset[1] > 310:
            dataset_distance = dataset[2] * math.cos(math.radians(dataset[1]))
            dataset_side_distance = dataset[2] * math.sin(math.radians(dataset[1]))
            if dataset_distance < min_distance and abs(dataset_side_distance) <= 150:
                min_distance = dataset_distance
    # calculate and return speed value
    # print("Min distance: {}".format(min_distance))
    if min_distance < min_speed_distance:
        # print(90)
        print("Stoooop")
        return 90
    elif min_distance > max_speed_distance:
        # print(75)
        return 80
    else:
        # print(90 - round((15 * (min_distance - speed_distance_diff)) / speed_distance_diff))
        # print(90 - round(min_distance - min_speed_distance) // (round(speed_distance_diff / 10)))
        return min(90 - round(min_distance - min_speed_distance) // (round(speed_distance_diff / 10)), 83)


def is_object_close_to_side_lidar():
    """ Makes the car steer away from obstacles located at the sides.
            - min_steer_distance: from this value to 0 steering is maximized
            - max_steer_distance: from this value and greater the car will not steer
            - If the side distance is between these two values,
              the car will steer more when it comes closer to the obstacle
              and lesser when it veers away from the obstacle.
    """
    min_steer_distance = 50
    max_steer_distance = 200
    steer_change_interval_len = max_steer_distance - min_steer_distance
    left_side_minimal = False
    right_side_minimal = False
    cur_min_distance_to_objects = 50000     # [{left=0,right=1}, distance]
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
        # print("obstacle left ")
        # print("  " + str(cur_min_distance_to_objects))
        if cur_min_distance_to_objects < min_steer_distance:
            # print(120)
            return 120
        elif cur_min_distance_to_objects > max_steer_distance:
            # print(90)
            return 90
        else:
            # print(90 + (30 - round(cur_min_distance_to_objects - min_steer_distance)) // (round(steer_change_interval_len / 30)))
            a = 90 + round((1 - ((cur_min_distance_to_objects - min_steer_distance) / steer_change_interval_len)) * 30)
            # print(a)
            return a
            # return 90 + (30 - round(cur_min_distance_to_objects - min_steer_distance)) // (round(steer_change_interval_len / 30))
            # print(90 - round((30 * (min_distance - steer_diff)) / steer_diff))
            # return 90 - round((30 * (min_distance - steer_diff)) / steer_diff)

    if right_side_minimal:
        # print("obstacle right ")
        # print("  " + str(cur_min_distance_to_objects))
        if cur_min_distance_to_objects < min_steer_distance:
            # print(60)
            return 60
        elif cur_min_distance_to_objects > max_steer_distance:
            # print(90)
            return 90
        else:
            a = 90 - round((1 - (cur_min_distance_to_objects / steer_change_interval_len)) * 30)
            # print(90 - (30 - round(cur_min_distance_to_objects - min_steer_distance)) // (round(steer_change_interval_len / 30)))
            # print(a)
            return a
            # return 90 - (30 - round(cur_min_distance_to_objects - min_steer_distance)) // (round(steer_change_interval_len / 30))

            # print(90 + round((30 * (min_distance - steer_diff)) / steer_diff))
            # return 90 + round((30 * (min_distance - steer_diff)) / steer_diff)

