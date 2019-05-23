'''
Created on 14.05.2019

@author: David, Mirko
'''
# cmd: pip install matplotlib

import math
import matplotlib as mpl
import numpy as np
from CurrentData import CurrentData
from matplotlib import pyplot


class Map:
    '''
    The Map class stores an occupancy grid as a two dimensional
    numpy array.

    Public instance variables:

        origin_x   --  Position of the grid cell (0,0) in
        origin_y   --    in the map coordinate system.
        grid       --  numpy array with height rows and width columns.

    Note that x increases with increasing column number and y increases
    with increasing row number.
    '''

    def __init__(self, width=800, height=800):
        ''' Construct an empty occupancy grid.

        Arguments: width,
                   height    -- The grid will have height rows and width
                                columns cells.  width is the size of
                                the x-dimension and height is the size
                                of the y-dimension.
        '''
        CurrentData.register_method_as_observer(self.on_data_change)
        self.width = width  # x_max
        self.height = height  # y_max
        #self.grid = np.arange(width*height).reshape(width,height)
        self.grid = np.zeros((width,height))
        self.constant = 0  #Used to correct for wrong starting position of euler

    def on_data_change(self, changed_data_str):
        if changed_data_str == "lidar":
            self.add_lidar_data_to_map()

    def set_cell(self, x, y, val):
        ''' Set the value of a cell in the grid.

        Arguments:
            x, y  - This is a point in the map coordinate frame.
            val   - This is the value that should be assigned to the
                    grid cell that contains (x,y).
                    There is no defined value range yet and therefore no checking for val
        '''
        #if x >= 0 and x <= self.width and y >= 0 and y <= self.height:
        #    self.grid[x][y] = val
        #else:
        #    pass
        self.grid[x][y] = val
        return

    # make values from 0 to 2, for this example
    # here we could assign different colors for more frequently calculated points
    # grid = np.random.rand(5000,7000)*2
    def show_map(self):
        ''' Show an image of the Map including the grid and a legend
            later on it is possible to implement different brightness levels for different values
        '''

        # make a color map of fixed colors
        cmap = mpl.colors.ListedColormap(['white', 'black'])
        bounds = [0, 1, 2]
        norm = mpl.colors.BoundaryNorm(bounds, cmap.N)

        # tell imshow about color map so that only set colors are used
        img = pyplot.imshow(self.grid, origin="lower", interpolation='nearest',
                            cmap=cmap, norm=norm)

        # make a color bar
        pyplot.colorbar(img, cmap=cmap,
                        norm=norm, boundaries=bounds, ticks=[0, 1, 2])

        pyplot.show()
        return

    def get_lidar_vector(self, measurement, position, euler):
        # calculates coordinates based on a lidar measurement, used in addLidarDataToMap
        radians = math.radians(measurement[1])
        radians = radians + math.radians(euler[0])
        radians = radians + math.radians(self.constant)
        xCoord = (measurement[2] / 10) * math.cos(radians) + (position[0] / 10)
        yCoord = (measurement[2] / 10) * math.sin(radians) + (position[1] / 10)
        #print(xCoord, yCoord)
        return (int(round(xCoord, 0)), int(round(yCoord, 0)))

    def add_lidar_data_to_map(self):
    # implements getLidarVector() to addLidarData to the map, uses aadc/lidar/pcl, aadc/sensor/position, aadc/sensor/euler as lidarData,position,euler
    # should be called on whenever Controller.onMessage() receives lidar data
        position = CurrentData.get_value_from_tag_from_sensor("position")
        euler = CurrentData.get_value_from_tag_from_sensor("euler")
        lidarData = CurrentData.get_value_from_tag_from_lidar("pcl")
        for i in range(len(lidarData)):
            if lidarData[i][1] < 90 or lidarData[i][1] > 270:
                coord = self.get_lidar_vector(lidarData[i], position, euler)
                #print(coord[0], coord[1])
                if (self.width > coord[0] > 0) and (self.height > coord[1] > 0):
                    #print("coordinates ok")
                    Map.set_cell(self,coord[0], coord[1], 1)
                    #map[coord[0]][coord[1]] = True
        return

    def calc_constant(self, euler):
        # calculates constant based on aadc/sensor/euler, to be used when car is put in the base position
        # should get a GUI Button

        self.constant = - euler[0]
        return
'''
    def testMap():
        # tests Map functions based on test data

        testLidar = [[15, 350.96875, 1920.5], [15, 353.0, 1874.0], [15, 355.046875, 1828.75], [15, 357.09375, 1795.25], [15, 359.0625, 1759.75], [15, 1.078125, 1728.25], [15, 3.140625, 1694.0], [15, 5.109375, 1667.0], [15, 7.125, 1647.5], [15, 9.21875, 1626.25], [15, 11.21875, 1612.0], [15, 13.203125, 1599.0], [15, 15.1875, 1583.0], [15, 17.25, 1569.75], [15, 19.203125, 1564.75], [15, 21.21875, 1562.0], [15, 23.265625, 1547.25], [15, 25.28125, 1545.0], [15, 27.28125, 1545.0], [15, 29.21875, 1550.25], [15, 31.25, 1549.5], [15, 33.265625, 1547.5], [15, 35.5, 1564.0], [15, 37.5625, 1565.25], [15, 39.546875, 1582.0], [15, 41.546875, 1589.25], [15, 43.578125, 1608.25], [11, 45.546875, 1668.5], [9, 47.640625, 1607.0], [10, 49.609375, 1636.25], [15, 51.609375, 1798.25], [15, 53.59375, 1805.25], [15, 55.484375, 2152.25], [15, 57.53125, 2032.5], [15, 59.046875, 2050.75], [15, 60.96875, 2336.75], [15, 62.984375, 2203.25], [15, 64.65625, 4206.75], [15, 66.640625, 4283.0], [15, 68.625, 4402.5], [15, 70.578125, 4554.75], [15, 72.5625, 4741.25], [15, 74.515625, 4911.0], [15, 76.484375, 5103.25], [15, 78.640625, 3395.25], [15, 80.609375, 3298.75], [15, 82.96875, 3231.5], [15, 91.0625, 2975.5], [15, 93.0625, 2950.5], [15, 95.078125, 2906.25], [15, 97.09375, 2872.5], [15, 109.03125, 2745.5], [15, 111.015625, 2721.5], [15, 113.015625, 2730.5], [15, 115.03125, 2731.0], [15, 117.0, 2713.5], [15, 119.015625, 2721.5], [15, 121.015625, 2734.5], [15, 123.0, 2752.5], [15, 125.015625, 2754.5], [15, 127.0, 2785.5], [15, 128.96875, 2800.75], [15, 130.96875, 2821.75], [15, 135.109375, 2152.75], [15, 137.140625, 1973.75], [15, 148.078125, 256.5], [15, 150.015625, 249.0], [15, 152.65625, 254.25], [15, 148.96875, 2599.0], [15, 165.6875, 1408.0], [15, 167.921875, 1199.25], [15, 169.921875, 1213.25], [15, 172.0625, 1074.0], [15, 174.15625, 1018.0], [13, 184.78125, 132.0], [15, 186.84375, 134.25], [15, 190.859375, 132.25], [14, 187.921875, 1134.5], [15, 206.375, 384.75], [15, 217.890625, 1409.75], [15, 223.96875, 1302.5], [15, 230.515625, 823.75], [15, 232.625, 806.5], [15, 234.625, 793.75], [15, 236.71875, 782.25], [15, 238.78125, 768.5], [8, 242.484375, 875.75], [15, 244.671875, 823.0], [15, 245.703125, 1793.75], [9, 247.9375, 1361.25], [15, 253.8125, 1537.75], [15, 256.0, 1208.25], [15, 262.125, 1101.0], [15, 264.25, 1044.25], [15, 266.265625, 1025.75], [14, 268.21875, 1098.75], [15, 270.046875, 1243.0], [15, 280.34375, 1160.0], [11, 289.0625, 381.0], [15, 291.0, 375.75], [15, 301.265625, 5028.25], [15, 303.265625, 5066.5], [15, 305.265625, 5088.5], [15, 307.203125, 5856.0], [15, 313.1875, 6159.0], [15, 319.171875, 6294.25], [15, 321.328125, 3743.5], [15, 323.546875, 3491.0], [15, 325.5625, 3262.75], [15, 327.609375, 3059.5], [15, 329.625, 2895.5], [15, 331.65625, 2730.5], [15, 333.71875, 2622.0], [15, 335.765625, 2499.75], [15, 337.78125, 2378.5], [15, 339.828125, 2288.0], [15, 341.828125, 2204.25], [15, 343.890625, 2124.0], [15, 345.9375, 2056.25], [15, 347.90625, 1999.5]]
        testPosition = [5000, 3000, 0]
        testEuler = [114.18, 1.65, 179.36]

        calcConstant(testEuler)
        addLidarDataToMap(testLidar, testPosition, testEuler)
        #generateMapImg()
        return
'''
"""
testmap = Map()
#testMap
#Map.set_cell(testmap, 5, 5, 1)

testLidar = [[15, 350.96875, 1920.5], [15, 353.0, 1874.0], [15, 355.046875, 1828.75], [15, 357.09375, 1795.25], [15, 359.0625, 1759.75], [15, 1.078125, 1728.25], [15, 3.140625, 1694.0], [15, 5.109375, 1667.0], [15, 7.125, 1647.5], [15, 9.21875, 1626.25], [15, 11.21875, 1612.0], [15, 13.203125, 1599.0], [15, 15.1875, 1583.0], [15, 17.25, 1569.75], [15, 19.203125, 1564.75], [15, 21.21875, 1562.0], [15, 23.265625, 1547.25], [15, 25.28125, 1545.0], [15, 27.28125, 1545.0], [15, 29.21875, 1550.25], [15, 31.25, 1549.5], [15, 33.265625, 1547.5], [15, 35.5, 1564.0], [15, 37.5625, 1565.25], [15, 39.546875, 1582.0], [15, 41.546875, 1589.25], [15, 43.578125, 1608.25], [11, 45.546875, 1668.5], [9, 47.640625, 1607.0], [10, 49.609375, 1636.25], [15, 51.609375, 1798.25], [15, 53.59375, 1805.25], [15, 55.484375, 2152.25], [15, 57.53125, 2032.5], [15, 59.046875, 2050.75], [15, 60.96875, 2336.75], [15, 62.984375, 2203.25], [15, 64.65625, 4206.75], [15, 66.640625, 4283.0], [15, 68.625, 4402.5], [15, 70.578125, 4554.75], [15, 72.5625, 4741.25], [15, 74.515625, 4911.0], [15, 76.484375, 5103.25], [15, 78.640625, 3395.25], [15, 80.609375, 3298.75], [15, 82.96875, 3231.5], [15, 91.0625, 2975.5], [15, 93.0625, 2950.5], [15, 95.078125, 2906.25], [15, 97.09375, 2872.5], [15, 109.03125, 2745.5], [15, 111.015625, 2721.5], [15, 113.015625, 2730.5], [15, 115.03125, 2731.0], [15, 117.0, 2713.5], [15, 119.015625, 2721.5], [15, 121.015625, 2734.5], [15, 123.0, 2752.5], [15, 125.015625, 2754.5], [15, 127.0, 2785.5], [15, 128.96875, 2800.75], [15, 130.96875, 2821.75], [15, 135.109375, 2152.75], [15, 137.140625, 1973.75], [15, 148.078125, 256.5], [15, 150.015625, 249.0], [15, 152.65625, 254.25], [15, 148.96875, 2599.0], [15, 165.6875, 1408.0], [15, 167.921875, 1199.25], [15, 169.921875, 1213.25], [15, 172.0625, 1074.0], [15, 174.15625, 1018.0], [13, 184.78125, 132.0], [15, 186.84375, 134.25], [15, 190.859375, 132.25], [14, 187.921875, 1134.5], [15, 206.375, 384.75], [15, 217.890625, 1409.75], [15, 223.96875, 1302.5], [15, 230.515625, 823.75], [15, 232.625, 806.5], [15, 234.625, 793.75], [15, 236.71875, 782.25], [15, 238.78125, 768.5], [8, 242.484375, 875.75], [15, 244.671875, 823.0], [15, 245.703125, 1793.75], [9, 247.9375, 1361.25], [15, 253.8125, 1537.75], [15, 256.0, 1208.25], [15, 262.125, 1101.0], [15, 264.25, 1044.25], [15, 266.265625, 1025.75], [14, 268.21875, 1098.75], [15, 270.046875, 1243.0], [15, 280.34375, 1160.0], [11, 289.0625, 381.0], [15, 291.0, 375.75], [15, 301.265625, 5028.25], [15, 303.265625, 5066.5], [15, 305.265625, 5088.5], [15, 307.203125, 5856.0], [15, 313.1875, 6159.0], [15, 319.171875, 6294.25], [15, 321.328125, 3743.5], [15, 323.546875, 3491.0], [15, 325.5625, 3262.75], [15, 327.609375, 3059.5], [15, 329.625, 2895.5], [15, 331.65625, 2730.5], [15, 333.71875, 2622.0], [15, 335.765625, 2499.75], [15, 337.78125, 2378.5], [15, 339.828125, 2288.0], [15, 341.828125, 2204.25], [15, 343.890625, 2124.0], [15, 345.9375, 2056.25], [15, 347.90625, 1999.5]]
testPosition = [5000, 3000, 0]
testEuler = [114.18, 1.65, 179.36]

Map.calcConstant(testEuler)
Map.addLidarDataToMap(testmap, testLidar, testPosition, testEuler)

Map.show_map(testmap)
"""