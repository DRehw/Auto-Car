"""
Created on 14.05.2019

@author: David, Mirko
"""
# cmd: pip install matplotlib

import math
import matplotlib as mpl
import numpy as np
from tkinter import PhotoImage
from time import time
import array
from CurrentData import CurrentData
from matplotlib import pyplot


class Map:
    """
    The Map class stores an occupancy grid as a two dimensional
    numpy array.

    Public instance variables:

        origin_x   --  Position of the grid cell (0,0) in
        origin_y   --    in the map coordinate system.
        grid       --  numpy array with height rows and width columns.

    Note that x increases with increasing column number and y increases
    with increasing row number.
    """

    def __init__(self, width=800, height=800):
        """
        Construct an empty occupancy grid.

        Arguments: width,
                   height    -- The grid will have height rows and width
                                columns cells.  width is the size of
                                the x-dimension and height is the size
                                of the y-dimension.
        """
        CurrentData.register_method_as_observer(self.on_data_change)
        if width > 0:
            self.width = width  # x_max
        if height > 0:
            self.height = height  # y_max
        self.grid = np.zeros((self.width, self.height), np.uint8)
        self.constant = 0  # Used to correct for wrong starting position of euler
        self.euler_reseted = False
        self.lidar_counter = 0
        self.ppm_header = bytes('P5 {} {} 255 '.format(self.width, self.height), 'ascii')
        self.ppm_array = np.zeros((self.width, self.height), np.uint8)
        self.sensor_data_list = []  # list of sensor data elements of the Form [[timestamp,position[],euler]]
        self.waiting_for_final_sensor = False  # set true when lidar data arrives and false, when the next sensor data arrive

    def reset_poor_map_data(self):
        self.grid[self.grid < 30] = 0

    """
    def on_data_change(self, changed_data_str):
        if not self.euler_reseted:
            self.calc_constant(CurrentData.get_value_from_tag_from_sensor("euler"))
        if self.euler_reseted and changed_data_str == "lidar":
            self.add_lidar_data_to_map()
            if self.lidar_counter < 50:
                self.lidar_counter += 1
            else:
                self.reset_poor_map_data()
                self.lidar_counter = 0
        return
    """

    def calculate_constant_automatic(self, sensor1, sensor2):
        x = np.degrees(math.atan2(sensor2[1][0] - sensor1[1][0], sensor1[1][1] - sensor2[1][1])) - 90
        if x < 0:
            x = (360 + x)
        constant = x + sensor2[2]
        if constant >= 360:
            constant = constant - 360
        self.constant = - constant
        self.euler_reseted = True
        return

    def on_data_change(self, changed_data_str):
        if not self.euler_reseted:
            #self.calc_constant(CurrentData.get_value_from_tag_from_sensor("euler"))
            if len(self.sensor_data_list) >= 20:
                distance = math.sqrt(((self.sensor_data_list[19][1][0] - self.sensor_data_list[0][1][0]) ** 2 + (self.sensor_data_list[19][1][1] - self.sensor_data_list[0][1][1]) ** 2))
                if distance >= 120:
                    self.calculate_constant_automatic(self.sensor_data_list[0], self.sensor_data_list[19])
        if self.euler_reseted and changed_data_str == "lidar":
            self.waiting_for_final_sensor = True
            if self.lidar_counter < 50:
                self.lidar_counter += 1
            else:
                self.reset_poor_map_data()
                self.lidar_counter = 0

        if changed_data_str == "sensor":
            self.add_sensor_data_to_list()
            if self.waiting_for_final_sensor:
                self.waiting_for_final_sensor = False
                if self.euler_reseted:
                    self.add_lidar_data_to_map()
        else:
            return
        return

    def set_cell(self, x, y, val):
        """
        Set the value of a cell in the grid.

        Arguments:
            x, y  - This is a point in the map coordinate frame.
            val   - This is the value that should be assigned to the
                    grid cell that contains (x,y).
                    There is no defined value range yet and therefore no checking for val
        """
        if 0 <= x <= self.width and 0 <= y <= self.height:
            # self.grid[x][y] = val
            self.grid[x][y] += val
        return

    def set_cells(self, x,y):
        self.set_cell(x-2,y-2, 1)
        self.set_cell(x-2,y-1, 2)
        self.set_cell(x-2,y, 3)
        self.set_cell(x-2,y+1, 2)
        self.set_cell(x-2,y+2, 1)
        self.set_cell(x-1,y-2, 2)
        self.set_cell(x-1,y-1, 4)
        self.set_cell(x-1,y, 4)
        self.set_cell(x-1,y+1, 4)
        self.set_cell(x-1,y+2, 2)
        self.set_cell(x,y-2, 3)
        self.set_cell(x,y-1, 4)
        self.set_cell(x,y, 5)
        self.set_cell(x,y+1, 4)
        self.set_cell(x,y+2, 3)
        self.set_cell(x+1,y-2, 2)
        self.set_cell(x+1,y-1, 4)
        self.set_cell(x+1,y, 4)
        self.set_cell(x+1,y+1, 4)
        self.set_cell(x+1,y+2, 2)
        self.set_cell(x+2,y-2, 1)
        self.set_cell(x+2,y-1, 2)
        self.set_cell(x+2,y, 3)
        self.set_cell(x+2,y+1, 2)
        self.set_cell(x+2,y+2, 1)

    def show_map(self):
        """
        Show an image of the Map including the grid and a legend.
        Later on it is possible to implement different brightness levels for different values
        """

        # make a color map of fixed colors
        cmap = mpl.colors.ListedColormap(['white', 'grey', 'black'])
        bounds = [0, 5, 1000]
        norm = mpl.colors.BoundaryNorm(bounds, cmap.N)

        # tell imshow about color map so that only set colors are used
        img = pyplot.imshow(self.grid, origin="lower", interpolation='nearest',
                            cmap=cmap, norm=norm)

        # make a color bar
        pyplot.colorbar(img, cmap=cmap,
                        norm=norm, boundaries=bounds, ticks=[0, 5, 1000])

        pyplot.show()
        return

    def get_lidar_vector(self, measurement, position, euler):
        """
        calculates coordinates based on a lidar measurement, used in addLidarDataToMap
        """
        # print("Position: {}, {}".format(position[0], position[1]))
        radians = math.radians(measurement[1])
        radians += math.radians(euler[0])
        radians -= math.radians(self.constant)
        x_coord = (measurement[2] / 10) * math.cos(radians) + (position[1] / 10)
        y_coord = (measurement[2] / 10) * math.sin(radians) + (position[0] / 10)
        return int(round(x_coord, 0)), int(round(y_coord, 0))

    def add_lidar_data_to_map_without_interpolation(self):

        #Implements getLidarVector() to addLidarData to the map, uses aadc/lidar/pcl, aadc/sensor/position, aadc/sensor/euler as lidarData,position,euler
        #Should be called on whenever Controller.onMessage() receives lidar data

        position = CurrentData.get_value_from_tag_from_sensor("position")
        euler = CurrentData.get_value_from_tag_from_sensor("euler")
        lidarData = CurrentData.get_value_from_tag_from_lidar("pcl")
        for i in range(len(lidarData)):
            if lidarData[i][1] < 90 or lidarData[i][1] > 270:
                coord = self.get_lidar_vector(lidarData[i], position, euler)
                if (self.width > coord[0] > 0) and (self.height > coord[1] > 0):
                    # Map.set_cell(self, coord[0], coord[1], 1)
                    Map.set_cells(self, coord[0], coord[1])
        return


    def interpolate_by_time(self, sensors1, sensors2, time_point):
        # returns interpolated position for a specified time point between two sensor data elements (positions)

        time_interval =  sensors2[0] - sensors1[0]
        ##distance = math.sqrt(((sensors2[1][0] - sensors1[1][0])**2 + (sensors2[1][1] - sensors1[1][1])**2))
        if sensors2[1][0] < sensors1[1][0]:
            dif_x = -(sensors1[1][0] - sensors2[1][0])
        else:
            dif_x = sensors2[1][0] - sensors1[1][0]
        if sensors2[1][1] < sensors1[1][1]:
            dif_y = -(sensors1[1][1] - sensors2[1][1])
        else:
            dif_y = sensors2[1][1] - sensors1[1][1]
        if sensors2[2] < sensors1[2]:
            euler_interval = sensors2[2] + 360 - sensors1[2]
        else:
            euler_interval = sensors2[2] - sensors1[2]
        new_x = sensors1[1][0] + dif_x*(time_point/time_interval)
        new_y = sensors1[1][1] + dif_y*(time_point/time_interval)
        new_euler = sensors1[2] + euler_interval*(time_point/time_interval)
        if new_euler > 360:
            new_euler = new_euler - 360
        new_timestamp = sensors1[0]+time_point
        return [new_timestamp,time_point, [new_x,new_y],new_euler]


    def add_sensor_data_to_list(self):
        #adds sensor data from CurrentData to self.sensor_data_list

        sensor_timestamp = CurrentData.get_value_from_tag_from_sensor("timestamp")
        sensor_position = [CurrentData.get_value_from_tag_from_sensor("position")[0],CurrentData.get_value_from_tag_from_sensor("position")[1]]
        sensor_euler = CurrentData.get_value_from_tag_from_sensor("euler")[0]
        self.sensor_data_list.append([sensor_timestamp,sensor_position,sensor_euler])
        if len(self.sensor_data_list) > 20:
            del self.sensor_data_list[0]
        # print(CurrentData.get_value_from_tag_from_sensor("euler")[0])



    def get_interval(self, time_point):
        # returns interval of elements from self.sensor_data_list within a specified time point is located

        for i in range(len(self.sensor_data_list)):
            if self.sensor_data_list[i][0] >= time_point:
                return [i-1, i]

    def add_lidar_data_to_map(self):
        """ Implements getLidarVector() to addLidarData to the map, uses aadc/lidar/pcl, aadc/sensor/position, aadc/sensor/euler as lidarData,position,euler
            Should be called on whenever Controller.onMessage() receives lidar data
            Uses interpolation
        """
        #position = CurrentData.get_value_from_tag_from_sensor("position")
        #euler = CurrentData.get_value_from_tag_from_sensor("euler")
        lidarData = CurrentData.get_value_from_tag_from_lidar("pcl")
        lidar_timestamp = CurrentData.get_value_from_tag_from_lidar("timestamp")
        current_time_point = 0
        last_lidar_degree = None
        #last_sensor = None
        try:
            for i in range(len(lidarData)):
                if (last_lidar_degree == None) or (last_lidar_degree + 2.5 > lidarData[i][1]):
                    if lidarData[i][1] < 90 or lidarData[i][1] > 270:
                        interval = self.get_interval((lidar_timestamp - 100 + current_time_point))
                        relative_time_point = (lidar_timestamp - 100 + current_time_point) - self.sensor_data_list[interval[0]][0]
                        interpolated_data = self.interpolate_by_time(self.sensor_data_list[interval[0]],self.sensor_data_list[interval[1]], relative_time_point)
                        #last_sensor = self.sensor_data_list[interval[1]]
                        position = interpolated_data[2]
                        euler = [interpolated_data[3]]
                        coord = self.get_lidar_vector(lidarData[i], position, euler)
                        if (self.width > coord[0] > 0) and (self.height > coord[1] > 0):
                            #Map.set_cell(self, coord[0], coord[1], 1)
                            Map.set_cells(self, coord[0], coord[1])
                current_time_point += 100 / 120
                last_lidar_degree = lidarData[i][1]
        except Exception as InterpolationError:
            print("Interpolation Failed!\n" + str(InterpolationError))
            self.add_lidar_data_to_map_without_interpolation()
        return


    def calc_constant(self, euler):
        """
        Calculates constant based on aadc/sensor/euler, to be used when car is put in the base position
        is now automatically done when subscribed
        """

        self.constant = - euler[0]
        self.euler_reseted = True
        return

    @staticmethod
    def get_color_from_value(value):
        if value > 0:
            return 0
        else:
            return 255

    def _get_map_as_ppm(self):
        self.ppm_array = np.copy(self.grid)
        self.ppm_array[self.ppm_array < 1] = 255
        return self.ppm_header + b' ' + self.ppm_array.tobytes()

    def get_map_as_photo_img(self):
        img = PhotoImage(width=self.width, height=self.height, data=self._get_map_as_ppm(), format='PPM')
        return img
