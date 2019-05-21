'''
Created on May 11, 2019

@author: Dave
'''
from gui import MainGui
import Controller
import MqttConnection
import Logic
import Map

if __name__ == '__main__':
    connection = MqttConnection.MqttConnection()
    logic = Logic.Logic(connection)
    map = Map.Map()
    controller = Controller.Controller(connection, logic, map)
    gui = MainGui.MainGui(controller)
