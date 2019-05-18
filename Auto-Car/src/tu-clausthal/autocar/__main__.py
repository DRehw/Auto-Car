'''
Created on May 11, 2019

@author: Dave
'''
from gui import MainGui
import Controller
import MqttConnection
import Logic

if __name__ == '__main__':
    connection = MqttConnection.MqttConnection()
    logic = Logic.Logic(connection)
    controller = Controller.Controller(connection, logic)
    gui = MainGui.MainGui(controller)
