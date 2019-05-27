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

    def reset_poor_map_data(self):
        for i in range(self.width):
            for j in range(self.height):
                if self.grid[i][j] < 5:
                    self.grid[i][j] = 0

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

    def set_cell(self, x, y, val):
        """ Set the value of a cell in the grid.

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
        """ calculates coordinates based on a lidar measurement, used in addLidarDataToMap
        """
        # print("Position: {}, {}".format(position[0], position[1]))
        radians = math.radians(measurement[1])
        radians = radians + math.radians(euler[0])
        radians = radians + math.radians(self.constant)
        x_coord = (measurement[2] / 10) * math.cos(radians) + (position[1] / 10)
        y_coord = (measurement[2] / 10) * math.sin(radians) + (position[0] / 10)
        return int(round(x_coord, 0)), int(round(y_coord, 0))

    def add_lidar_data_to_map(self):
        """ Implements getLidarVector() to addLidarData to the map, uses aadc/lidar/pcl, aadc/sensor/position, aadc/sensor/euler as lidarData,position,euler
            Should be called on whenever Controller.onMessage() receives lidar data
        """
        position = CurrentData.get_value_from_tag_from_sensor("position")
        euler = CurrentData.get_value_from_tag_from_sensor("euler")
        lidarData = CurrentData.get_value_from_tag_from_lidar("pcl")
        for i in range(len(lidarData)):
            if lidarData[i][1] < 90 or lidarData[i][1] > 270:
                coord = self.get_lidar_vector(lidarData[i], position, euler)
                if (self.width > coord[0] > 0) and (self.height > coord[1] > 0):
                    Map.set_cell(self, coord[0], coord[1], 1)
        return

    def calc_constant(self, euler):
        """ Calculates constant based on aadc/sensor/euler, to be used when car is put in the base position
            is now automatically done when subscribed
        """

        self.constant = - euler[0]
        self.euler_reseted = True
        return
