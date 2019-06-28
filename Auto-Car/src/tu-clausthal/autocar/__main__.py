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
import test_papa_pytest

if __name__ == '__main__':
    CurrentData.CurrentData()
    connection = MqttConnection.MqttConnection()
    logic = Logic.Logic(connection)
    occupancy_map = Map.Map()
    controller = Controller.Controller(connection, logic, occupancy_map)
    # test_papa_pytest.set_refs(connection, logic, occupancy_map, controller)
    gui = MainGui(controller)


