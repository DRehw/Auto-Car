'''
Created on May 12, 2019

@author: Dave
'''

import math
import sensor
from CurrentData import CurrentData


def isObjectInRedZoneLidar(lidarData):
    for dataset in lidarData:
        if dataset[0] > 10 and (dataset[1] < 20.0 or dataset[1] > 340.0) and dataset[2]*math.cos(math.radians(dataset[1])) < 1000.0:
            #print("{}, {}, {}".format(dataset[0], dataset[1], dataset[2]))
            return True
    return False

def isObjectInRedZoneUS():
    usData = CurrentData.get_value_from_tag_from_sensor("us")
    usData = usData[1:3]
    for dist in usData:
        if dist > 2 and dist < 100:
            #print(str(usData) + "True")
            return True
    #print(str(usData) + "False")
    return False
def defineRedZoneDynamic(currentSpeed):
    redZone = 100
    maxSpeed = 12
    minSpeed = 6
    maxZone = 120
    minZone = 50
    speed = convertSpeed(currentSpeed)

    if speed >= maxSpeed:
        redZone = maxZone
    elif speed <= minSpeed:
        redZone = minZone
    else:
        redZone = minZone + (maxZone - minZone)/((maxSpeed - minSpeed)/(speed - minSpeed))
    #print(redZone)
    return redZone

def defineYellowZoneDynamic(currentSpeed):
    redZone = 150
    maxSpeed = 12
    minSpeed = 6
    maxZone = 300
    minZone = 100
    speed = convertSpeed(currentSpeed)

    if speed >= maxSpeed:
        redZone = maxZone
    elif speed <= minSpeed:
        redZone = minZone
    else:
        redZone = minZone + (maxZone - minZone)/((maxSpeed - minSpeed)/(speed - minSpeed))
    #print(redZone)
    return redZone

def isObjectInRedZoneUSDynamic(currentSpeed):
    usData = CurrentData.get_value_from_tag_from_sensor("us")
    usData = usData[1:3]
    for dist in usData:
        if dist > 2 and dist < defineRedZoneDynamic(currentSpeed):
            #print(str(usData) + "True")
            return True
        else:
          return False
    #print(str(usData) + "False")


def isObjectInYellowZoneUSDynamic(currentSpeed):
    usData = CurrentData.get_value_from_tag_from_sensor("us")
    usData = usData[1:3]
    for dist in usData:
        if dist > 2 and dist < defineYellowZoneDynamic(currentSpeed):
            #print(str(usData) + "True")
            return True
        else:
          return False
    #print(str(usData) + "False")

def convertSpeed(speed):
    speed = 15 - (speed - 75)
    return speed
