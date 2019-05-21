'''
Created on May 11, 2019

@author: Dave
'''
from MainGui import MainGui
import Controller
import MqttConnection
import Logic
import Map
import CurrentData

if __name__ == '__main__':
    CurrentData.CurrentData()
    connection = MqttConnection.MqttConnection()
    logic = Logic.Logic(connection)
    map = Map.Map()
    controller = Controller.Controller(connection, logic, map)
    gui = MainGui(controller)
