'''
Created on May 12, 2019

@author: Dave
'''

import math

def isObjectInRedZoneLidar(lidarData):
    for dataset in lidarData:
        if dataset[0] > 10 and (dataset[1] < 20.0 or dataset[1] > 340.0) and dataset[2]*math.cos(math.radians(dataset[1])) < 1000.0:
            print("{}, {}, {}".format(dataset[0], dataset[1], dataset[2]))
            return True
    return False