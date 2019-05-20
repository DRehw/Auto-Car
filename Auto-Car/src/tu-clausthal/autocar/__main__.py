'''
Created on May 11, 2019

@author: Dave
'''
from gui import MainGui
import Controller
import subprocess
import os
import Map

if __name__ == '__main__':
    occupancy_map = Map.Map()
    controller = Controller.Controller(occupancy_map)
    gui = MainGui.MainGui(controller)
