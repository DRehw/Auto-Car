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


def is_object_in_red_zone_us():
    us_data = CurrentData.get_value_from_tag_from_sensor("us")
    us_data = us_data[1:3]
    for dist in us_data:
        if 2 < dist < 100:
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
        # print(str(usData) + "True")
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
    print("{}, {}".format(us_data[0], us_data[1]))
    if us_data[0] < 40:
        return 110
    elif us_data[1] < 40:
        return 70
    else:
        return 90


def distance_speed_control():
    min_speed_distance = 200
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
    print("Min distance: {}".format(min_distance))
    if min_distance < min_speed_distance:
        print(90)
        return 90
    elif min_distance > max_speed_distance:
        print(75)
        return 75
    else:
        # print(90 - round((15 * (min_distance - speed_distance_diff)) / speed_distance_diff))
        print(90 - round(min_distance - min_speed_distance) // (round(speed_distance_diff / 15)))
        return min(90 - round(min_distance - min_speed_distance) // (round(speed_distance_diff / 15)), 84)


def is_object_close_to_side_lidar():
    """ Makes the car steer away from obstacles located at the sides.
            - min_steer_distance: from this value to 0 steering is maximized
            - max_steer_distance: from this value and greater the car will not steer
            - If the side distance is between these two values,
              the car will steer more when it comes closer to the obstacle
              and lesser when it veers away from the obstacle.
    """
    min_steer_distance = 60
    max_steer_distance = 200
    steer_diff = max_steer_distance - min_steer_distance
    min_dataset = [0, 50000]     # [{left=0,right=1}, distance]
    # find smallest distance on left OR right side
    for dataset in CurrentData.get_value_from_tag_from_lidar("pcl"):
        if 50 < dataset[1] < 80:
            dataset_distance = dataset[2] * math.cos(math.radians(dataset[1]))
            if dataset_distance < min_dataset[1]:
                min_dataset = [1, dataset_distance]
        if 280 < dataset[1] < 310:
            dataset_distance = dataset[2] * math.cos(math.radians(dataset[1]))
            if dataset_distance < min_dataset[1]:
                min_dataset = [0, dataset_distance]
    # calculate and return steering value
    print(min_dataset)
    if min_dataset[0] == 0:
        if min_dataset[1] < min_steer_distance:
            print(120)
            return 120
        elif min_dataset[1] > max_steer_distance:
            print(90)
            return 90
        else:
            print(90 - round((30 * (min_dataset[1] - steer_diff)) / steer_diff))
            return 90 - round((30 * (min_dataset[1] - steer_diff)) / steer_diff)
    if min_dataset[0] == 1:
        if min_dataset[1] < min_steer_distance:
            print(60)
            return 60
        elif min_dataset[1] > max_steer_distance:
            print(90)
            return 90
        else:
            print(90 + round((30 * (min_dataset[1] - steer_diff)) / steer_diff))
            return 90 + round((30 * (min_dataset[1] - steer_diff)) / steer_diff)

