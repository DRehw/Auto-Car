'''
Created on May 11, 2019

@author: Dave
'''

import tkinter as tk
import Controller
import Map

class MainGui():
    '''
    classdocs
    '''

    def __init__(self, controller):
        '''
        Constructor
        '''
        self.controller = controller
        self.Map = Map
        self.controller.guiInit(self)
        self.window = tk.Tk()
        self.window.title("Auto-Car Debug")
        self.window.bind("<KeyRelease>", self.key_release)
        self.window.bind("<KeyPress>", self.key_press)
        self.window.option_add("*font", "Helvetica 14")
        infoFrame = tk.Frame(self.window)
        infoFrame.grid(row=0,column=0, padx=(10,10),pady=(10,10))
        buttonFrame = tk.Frame(self.window)
        buttonFrame.grid(row=0,column=1, padx=(10,10),pady=(10,10), sticky=tk.N)

        self.window.columnconfigure(0,weight=1)
        self.window.columnconfigure(1,weight=1)

        self.speedScale = tk.Scale(infoFrame, from_=15, to=-15, orient = tk.VERTICAL, label="Speed", width=20, length=300, command=self.controller.onSpeedChange)
        self.speedScale.set(0)
        self.speedScale.bind("<ButtonRelease-1>", self.speed_scale_mouse_release)
        self.speedScale.grid(row=0,column=1, columnspan=1)
        self.steerScale = tk.Scale(infoFrame, from_=-30, to=30, orient = tk.HORIZONTAL, label="Steering", width=20, length=300, command=self.controller.onSteerChange)
        self.steerScale.set(0)
        self.steerScale.bind("<ButtonRelease-1>", self.steer_scale_mouse_release)
        self.steerScale.grid(row=0,column=0,columnspan=1)
        tk.Button(infoFrame,text="Send Command", command=self.sendMQTT).grid(row=2,column=0,padx=(0,0),sticky=tk.W+tk.E)
        tk.Button(infoFrame,text="Stop", command=self.resetSlider).grid(row=2,column=1,padx=(0,0),sticky=tk.W+tk.E)
    
        tk.Button(buttonFrame, text="Connect to local Broker", command=self.connectToLocalBroker).grid(row=1,column=0,sticky=tk.W+tk.E+tk.N,pady=(5,5))
        tk.Button(buttonFrame, text="Connect to Car Broker", command=self.connectToCar).grid(row=1,column=1,sticky=tk.W+tk.E,pady=(5,5))
        tk.Button(buttonFrame, text="Subscribe to 'aadc/rc','aadc/sensor','aadc/lidar'", command=self.subscribe).grid(row=2,column=0,columnspan=2,sticky=tk.W+tk.E,pady=(5,5))
        tk.Button(buttonFrame, text="Open Cmd at Mosquitto path", command=self.cmdSend).grid(row=3,column=0,columnspan=2,sticky=tk.W+tk.E,pady=(5,5))
        tk.Button(buttonFrame, text="Send test messages", command=self.controller.sendTest).grid(row=4,column=0,columnspan=2,sticky=tk.W+tk.E,pady=(5,5))
        tk.Button(buttonFrame, text="Show Map", command=self.controller.show_map_button).grid(row=6, column=0, sticky=tk.W + tk.E + tk.N,pady=(5, 5))
        tk.Button(buttonFrame, text="Reset Euler", command=self.controller.reset_euler_button).grid(row=6, column=1, sticky=tk.W + tk.E + tk.N, pady=(5, 5))

        self.ignoreLogicButon = tk.Button(buttonFrame, text="Ignore Logic", command=self.controller.toggleIgnoreLogicButton, bg="red")
        self.ignoreLogicButon.grid(row=5,column=0,columnspan=2,sticky=tk.W+tk.E+tk.S,pady=(5,5))
        self.window.mainloop()

    def speed_scale_mouse_release(self, event):
        self.speedScale.set(0)
        self.controller.sendCommand()

    def steer_scale_mouse_release(self, event):
        self.steerScale.set(0)
        self.controller.sendCommand()

    def key_press(self, event):
        print(event.keysym)
        print(event.type)

    def key_release(self, event):
        print(event.keysym)
        print(event.type)

    def changeIgnoreLogicBColor(self, color):
        self.ignoreLogicButon.configure(bg=color)
    
    def sendMQTT(self):
        self.controller.sendCommand()
        return
    
    def resetSlider(self):
        #print("Resetting slider!")
        self.speedScale.set(0)
        self.steerScale.set(0)
        self.controller.sendCommand()
        #print("Slider resetted")
        return
    
    def connectToLocalBroker(self):
        self.controller.startMosquittoAsync()
        return
    
    def connectToCar(self):
        self.controller.connectToCar()
        return
    
    def subscribe(self):
        self.controller.subscribe()
        return
    
    def cmdSend(self):
        self.controller.startCmdMosqPath()
        return
