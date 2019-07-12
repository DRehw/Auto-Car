"""
Created on May 12, 2019
"""

import math
from CurrentData import CurrentData


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

"""
def is_object_in_red_zone_steering_dynamic(current_steering, current_speed):
    if current_steering != 0:
        back_axle_offset = (0, -32)
        fron_axle_offset = (0, 4)
        wheel_side_offset = 15
        lidar_offset = (0, 0)
        axle_dif_len = 30
        dist_back_ax_to_front_bumper = 45
        rel_x_coord_circ_center_to_wheel = axle_dif_len / math.sin(math.radians(current_steering)) \
                                              * math.sin(math.radians(90-current_steering))
        steering_circle_center = (back_axle_offset[0] + rel_x_coord_circ_center_to_wheel,
                                  back_axle_offset[1])
        outer_circle_radius = math.hypot(abs(steering_circle_center[0]) + wheel_side_offset, axle_dif_len)
        inner_circle_radius = math.hypot(abs(steering_circle_center[0]) - wheel_side_offset, axle_dif_len)
        middle_circle_radius = (outer_circle_radius + inner_circle_radius) / 2
        red_zone_dist = define_red_zone_dynamic(current_speed)
        # Transposing the equation for the arc of a circle (Gleichung für die Länge eines Kreibogens) to get the angle
        look_angle = (100 * 180) / (math.pi * middle_circle_radius)
        car_look_start_angle = math.asin(45 / inner_circle_radius) * 180 / math.pi
        x_offset_form_circ_center = middle_circle_radius * math.cos(math.radians(car_look_start_angle + look_angle))
        y_offset_form_circ_center = middle_circle_radius * math.sin(math.radians(car_look_start_angle + look_angle))
        if x_offset_form_circ_center != 0:
            car_rel_x_from_point = steering_circle_center[0] + x_offset_form_circ_center
            car_rel_y_from_point = steering_circle_center[1] + y_offset_form_circ_center
            incline = y_offset_form_circ_center / x_offset_form_circ_center
        else:
            incline = math.inf
        if incline != math.inf:
            abs_term = steering_circle_center[1] - incline * steering_circle_center[0]

        min_distance = math.inf
        for scan in CurrentData.get_value_from_tag_from_lidar("pcl"):
            if 270 <= scan[1] or scan[1] <= 90:
                local_x = scan[2]/10 * math.sin(math.radians(scan[1])) + lidar_offset[0]
                local_y = scan[2]/10 * math.cos(math.radians(scan[1])) + lidar_offset[1]
                if incline != math.inf:
                    f = local_x * incline + abs_term
                if (incline != math.inf and ((incline < 0 and f <= local_y) or (incline >= 0 and f >= local_y))) \
                        or (incline == math.inf and local_x >= steering_circle_center[0]):
                    distance_to_circle_center = math.hypot(steering_circle_center[0] - local_x, steering_circle_center[1] - local_y)
                    if inner_circle_radius <= distance_to_circle_center <= outer_circle_radius:
                        print("Hallo")
                        distance_to_car = math.hypot(local_x, local_y)
                        if distance_to_car < min_distance:
                            min_distance = distance_to_car

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
"""


def is_object_in_red_zone_steering_dynamic(current_steering):
    current_steering -= 90
    if current_steering != 0:
        back_axle_offset = (0, -420)
        fron_axle_offset = (0, -40)
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
        # look_angle = (100 * 180) / (math.pi * middle_circle_radius)
        # x_offset_form_circ_center = middle_circle_radius * math.cos(math.radians(car_look_start_angle + look_angle))
        # y_offset_form_circ_center = middle_circle_radius * math.sin(math.radians(car_look_start_angle + look_angle))
        hypot = math.hypot(inner_circle_radius, dist_back_ax_to_front_bumper)
        car_look_start_angle = math.asin(dist_back_ax_to_front_bumper / hypot) * 180 / math.pi

        min_distance = math.inf
        for scan in CurrentData.get_value_from_tag_from_lidar("pcl"):
            if 270 <= scan[1] or scan[1] <= 90:
                local_x = scan[2] * math.sin(math.radians(scan[1])) + lidar_offset[0]
                local_y = scan[2] * math.cos(math.radians(scan[1])) + lidar_offset[1]
                # print(local_y)
                distance_to_circle_center = math.hypot(steering_circle_center[0] - local_x, steering_circle_center[1] - local_y)

                if inner_circle_radius <= distance_to_circle_center <= outer_circle_radius:
                    # point_angle = math.asin(back_axle_offset[1] + local_y / distance_to_circle_center) * 180 / math.pi
                    # distance_on_circle = point_angle/360 * 2 * math.pi * distance_to_circle_center
                    point_offset_form_cricle_x = local_x - steering_circle_center[0]
                    point_offset_form_cricle_y = local_y - steering_circle_center[1]
                    angle = math.asin(point_offset_form_cricle_y / distance_to_circle_center) * 180 / math.pi
                    # print("x: {}, y: {}, angle: {}".format(point_offset_form_cricle_x, point_offset_form_cricle_y, angle))
                    q = 0
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

                    # print("    {}".format(angle + angle_offset))
                    # distance_on_circle = math.hypot(local_x, local_y)
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


def is_object_in_red_zone_us_dynamic(current_speed):
    us_data = CurrentData.get_value_from_tag_from_sensor("us")
    if us_data is not None:
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


def convert_speed(speed):
    speed = 90 - speed
    return speed


def distance_speed_control(current_steer):
    min_speed_distance = 350
    max_speed_distance = 4000
    speed_distance_diff = max_speed_distance - min_speed_distance
    min_distance = is_object_in_red_zone_steering_dynamic(current_steer)
    print("    {:2}cm".format(min_distance))
    # print(min_distance)
    # find smallest distance on left OR right side
    # calculate and return speed value
    # print("Min distance: {}".format(min_distance))
    if min_distance < min_speed_distance:
        # print(90)
        # print("Stoooop")
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
            a = 90 - round((1 - ((cur_min_distance_to_objects - min_steer_distance) / steer_change_interval_len)) * 30)
            # print(90 - (30 - round(cur_min_distance_to_objects - min_steer_distance)) // (round(steer_change_interval_len / 30)))
            # print(a)
            return a
            # return 90 - (30 - round(cur_min_distance_to_objects - min_steer_distance)) // (round(steer_change_interval_len / 30))

            # print(90 + round((30 * (min_distance - steer_diff)) / steer_diff))
            # return 90 + round((30 * (min_distance - steer_diff)) / steer_diff)

