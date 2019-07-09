from CurrentData import CurrentData
from tkinter import PhotoImage
import numpy as np
import math
from History import History


class MapTest:

    use_interpolation = True
    front_left_corner_offset_to_pozyx = (-15, 10)
    front_left_corner_distance_to_pozyx = math.hypot(front_left_corner_offset_to_pozyx[0],
                                                     front_left_corner_offset_to_pozyx[1])
    front_left_corner_angle_to_pozyx = math.asin(front_left_corner_offset_to_pozyx[1] /
                                                 front_left_corner_distance_to_pozyx)

    back_right_corner_offset_to_pozyx = (15, 30)
    back_right_corner_distance_to_pozyx = math.hypot(back_right_corner_offset_to_pozyx[0],
                                                     back_right_corner_offset_to_pozyx[1])
    back_right_corner_angle_to_pozyx = math.asin(back_right_corner_offset_to_pozyx[1] /
                                                 back_right_corner_distance_to_pozyx)

    def __init__(self, width=800, height=800):
        CurrentData.register_method_as_observer(self.on_data_change)
        if width > 0:
            self.width = width  # x_max
        if height > 0:
            self.height = height  # y_max
        self.grid = np.zeros((self.width, self.height), np.uint8)
        self.lidar_counter = 0
        self.ppm_header = bytes('P5 {} {} 255 '.format(self.width, self.height), 'ascii')
        self.ppm_array = np.zeros((self.width, self.height), np.uint8)
        self.pos_euler_history = History(10)
        self.last_lidar_set = []
        self.last_lidar_set_ts = 0
        self.wait_for_next_sensor_data = False
        self.euler_offset = 45
        self.gui = None

    def gui_init(self, gui):
        self.gui = gui

    @staticmethod
    def get_global_coords_from_lidar_scan(car_pos, car_heading, lidar_scan_angle, lidar_scan_dist):
        global_angle_rad = math.radians(car_heading + lidar_scan_angle + 180)
        global_x = int(round(lidar_scan_dist/10 * math.sin(global_angle_rad) + car_pos[0]/10))
        global_y = int(round(-lidar_scan_dist/10 * math.cos(global_angle_rad) + car_pos[1]/10))
        return global_x, global_y

    def on_data_change(self, changed_data_str):
        if changed_data_str == "lidar":
            self.last_lidar_set = CurrentData.get_value_from_tag_from_lidar("pcl")
            self.last_lidar_set_ts = CurrentData.get_value_from_tag_from_lidar("timestamp")
            if MapTest.use_interpolation:
                self.wait_for_next_sensor_data = True
            else:
                self.add_last_lidar_set_to_map()
        elif changed_data_str == "sensor":
            pos = CurrentData.get_value_from_tag_from_sensor("position")[:-1]
            euler = 360 - CurrentData.get_value_from_tag_from_sensor("euler")[0]
            timestamp = CurrentData.get_value_from_tag_from_sensor("timestamp")
            self.pos_euler_history.append([timestamp, pos, euler])
            # self.update_car_rect_on_canvas()
            if self.wait_for_next_sensor_data and MapTest.use_interpolation:
                self.add_last_lidar_set_to_map()
                self.wait_for_next_sensor_data = False

    def get_interpolated_pos_and_euler(self, timestamp):
        pos_euler_history_len = len(self.pos_euler_history)
        if pos_euler_history_len > 0:
            first_entry = self.pos_euler_history.get(0)
            last_entry = self.pos_euler_history.get(pos_euler_history_len - 1)
            if first_entry[0] <= timestamp <= last_entry[0]:
                for i in range(pos_euler_history_len):
                    cur = self.pos_euler_history.get(i)
                    if timestamp < cur[0]:
                        if 0 < i <= pos_euler_history_len-1:
                            prev = self.pos_euler_history.get(i-1)
                            lin_interpol_factor = (timestamp-prev[0]) / (cur[0]-prev[0])
                            interpol_pos = []
                            for j, val in enumerate(prev[1]):
                                interpol_pos.append(val + lin_interpol_factor * (cur[1][j]-val))
                            interpol_euler = prev[2]
                            normal_dist = cur[2] - prev[2]
                            distance_over_360 = min(360 - prev[2] + cur[2], 360 - cur[2] + prev[2])
                            if distance_over_360 < normal_dist:
                                if prev[2] < cur[2]:
                                    distance_over_360 = -distance_over_360
                                euler_offset = lin_interpol_factor * distance_over_360
                            else:
                                euler_offset = lin_interpol_factor * normal_dist
                            interpol_euler = prev[2] + euler_offset
                            if interpol_euler < 0:
                                interpol_euler = 360 + interpol_euler
                            elif interpol_euler > 360:
                                interpol_euler = interpol_euler % 360
                            return interpol_pos, interpol_euler
                        elif i == 0:
                            return cur[1], cur[2]
                    else:
                        if i == pos_euler_history_len:
                            return cur[1], cur[2]

            elif timestamp < first_entry[0]:
                return first_entry[1], first_entry[2]
            else:
                return last_entry[1], last_entry[2]

    def add_last_lidar_set_to_map(self):
        for i, scan in enumerate(self.last_lidar_set):
            if 0 <= scan[1] <= 120 or 240 <= scan[1] <= 360:
                if MapTest.use_interpolation:
                    current_ts = self.last_lidar_set_ts - 100 + int(round((i / len(self.last_lidar_set) * 100)))
                    car_pos, car_heading = self.get_interpolated_pos_and_euler(current_ts)
                else:
                    last_history_element = self.pos_euler_history.get(len(self.pos_euler_history)-1)
                    car_pos = last_history_element[1]
                    car_heading = last_history_element[2]
                global_x, global_y = MapTest.get_global_coords_from_lidar_scan(car_pos, car_heading, scan[1], scan[2])
                self.add_point_to_map(global_x, global_y)

    def update_car_rect_on_canvas(self):
        if len(self.pos_euler_history) > 0:
            last_sensor_entry = self.pos_euler_history.get(len(self.pos_euler_history)-1)
            pos = last_sensor_entry[1]
            for axis in pos:
                axis = round(axis/10, 2)
            euler = last_sensor_entry[2]
            global_front_angle = euler + self.euler_offset - 90 + MapTest.front_left_corner_angle_to_pozyx
            front_left_corner_global_offset = (MapTest.front_left_corner_distance_to_pozyx * math.sin(global_front_angle),
                                               MapTest.front_left_corner_distance_to_pozyx * math.cos(global_front_angle))
            global_back_angle = euler + self.euler_offset + 180 + MapTest.back_right_corner_angle_to_pozyx
            back_right_corner_global_offset = (MapTest.back_right_corner_distance_to_pozyx * math.sin(global_back_angle),
                                               MapTest.back_right_corner_distance_to_pozyx * math.cos(global_back_angle))
            self.gui.update_car_rect()

    def add_point_to_map(self, x, y):
        # print("{} {}".format(x, y))
        for i in range(-2, 3):
            for j in range(-2, 3):
                if 0 <= x + i < self.width and 0 <= y + j < self.height:
                    dist = math.hypot(i, j)
                    if dist >= 2:
                        self.grid[x + i][y + j] += 1
                    elif 0 < dist < 2:
                        self.grid[x + i][y + j] += 2
                    else:
                        self.grid[x + i][y + j] += 3

    def reset_map(self):
        self.grid = np.zeros((self.width, self.height), np.uint8)

    def _get_map_as_ppm(self):
        self.ppm_array = np.copy(self.grid)
        car_pos = CurrentData.get_value_from_tag_from_sensor("position")
        self.ppm_array[self.ppm_array < 1] = 255
        self.ppm_array[self.ppm_array < 255] = 0
        if car_pos is not None:
            car_x = int(round(car_pos[0]/10))
            car_y = int(round(car_pos[1]/10))
            for i in range(-2, 3):
                for j in range(-2, 3):
                    self.ppm_array[car_x + i][car_y + j] = 127
        return self.ppm_header + b' ' + self.ppm_array.tobytes()

    def get_map_as_photo_img(self):
        img = PhotoImage(width=self.width, height=self.height, data=self._get_map_as_ppm(), format='PPM')
        return img
