from CurrentData import CurrentData
from tkinter import PhotoImage
import numpy as np
import math


class MapTest:

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

    @staticmethod
    def get_global_coords_from_lidar_scan(car_pos, car_heading, lidar_scan_angle, lidar_scan_dist):
        global_angle_rad = math.radians(car_heading + lidar_scan_angle + 180)
        global_x = int(round(lidar_scan_dist/10 * math.sin(global_angle_rad) + car_pos[0]/10))
        global_y = int(round(lidar_scan_dist/10 * math.cos(global_angle_rad) + car_pos[1]/10))
        return global_x, global_y

    def on_data_change(self, changed_data_str):
        if changed_data_str == "lidar":
            lidar_values = CurrentData.get_value_from_tag_from_lidar("pcl")
            car_pos = CurrentData.get_value_from_tag_from_sensor("position")
            car_heading = CurrentData.get_value_from_tag_from_sensor("euler")[0]
            self.lidar_counter += 1
            for scan in lidar_values:
                if 0 <= scan[1] <= 120 or 240 <= scan[1] <= 360:
                    global_x, global_y = MapTest.get_global_coords_from_lidar_scan(car_pos, car_heading, scan[1], scan[2])
                    self.add_point_to_map(global_x, global_y)

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
        car_x = int(round(car_pos[0]/10))
        car_y = int(round(car_pos[1]/10))
        self.ppm_array[self.ppm_array < 1] = 255
        self.ppm_array[self.ppm_array < 255] = 0
        for i in range(-2, 3):
            for j in range(-2, 3):
                self.ppm_array[car_x + i][car_y + j] = 127
        return self.ppm_header + b' ' + self.ppm_array.tobytes()

    def get_map_as_photo_img(self):
        img = PhotoImage(width=self.width, height=self.height, data=self._get_map_as_ppm(), format='PPM')
        return img
