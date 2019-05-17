'''
Created on May 11, 2019

@author: Dave
'''

import mqtt.mqttlib as mqttl
import subprocess
import threading
import os
import time
import sensor
import zones
import json

class Controller():
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self.currentSpeed = 90
        self.currentSteer = 90
        self.ignoreLogic = False
        self.lidarNew = False
        self.sensorNew = False
        self.lidarData = None
        self.sensorData = None
        self.getCmdTimeStamp = 0
        self.sendCmdTimeStamp = 0
        self.client = mqttl.getClient("Client", self.on_connect, self.on_subscribe, self.on_message, self.on_disconnect)
        return
    
    def guiInit(self, gui):
        self.gui = gui
    
    def toggleIgnoreLogicButton(self):
        self.ignoreLogic = ~self.ignoreLogic
        if self.ignoreLogic:
            print("Ignoring Logic!")
            self.gui.changeIgnoreLogicBColor("green")
        else:
            print("Stopped ignoring Logic")
            self.gui.changeIgnoreLogicBColor("red")
        return
    
    def logic(self):
        #print("Logic")
        if ~self.ignoreLogic:
            if False:
            #if self.lidarNew and self.sensorNew:
                if zones.isObjectInRedZoneLidar(self.lidarData):
                    self.gui.resetSlider()
                else:
                    self.sendCommand()
            else:
                if zones.isObjectInRedZoneUSDynamic(self.sensorData, self.currentSpeed):
                    self.gui.resetSlider()
                else:
                    self.sendCommand()
        else:
            self.sendCommand()
        self.lidarNew = False
        self.sensorNew = False
        return
    
    def connectToCar(self):
        if "Mobilitaetslabor" in str(subprocess.check_output("netsh wlan show interfaces")):
            mqttl.connect(self.client, "192.168.50.141")
        else:
            print("Not connected to the right Wifi!")
        return
    
    def connectToMoquitto(self):
        mqttl.connect(self.client, "127.0.0.1")
        return
    
    def sendCommand(self):
        mqttl.sendCmd(self.client, mqttl.getJSONCmd(self.currentSpeed, self.currentSteer))
        return
    
    def on_message(self, client, userdata, message):
        
        #print("Message received! Topic: " + message.topic)
        if message.topic == "aadc/lidar":
            self.lidarNew = True
            #self.lidarData = sensor.parseAADCData(str(message.payload.decode("utf-8")), "pcl")
            #self.lidarData = sensor.parseLidarData(str(message.payload.decode("utf-8")))
            self.lidarData = sensor.getJsonDataFromTag(str(message.payload.decode("utf-8")), "pcl")
        elif message.topic == "aadc/sensor":
            self.sensorNew = True
            self.sensorData = str(message.payload.decode("utf-8"))
            millis = int(round(time.time() * 1000))
            #print("Time since last sensor message: " + str(millis-self.getCmdTimeStamp))
            self.getCmdTimeStamp = int(round(time.time() * 1000))
            #self.gpsData = sensor.getJsonDataFromTag(self.sensorData, "position")
        elif message.topic == "aadc/rc":
            #print("")
            pass
            #print("message received " ,str(message.payload.decode("utf-8")))
        if self.sensorNew or self.lidarNew:
            #print("Logic")
            self.logic()
        return
    
    def on_subscribe(self, client, userdata, mid, granted_qos):
        if self.mid != None:
            if self.mid == mid:
                print("Subscribed successively!")
            else:
                print("Subscription not successful!")
        else:
            print("No previous subscription attempt ?!")
        return
    
    def on_connect(self, client, userdata, flags, rc):
        if rc != 0:
            print("Could not connect!")
        else:
            print("Connected successively!")
        return
    
    def on_disconnect(self, client, userdata, rc):
        if rc != 0:
            print("Unexpected disconnect!")
        else:
            print("Disconnected successively!")
    
    def onSpeedChange(self, val):
        self.currentSpeed = 90 - int(val)
        return
    
    def onSteerChange(self, val):
        self.currentSteer = 90 + int(val)
        return
    
    def startCmdMosqPath(self):
        mosqPath = '"' + os.environ.get('MOSQUITTO_DIR')+'\\"'
        cmdMosqPub = "mosquitto_pub -t aadc/rc -h 192.168.50.141 -m \"{}\"".format(mqttl.getJSONCmd(90,90))
        cmdMosqSub = "mosquitto_sub -t aadc/ -h 192.168.50.141"
        os.system('start "Send Mosquitto Messages" cmd /k "cd ' + mosqPath + ' && echo ' + cmdMosqPub + ' && echo ---------- && echo ' + cmdMosqSub + '"')
        return 
    
    def startMosquittoAsync(self):
        '''
        Starts Mosquitto and waits until it has started (at max 2 seconds), at which point it
        calls on_mosquittoStart.
        '''
        def runInThread(onStart):
            mosqPath = '"'+os.environ.get('MOSQUITTO_DIR')+'\mosquitto.exe"'
            subprocess.Popen(mosqPath)
            startingMillis=int(round(time.time() * 1000))
            while True:
                currentMillis = int(round(time.time() * 1000))
                if currentMillis-startingMillis >= 2000:
                    return
                r = os.popen("wmic process get description").read().strip().split('\n')
                for p in r:
                    if "mosquitto.exe" in p:
                        onStart()
                        return
                time.sleep(0.05)
                    
        thread = threading.Thread(target=runInThread, args=(self.on_mosquittoStart,))
        thread.start()
        return thread
    
    def on_mosquittoStart(self):
        '''
        gets called after startMosquittoAsync, when mosquitto has been started
        '''
        self.connectToMoquitto()
        print("Mosquitto started successively!")
        return
    
    def subscribe(self):
        self.mid = mqttl.subscribe(self.client, "aadc/rc", "aadc/sensor", "aadc/lidar")
        return
    
    def sendTest(self):
        self.client.publish("aadc/sensor", '{"vehicle": "AADC2016", "type": "sensor", "us": [423, 423, 423, 194, 220, 169, 6, 253, 162, 114], "wheel": [1, 19444, 0, 17200], "euler": [114.18, 1.65, 179.36], "acceleration": [-0.01, -0.23, -9.75], "position": [0, 0, 0], "temp": 23.62, "motorctr": 600,"timestamp": 1551853635446}')
        self.client.publish("aadc/lidar", '{"vehicle": "AADC2016", "type": "sensor", "drive": 83, "steering": 113, "pcl": [[15, 352.234375, 1204.75], [15, 354.171875, 1204.75], [15, 356.1875, 1192.0], [15, 358.109375, 1184.0], [15, 0.0625, 1186.5], [15, 2.0, 1182.25], [15, 3.890625, 1186.5], [15, 5.796875, 1187.75], [15, 7.765625, 1185.25], [15, 9.71875, 1183.75], [15, 11.578125, 1189.75], [15, 13.5, 1200.75], [15, 15.4375, 1212.75], [15, 17.421875, 1218.5], [15, 19.328125, 1237.0], [15, 21.234375, 1253.25], [15, 23.09375, 1266.5], [15, 25.046875, 1290.25], [15, 26.921875, 1310.25], [15, 28.921875, 1339.75], [15, 30.8125, 1363.0], [15, 32.671875, 1390.75], [15, 34.640625, 1424.75], [15, 36.8125, 1456.25], [15, 38.734375, 1491.75], [15, 40.671875, 1530.0], [15, 42.578125, 1576.0], [15, 44.515625, 1627.25], [15, 46.40625, 1681.75], [15, 48.328125, 1740.75], [15, 50.28125, 1804.0], [15, 52.203125, 1870.0], [15, 54.109375, 1950.0], [15, 56.0625, 1989.25], [15, 58.03125, 1943.25], [15, 59.578125, 1901.0], [15, 61.46875, 1861.75], [15, 63.421875, 1823.0], [15, 65.390625, 1795.25], [15, 67.265625, 1761.5], [15, 69.1875, 1808.0], [15, 74.515625, 4022.5], [15, 76.40625, 4625.5], [15, 78.296875, 4741.25], [15, 80.21875, 4741.25], [15, 82.5, 4709.25], [15, 84.453125, 4690.0], [15, 86.40625, 4685.75], [15, 88.328125, 4654.5], [15, 90.296875, 4650.25], [15, 92.25, 4635.75], [15, 94.796875, 1548.0], [15, 97.28125, 963.75], [15, 99.859375, 730.75], [15, 102.09375, 592.25], [12, 104.25, 539.5], [15, 106.328125, 524.25], [15, 108.1875, 533.5], [15, 110.140625, 539.0], [15, 112.015625, 546.5], [15, 113.78125, 554.25], [15, 115.859375, 563.0], [15, 117.609375, 572.25], [15, 119.46875, 579.75], [15, 121.34375, 592.25], [15, 123.28125, 605.75], [15, 125.234375, 619.25], [15, 135.015625, 151.25], [14, 136.953125, 154.25], [8, 139.921875, 144.75], [12, 143.96875, 144.5], [15, 138.953125, 2166.5], [15, 140.9375, 2112.0], [9, 159.5625, 207.5], [15, 154.546875, 1837.5], [15, 156.6875, 1805.25], [14, 158.625, 1743.0], [15, 164.5, 1705.0], [15, 173.875, 151.0], [8, 177.25, 204.5], [15, 179.203125, 200.25], [15, 181.15625, 197.75], [15, 187.546875, 1692.0], [15, 199.125, 1796.75], [15, 200.984375, 1809.0], [15, 203.078125, 1801.75], [15, 211.078125, 1456.0], [15, 213.0625, 1353.5], [15, 215.03125, 1281.75], [15, 217.09375, 1214.75], [15, 219.0625, 1177.25], [15, 225.046875, 1024.25], [15, 227.078125, 994.5], [15, 228.96875, 966.0], [15, 230.859375, 937.5], [15, 232.84375, 908.5], [15, 234.84375, 890.0], [15, 236.828125, 868.75], [15, 238.75, 848.25], [15, 240.75, 811.0], [15, 244.640625, 813.0], [15, 246.671875, 786.0], [15, 248.59375, 761.25], [15, 250.453125, 798.5], [15, 252.578125, 762.75], [15, 254.53125, 749.25], [15, 256.453125, 743.5], [15, 258.3125, 736.25], [15, 260.375, 733.25], [15, 262.296875, 727.5], [15, 264.109375, 724.5], [15, 266.0625, 722.5], [15, 267.96875, 719.5], [15, 270.0, 718.75], [15, 271.890625, 721.25], [15, 273.890625, 722.5], [15, 275.859375, 724.0], [15, 277.96875, 728.25], [15, 279.8125, 730.5], [15, 281.796875, 736.25], [15, 283.65625, 741.0], [15, 285.640625, 749.25], [15, 287.640625, 756.75], [15, 289.40625, 764.25], [15, 291.375, 774.5], [15, 293.328125, 787.25], [15, 295.265625, 797.0], [15, 297.09375, 808.75], [15, 299.015625, 822.25], [15, 300.671875, 838.5], [15, 302.6875, 856.0], [15, 304.53125, 878.25], [15, 306.4375, 897.5], [15, 308.265625, 918.0], [15, 310.1875, 948.25], [15, 312.109375, 977.0], [15, 313.96875, 1012.0], [15, 315.828125, 1044.75], [15, 317.71875, 1084.5], [15, 319.53125, 1127.75], [15, 321.421875, 1180.5], [15, 323.5, 1237.5], [15, 325.40625, 1298.75], [15, 327.265625, 1334.0], [15, 329.265625, 1307.75], [15, 331.203125, 1282.25], [15, 333.140625, 1255.75], [15, 335.125, 1240.75], [15, 337.078125, 1227.0], [15, 339.0, 1212.25], [15, 341.0, 1192.5], [15, 342.953125, 1181.0], [15, 344.875, 1173.5], [15, 346.8125, 1161.25], [15, 348.71875, 1161.25]], "us": [189, 423, 106, 107, 56, 55, 36, 63, 122, 49], "wheel": [0, 8748, 0, 12164], "euler": [-133.2, 0.48, 177.51], "acceleration": [-0.16, 0.37, -9.19], "position": [0, 0, 0], "temp": 22.89, "motorctr": 796, "timestamp": 1552649331254}')
        return
        