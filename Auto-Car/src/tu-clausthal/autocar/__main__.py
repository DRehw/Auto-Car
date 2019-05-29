"""
Created on May 11, 2019

@author: Dave
"""
import Controller
import CurrentData
import Logic
import Map
import MqttConnection
from MainGui import MainGui
from KeyController2 import start

if __name__ == '__main__':
    CurrentData.CurrentData()
    connection = MqttConnection.MqttConnection()
    logic = Logic.Logic(connection)
    occupancy_map = Map.Map()
    controller = Controller.Controller(connection, logic, occupancy_map)
    start()
    gui = MainGui(controller)
