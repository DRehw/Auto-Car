'''
Created on May 11, 2019

@author: Dave
'''
import Controller
import CurrentData
import Logic
import Map
import MqttConnection
from MainGui import MainGui

if __name__ == '__main__':
    CurrentData.CurrentData()
    connection = MqttConnection.MqttConnection()
    logic = Logic.Logic(connection)
    map = Map.Map()
    controller = Controller.Controller(connection, logic, map)
    gui = MainGui(controller)
