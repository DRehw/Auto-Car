'''
Created on May 11, 2019

@author: Dave
'''
from gui import MainGui
import Controller
import subprocess
import os

if __name__ == '__main__':
    controller = Controller.Controller()
    gui = MainGui.MainGui(controller)