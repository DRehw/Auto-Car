#from Controller import Controller
#import Logic
from CurrentData import CurrentData
from math import sin, cos, radians

#current_speed = get_current_speed
current_speed = 0
current_steer = 0
current_min_dist_front_lidar = 0
current_side_dist_lidar = 0

emergencybrake_test_failed = False
left_side_distance_test_failed = False
right_side_distance_test_failed = False

"""
def set_refs(connection, logic, occupancy_map, controller):
    global _connection, _logic, _occupancy_map, _controller
    _connection = connection
    _logic = logic
    _occupancy_map = occupancy_map
    _controller = controller
    print(_logic)
"""

def get_min_front_dist_lidar():
    min_dist = 50000
    for lidar in CurrentData.get_value_from_tag_from_lidar("pcl"):
        if lidar[1] < 10 or lidar[1] > 350:
            dist = lidar[2] * cos(radians(lidar[1]))
            side_dist = lidar[2] * sin(radians(lidar[1]))
            if dist < min_dist and abs(side_dist) <= 150:
                min_dist = dist
    print("    minimal distance: " + str(min_dist))
    return min_dist


def get_min_side_dist_lidar():
    cur_min_distance_to_objects = 50000
    for dataset in CurrentData.get_value_from_tag_from_lidar("pcl"):
        if 60 < dataset[1] < 80 or 280 < dataset[1] < 300:
            dataset_distance = dataset[2] * cos(radians(dataset[1]))
            if dataset_distance < cur_min_distance_to_objects:
                cur_min_distance_to_objects = dataset_distance
    print("    minimal side distance: " + str(cur_min_distance_to_objects))
    return cur_min_distance_to_objects


def test_emergencybrake():
    # global _logic
    # current_speed = _logic.get_current_speed()

    # print("===================Start emergency test==================\n")
    # print("    current speed: " + str(current_speed))
    # print("    current distance: " + str(current_min_dist_front_lidar))

    # Controller.toggle_autopilot_button
    global emergencybrake_test_failed
    min_front_distance = current_min_dist_front_lidar
    if not min_front_distance >= 150:
        print("====emergency brake test failed====\n    front distance too low\n    min front distance: " + str(min_front_distance))
        emergencybrake_test_failed = True
    assert min_front_distance >= 150
    if min_front_distance >= 350:
        # if current_speed >= 90:
            # print("ghgh: {}".format(min_front_distance))
        if not current_speed < 90:
            print("====emergency brake test failed====\n    speed is too low\n    min front distance: " + str(min_front_distance) + "\n    speed: " + str(current_speed))
            emergencybrake_test_failed = True
        assert current_speed < 90
    elif min_front_distance < 310:
        # if current_speed != 90:
            # print("ghgh: {}".format(min_front_distance))
        if not current_speed == 90:
            print("====emergency brake test failed====\n    speed should be 0\n    min front distance: " + str(min_front_distance) + "\n    speed: " + str(current_speed))
            emergencybrake_test_failed = True
        assert current_speed == 90


def test_right_side_distance():
    # print("====================Start right side distance test=======================\n")
    # print("    current steer: " + str(current_steer))
    # print("    current side distance: " + str(current_side_dist_lidar))
    # min_side_distance = get_min_side_dist_lidar()
    global right_side_distance_test_failed
    min_side_distance = current_side_dist_lidar
    if not min_side_distance >= 50:
        print("====right side distance test failed====\n    side distance too low\n    side distance: " + str(min_side_distance))
        right_side_distance_test_failed = True
    assert min_side_distance >= 50
    if min_side_distance >= 200:
        if not current_steer == 90:
            print("====right side distance test failed====\n    steering should be 0\n    side distance: " + str(min_side_distance) + "\n    steering: " + str(current_steer))
            right_side_distance_test_failed = True
        assert current_steer == 90
    elif min_side_distance < 197:
        if not current_steer < 90:
            print("====right side distance test failed====\n    should steer to left\n    side distance: " + str(min_side_distance) + "\n    steering: " + str(current_steer))
            right_side_distance_test_failed = True
        assert current_steer < 90


def test_left_side_distance():
    # print("=========================Start left side distance test==========================\n")
    # print("    current steer: " + str(current_steer))
    # print("    current side distance: " + str(current_side_dist_lidar))
    # min_side_distance = get_min_side_dist_lidar()
    global left_side_distance_test_failed
    min_side_distance = current_side_dist_lidar
    if not min_side_distance >= 50:
        print("====left side distance test failed====\n    side distance too low\n    side distance: " + str(min_side_distance))
        left_side_distance_test_failed = True
    assert min_side_distance >= 50
    if min_side_distance >= 200:
        if not current_steer == 90:
            print("====left side distance test failed====\n    steering should be 0\n    side distance: " + str(min_side_distance) + "\n    steering: " + str(current_steer))
            left_side_distance_test_failed = True
        assert current_steer == 90
    elif min_side_distance < 197:
        if not current_steer > 90:
            print("====left side distance test failed====\n    should steer to right\n    side distance: " + str(min_side_distance) + "\n    steering: " + str(current_steer))
            left_side_distance_test_failed = True
        assert current_steer > 90
