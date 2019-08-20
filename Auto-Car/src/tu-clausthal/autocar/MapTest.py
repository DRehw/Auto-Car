from CurrentData import CurrentData
from tkinter import PhotoImage
import numpy as np
import math
from History import History


class MapTest:

    """
    This class creates a global map (2D occupancy grid) of the cars surroundings, using lidar, rotation and position
    data, and provides the methods to convert the map into an image, which can be displayed on the GUI.
    """

    use_interpolation = True

    car_point_radius = 14
    car_point_range = range(-car_point_radius, car_point_radius + 1)
    car_heading_point_radius = int(car_point_radius / 3)
    car_heading_point_range = range(-car_heading_point_radius, car_heading_point_radius + 1)

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
        self.euler_offset = 0
        self.gui = None

    def gui_init(self, gui):
        """initializes GUI"""
        self.gui = gui

    def get_global_coords_from_lidar_scan(self, car_pos, car_heading, lidar_scan_angle, lidar_scan_dist):
        """
        Calculates the global coordinates of a detected lidar point using car position, rotation and
        the angle and distance of the lidar point
        """
        global_angle_rad = math.radians(car_heading + lidar_scan_angle + self.euler_offset)
        global_x = int(round(lidar_scan_dist/10 * math.sin(global_angle_rad) + car_pos[0]/10))
        global_y = int(round(-lidar_scan_dist/10 * math.cos(global_angle_rad) + car_pos[1]/10))
        return global_x, global_y

    def on_data_change(self, changed_data_str):
        """
        Is registered as an observer method of CurrentDatas __on_data_change method (see _init_). Is called whenever
        CurrentData receives new sensor/lidar data, receiving a data string "lidar"/"sensor" corresponding to the type
        of data received. Determines what is to be done when such data is received, i.e. adding lidar data to
        map/adding sensor data to history.
        """
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
            if self.wait_for_next_sensor_data and MapTest.use_interpolation:
                self.add_last_lidar_set_to_map()
                self.wait_for_next_sensor_data = False

    def calculate_euler_offset(self):
        """
        Calculates offset for the car rotation to arrive at the cars "global orientation".
        To be used when car is in "default position"
        """
        self.euler_offset = CurrentData.get_value_from_tag_from_sensor("euler")[0] - 90

    def get_interpolated_pos_and_euler(self, timestamp):
        """
        returns the approximated car position and rotation for a specified timestamp using linear interpolation.
        Only used if use_interpolation == True. (see self.add_last_lidar_set_to_map)
        """
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
        """adds the last collected lidar set (after converting it into global coordinates) to the map."""
        self.lidar_counter += 1
        for i, scan in enumerate(self.last_lidar_set):
            if 0 <= scan[1] <= 120 or 240 <= scan[1] <= 360:
                if MapTest.use_interpolation:
                    current_ts = self.last_lidar_set_ts - 100 + int(round((i / len(self.last_lidar_set) * 100)))
                    car_pos, car_heading = self.get_interpolated_pos_and_euler(current_ts)
                else:
                    last_history_element = self.pos_euler_history.get(len(self.pos_euler_history)-1)
                    car_pos = last_history_element[1]
                    car_heading = last_history_element[2]
                global_x, global_y = MapTest.get_global_coords_from_lidar_scan(self, car_pos, car_heading, scan[1], scan[2])
                self.add_point_to_map(global_x, global_y)
        if self.lidar_counter >= 30:
            self.lidar_counter = 0
            self.reset_poor_map_data()

    def add_point_to_map(self, x, y):
        """adds a point (described by x and y coordinates) to the map by increasing the integer values of the
        corresponding element in the grid as well as its immediate surroundings"""
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
        """Resets the map to a blank (np.zeros) grid.
        To be used when euler/rotation is reset or when map data is faulty."""
        self.grid = np.zeros((self.width, self.height), np.uint8)

    def reset_poor_map_data(self):
        """removes points from map which don't pass a minimum threshold of times measured"""
        self.grid[self.grid < 2] = 0

    def _get_map_as_ppm(self):
        """Generates a 2D-grid representing a visually intuitive 8-bit graphic representative of the map.
        Adds car position and rotation to the new grid. Used in self.get_map_as_photo_img"""
        self.ppm_array = np.copy(self.grid)
        car_pos = CurrentData.get_value_from_tag_from_sensor("position")
        car_heading = CurrentData.get_value_from_tag_from_sensor("euler")
        self.ppm_array[self.ppm_array < 1] = 255
        self.ppm_array[self.ppm_array < 255] = 0
        if car_pos is not None and car_heading is not None:
            car_x = int(round(car_pos[0]/10))
            car_y = int(round(car_pos[1]/10))
            car_heading[0] = 360 - car_heading[0]
            # car_heading[0] = car_heading[0] + 180
            for i in MapTest.car_point_range:
                for j in MapTest.car_point_range:
                    if 0 <= car_x + i < self.width and 0 <= car_y + j < self.height:
                        dist = math.hypot(i, j)
                        if dist <= MapTest.car_point_radius:
                            grey_val = 50 + (dist / MapTest.car_point_radius) * 50
                            self.ppm_array[car_x + i][car_y + j] = grey_val
            heading_x = int(car_x + MapTest.car_point_radius * math.sin(math.radians(self.euler_offset + car_heading[0])))
            heading_y = int(car_y + MapTest.car_point_radius * -math.cos(math.radians(self.euler_offset + car_heading[0])))
            # print("{}, {}".format(MapTest.car_point_radius * math.sin(self.euler_offset + car_heading[0]),
            #                      MapTest.car_point_radius * math.cos(self.euler_offset + car_heading[0])))
            # print("{}".format(self.euler_offset + car_heading[0]))

            for i in MapTest.car_heading_point_range:
                for j in MapTest.car_heading_point_range:
                    if 0 <= heading_x + i < self.width and 0 <= heading_y + j < self.height:
                        dist = math.hypot(i, j)
                        if dist <= MapTest.car_heading_point_radius:
                            self.ppm_array[heading_x + i][heading_y + j] = 255
        self.ppm_array = np.fliplr(self.ppm_array)
        return self.ppm_header + b' ' + self.ppm_array.tobytes()

    def get_map_as_photo_img(self):
        """generates an image representing the map and returns the image"""
        img = PhotoImage(width=self.width, height=self.height, data=self._get_map_as_ppm(), format='PPM')
        return img
