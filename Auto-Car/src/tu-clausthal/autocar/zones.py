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
    min_zone = 40
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


def is_object_close_to_side_lidar():
    for dataset in CurrentData.get_value_from_tag_from_lidar("pcl"):
        if dataset[0] > 10:
            if 60 < dataset[1] < 80:
                print(dataset)
                left_distance = dataset[2] * math.cos(math.radians(dataset[1]))
                if left_distance < 200:
                    return 60
            elif 280 < dataset[1] < 300:
                print(dataset)
                right_distance = dataset[2] * math.cos(math.radians(dataset[1]))
                if right_distance < 200:
                    return 110
    return 90
