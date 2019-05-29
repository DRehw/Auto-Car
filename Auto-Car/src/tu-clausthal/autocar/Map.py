"""
Created on 14.05.2019

@author: David, Mirko
"""
# cmd: pip install matplotlib

import math
import matplotlib as mpl
import numpy as np
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
        """ Construct an empty occupancy grid.

        Arguments: width,
                   height    -- The grid will have height rows and width
                                columns cells.  width is the size of
                                the x-dimension and height is the size
                                of the y-dimension.
        """
        CurrentData.register_method_as_observer(self.on_data_change)
        self.width = width  # x_max
        self.height = height  # y_max
        self.grid = np.zeros((width, height))
        self.constant = 0  # Used to correct for wrong starting position of euler
        self.euler_reseted = False
        self.lidar_counter = 0
        self.sensor_data_list = []
        self.waiting_for_final_sensor = False

    def reset_poor_map_data(self):
        for i in range(self.width):
            for j in range(self.height):
                if self.grid[i][j] < 5:
                    self.grid[i][j] = 0
        return

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

    def on_data_change(self, changed_data_str):
        if not self.euler_reseted:
            self.calc_constant(CurrentData.get_value_from_tag_from_sensor("euler"))
        if self.euler_reseted and changed_data_str == "lidar":
            self.waiting_for_final_sensor = True
            if self.lidar_counter < 50:
                self.lidar_counter += 1
            else:
                self.reset_poor_map_data()
                self.lidar_counter = 0

        if changed_data_str == "sensor":
            self.add_sensor_data_to_list()
            if self.waiting_for_final_sensor == True:
                self.waiting_for_final_sensor = False
                self.add_lidar_data_to_map()
        return

    def set_cell(self, x, y, val):
        """ Set the value of a cell in the grid.
#
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

    def show_map(self):
        """ Show an image of the Map including the grid and a legend.
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
        """ #calculates coordinates based on a lidar measurement, used in addLidarDataToMap
        """
        # print("Position: {}, {}".format(position[0], position[1]))
        radians = math.radians(measurement[1])
        radians = radians + math.radians(euler[0])
        radians = radians + math.radians(self.constant)
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
                    Map.set_cell(self, coord[0], coord[1], 1)
        return


    def interpolate_by_time(self, sensors1, sensors2, time_point):
        time_interval =  sensors2[0] - sensors1[0]
        #distance = math.sqrt(((sensors2[1][0] - sensors1[1][0])**2 + (sensors2[1][1] - sensors1[1][1])**2))
        if sensors2[1][0] < sensors1[1][0]:
            dif_x = -(sensors1[1][0] - sensors2[1][0])
            print(dif_x)
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
        sensor_timestamp = CurrentData.get_value_from_tag_from_sensor("timestamp")
        sensor_position = [[CurrentData.get_value_from_tag_from_sensor("position")[0]],[CurrentData.get_value_from_tag_from_sensor("position")[1]]]
        sensor_euler = CurrentData.get_value_from_tag_from_sensor("euler")[0]
        self.sensor_data_list.append([sensor_timestamp,sensor_position,sensor_euler])



    def get_interval(self, sensor_data_list, time_point):
        for i in range(len(sensor_data_list)):
            if self.sensor_data_list[i][0] >= time_point:
                return [[i-1],[i]]

    def add_lidar_data_to_map(self):
        """ Implements getLidarVector() to addLidarData to the map, uses aadc/lidar/pcl, aadc/sensor/position, aadc/sensor/euler as lidarData,position,euler
            Should be called on whenever Controller.onMessage() receives lidar data
        """
        #position = CurrentData.get_value_from_tag_from_sensor("position")
        #euler = CurrentData.get_value_from_tag_from_sensor("euler")
        lidarData = CurrentData.get_value_from_tag_from_lidar("pcl")
        lidar_timestamp = CurrentData.get_value_from_tag_from_lidar("timestamp")
        current_time_point = 0
        last_lidar_degree = None
        last_sensor = None
        try:
            for i in range(len(lidarData)):
                if (last_lidar_degree == None) or (last_lidar_degree + 2.5 > lidarData[i][1]):
                    if lidarData[i][1] < 90 or lidarData[i][1] > 270:
                        interval = self.get_interval((lidar_timestamp - 100 + current_time_point))
                        relative_time_point = (lidar_timestamp - 100 + current_time_point) - self.sensor_data_list[interval[0]][0]
                        interpolated_data = self.interpolate_by_time(self.sensor_data_list[interval[0]],self.sensor_data_list[interval[1]], relative_time_point)
                        last_sensor = self.sensor_data_list[interval[1]]
                        position = interpolated_data[2]
                        euler = [interpolated_data[3]]
                        coord = self.get_lidar_vector(lidarData[i], position, euler)
                        if (self.width > coord[0] > 0) and (self.height > coord[1] > 0):
                            Map.set_cell(self, coord[0], coord[1], 1)
                current_time_point += 100 / 120
                last_lidar_degree = lidarData[i][1]
                self.sensor_data_list = [[last_sensor]]
        except:
            self.add_lidar_data_to_map_without_interpolation()
        return


    def calc_constant(self, euler):
        """ Calculates constant based on aadc/sensor/euler, to be used when car is put in the base position
            is now automatically done when subscribed
        """

        self.constant = - euler[0]
        self.euler_reseted = True
        return
