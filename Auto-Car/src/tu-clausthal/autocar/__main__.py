"""
Created on May 11, 2019

@author: Dave
"""
import Controller
import CurrentData
import Logic
from MapTest import MapTest
import MqttConnection
from MainGui import MainGui
from Decorator import *


@debug_only
def debug_print():
    print("==========DEBUG MODE==========")


if __name__ == '__main__':
    debug_print()
    CurrentData.CurrentData()
    connection = MqttConnection.MqttConnection()
    logic = Logic.Logic(connection)
    occupancy_map = MapTest()
    controller = Controller.Controller(connection, logic, occupancy_map)
    gui = MainGui(controller, occupancy_map)
