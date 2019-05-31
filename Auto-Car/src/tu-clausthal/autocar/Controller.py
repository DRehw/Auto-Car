"""
Created on May 11, 2019

@author: Dave
"""

import os
import subprocess
import threading
import time
from tkinter import filedialog

import Simulator
from CurrentData import CurrentData
from MqttConnection import MqttConnection
from KeyController import start_loop


class Controller:
    """
    classdocs
    """

    def __init__(self, mqtt_connection, logic, occupancy_map):
        """
        Constructor
        """
        self.gui = None
        self.euler_reseted = False
        self.occupancy_map = occupancy_map
        self.logic = logic
        self.__mqtt_connection = mqtt_connection
        self.__mqtt_connection.add_callback_methods(on_connect=self.subscribe)
        self.logic.set_controller(self)
        return

    def on_window_close(self):
        self.__mqtt_connection.disconnect()
        return

    def subscribe(self, client, userdata, flags, rc):
        self.__mqtt_connection.subscribe("aadc/rc", "aadc/sensor", "aadc/lidar")
        return

    def gui_init(self, gui):
        self.gui = gui
        # start_loop(self)

    def start_cmd_mosq_path(self):
        if os.environ.get('MOSQUITTO_DIR'):
            mosq_path = '"' + os.environ.get('MOSQUITTO_DIR')+'\\"'
            cmd_mosq_pub = "mosquitto_pub -t aadc/rc -h 192.168.50.141 -m \"{}\""\
                .format(MqttConnection.get_json_cmd(90, 90))
            cmd_mosq_sub = "mosquitto_sub -t aadc/ -h 192.168.50.141"
            os.system('start "Send Mosquitto Messages" cmd /k "cd ' + mosq_path
                      + ' && echo ' + cmd_mosq_pub + ' && echo ---------- && echo ' + cmd_mosq_sub + '"')
        else:
            print("Mosquitto not properly installed!")
        return

    def start_mosquitto_async(self):
        """
        Starts Mosquitto and waits until it has started (at max 2 seconds), at which point it
        calls on_mosquittoStart.
        """
        def run_in_thread(on_start):
            mosq_path = '"'+os.environ.get('MOSQUITTO_DIR') + '\mosquitto.exe"'
            subprocess.Popen(mosq_path)
            starting_millis = int(round(time.time() * 1000))
            while True:
                current_millis = int(round(time.time() * 1000))
                if current_millis-starting_millis >= 2000:
                    return
                r = os.popen("wmic process get description").read().strip().split('\n')
                for p in r:
                    if "mosquitto.exe" in p:
                        on_start()
                        return
                time.sleep(0.05)

        if os.environ.get('MOSQUITTO_DIR'):
            thread = threading.Thread(target=run_in_thread, args=(self.on_mosquitto_start,))
            thread.start()
            return thread

    def on_mosquitto_start(self):
        """
        gets called after startMosquittoAsync, when mosquitto has been started
        """
        self.connect_to_mosquitto()
        print("Mosquitto started successively!")
        return

    def on_speed_change_scale(self, val):
        self.logic.set_speed_slider(90-int(val))
        return

    def on_steer_change_scale(self, val):
        self.logic.set_steer_slider(90+int(val))
        return

    def stop_cmd_btn(self):
        self.logic.set_stop(~self.logic.get_stop())
        if self.logic.get_stop():
            self.gui.stop_btn_set_color("red")
        else:
            self.gui.stop_btn_set_color("SystemButtonFace")

    def show_map_btn(self):
        self.occupancy_map.show_map()

    def reset_euler_btn(self):
        euler = CurrentData.get_value_from_tag_from_sensor("euler")
        self.occupancy_map.calc_constant(euler)
        self.euler_reseted = True

    def toggle_manual_control_button(self):
        # disable autopilot
        if self.logic.get_autopilot_control():
            self.logic.set_autopilot_control(not self.logic.get_autopilot_control())
            print("Autopilot disabled")
            self.gui.autopilot_control_btn_set_color("SystemButtonFace")
        # switch manual control
        self.logic.set_manual_control(~self.logic.get_manual_control())
        if self.logic.get_manual_control():
            print("Switched to manual control!")
            self.gui.manual_control_btn_set_color("red")
        else:
            print("Switched to logic mode!")
            self.gui.manual_control_btn_set_color("SystemButtonFace")
        return

    def toggle_autopilot_button(self):
        # disable manual control
        if self.logic.get_manual_control():
            self.logic.set_manual_control(not self.logic.get_manual_control())
            print("Manual control disabled")
            self.gui.manual_control_btn_set_color("SystemButtonFace")
        # switch autopilot
        self.logic.set_autopilot_control(not self.logic.get_autopilot_control())
        if self.logic.get_autopilot_control():
            print("Autopilot enabled")
            self.gui.autopilot_control_btn_set_color("red")
        else:
            print("Autopilot disabled")
            self.gui.autopilot_control_btn_set_color("SystemButtonFace")

    def connect_to_car_btn(self):
        if "Mobilitaetslabor" in str(subprocess.check_output("netsh wlan show interfaces")):
            self.__mqtt_connection.connect("192.168.50.141")
        else:
            print("Not connected to the right Wifi!")
        return
    
    def connect_to_mosquitto(self):
        self.__mqtt_connection.connect()
        return

    def send_test_btn(self):
        self.__mqtt_connection.publish("aadc/sensor", '{"vehicle": "AADC2016", "type": "sensor", "us": [423, 423, 423, 194, 220, 169, 6, 253, 162, 114], "wheel": [1, 19444, 0, 17200], "euler": [114.18, 1.65, 179.36], "acceleration": [-0.01, -0.23, -9.75], "position": [0, 0, 0], "temp": 23.62, "motorctr": 600,"timestamp": 1551853635446}')
        self.__mqtt_connection.publish("aadc/lidar", '{"vehicle": "AADC2016", "type": "sensor", "drive": 83, "steering": 113, "pcl": [[15, 352.234375, 1204.75], [15, 354.171875, 1204.75], [15, 356.1875, 1192.0], [15, 358.109375, 1184.0], [15, 0.0625, 1186.5], [15, 2.0, 1182.25], [15, 3.890625, 1186.5], [15, 5.796875, 1187.75], [15, 7.765625, 1185.25], [15, 9.71875, 1183.75], [15, 11.578125, 1189.75], [15, 13.5, 1200.75], [15, 15.4375, 1212.75], [15, 17.421875, 1218.5], [15, 19.328125, 1237.0], [15, 21.234375, 1253.25], [15, 23.09375, 1266.5], [15, 25.046875, 1290.25], [15, 26.921875, 1310.25], [15, 28.921875, 1339.75], [15, 30.8125, 1363.0], [15, 32.671875, 1390.75], [15, 34.640625, 1424.75], [15, 36.8125, 1456.25], [15, 38.734375, 1491.75], [15, 40.671875, 1530.0], [15, 42.578125, 1576.0], [15, 44.515625, 1627.25], [15, 46.40625, 1681.75], [15, 48.328125, 1740.75], [15, 50.28125, 1804.0], [15, 52.203125, 1870.0], [15, 54.109375, 1950.0], [15, 56.0625, 1989.25], [15, 58.03125, 1943.25], [15, 59.578125, 1901.0], [15, 61.46875, 1861.75], [15, 63.421875, 1823.0], [15, 65.390625, 1795.25], [15, 67.265625, 1761.5], [15, 69.1875, 1808.0], [15, 74.515625, 4022.5], [15, 76.40625, 4625.5], [15, 78.296875, 4741.25], [15, 80.21875, 4741.25], [15, 82.5, 4709.25], [15, 84.453125, 4690.0], [15, 86.40625, 4685.75], [15, 88.328125, 4654.5], [15, 90.296875, 4650.25], [15, 92.25, 4635.75], [15, 94.796875, 1548.0], [15, 97.28125, 963.75], [15, 99.859375, 730.75], [15, 102.09375, 592.25], [12, 104.25, 539.5], [15, 106.328125, 524.25], [15, 108.1875, 533.5], [15, 110.140625, 539.0], [15, 112.015625, 546.5], [15, 113.78125, 554.25], [15, 115.859375, 563.0], [15, 117.609375, 572.25], [15, 119.46875, 579.75], [15, 121.34375, 592.25], [15, 123.28125, 605.75], [15, 125.234375, 619.25], [15, 135.015625, 151.25], [14, 136.953125, 154.25], [8, 139.921875, 144.75], [12, 143.96875, 144.5], [15, 138.953125, 2166.5], [15, 140.9375, 2112.0], [9, 159.5625, 207.5], [15, 154.546875, 1837.5], [15, 156.6875, 1805.25], [14, 158.625, 1743.0], [15, 164.5, 1705.0], [15, 173.875, 151.0], [8, 177.25, 204.5], [15, 179.203125, 200.25], [15, 181.15625, 197.75], [15, 187.546875, 1692.0], [15, 199.125, 1796.75], [15, 200.984375, 1809.0], [15, 203.078125, 1801.75], [15, 211.078125, 1456.0], [15, 213.0625, 1353.5], [15, 215.03125, 1281.75], [15, 217.09375, 1214.75], [15, 219.0625, 1177.25], [15, 225.046875, 1024.25], [15, 227.078125, 994.5], [15, 228.96875, 966.0], [15, 230.859375, 937.5], [15, 232.84375, 908.5], [15, 234.84375, 890.0], [15, 236.828125, 868.75], [15, 238.75, 848.25], [15, 240.75, 811.0], [15, 244.640625, 813.0], [15, 246.671875, 786.0], [15, 248.59375, 761.25], [15, 250.453125, 798.5], [15, 252.578125, 762.75], [15, 254.53125, 749.25], [15, 256.453125, 743.5], [15, 258.3125, 736.25], [15, 260.375, 733.25], [15, 262.296875, 727.5], [15, 264.109375, 724.5], [15, 266.0625, 722.5], [15, 267.96875, 719.5], [15, 270.0, 718.75], [15, 271.890625, 721.25], [15, 273.890625, 722.5], [15, 275.859375, 724.0], [15, 277.96875, 728.25], [15, 279.8125, 730.5], [15, 281.796875, 736.25], [15, 283.65625, 741.0], [15, 285.640625, 749.25], [15, 287.640625, 756.75], [15, 289.40625, 764.25], [15, 291.375, 774.5], [15, 293.328125, 787.25], [15, 295.265625, 797.0], [15, 297.09375, 808.75], [15, 299.015625, 822.25], [15, 300.671875, 838.5], [15, 302.6875, 856.0], [15, 304.53125, 878.25], [15, 306.4375, 897.5], [15, 308.265625, 918.0], [15, 310.1875, 948.25], [15, 312.109375, 977.0], [15, 313.96875, 1012.0], [15, 315.828125, 1044.75], [15, 317.71875, 1084.5], [15, 319.53125, 1127.75], [15, 321.421875, 1180.5], [15, 323.5, 1237.5], [15, 325.40625, 1298.75], [15, 327.265625, 1334.0], [15, 329.265625, 1307.75], [15, 331.203125, 1282.25], [15, 333.140625, 1255.75], [15, 335.125, 1240.75], [15, 337.078125, 1227.0], [15, 339.0, 1212.25], [15, 341.0, 1192.5], [15, 342.953125, 1181.0], [15, 344.875, 1173.5], [15, 346.8125, 1161.25], [15, 348.71875, 1161.25]], "us": [189, 423, 106, 107, 56, 55, 36, 63, 122, 49], "wheel": [0, 8748, 0, 12164], "euler": [-133.2, 0.48, 177.51], "acceleration": [-0.16, 0.37, -9.19], "position": [0, 0, 0], "temp": 22.89, "motorctr": 796, "timestamp": 1534649331254}')
        return

    def path_change_record_btn(self):
        location = filedialog.asksaveasfilename(filetypes=(("text files", ".txt"),), defaultextension='.txt')
        self.gui.set_record_path(location)
        return

    def show_autopilot_speed_steer(self, speed, steer):
        self.gui.set_auto_speed_label_text(speed)
        self.gui.set_auto_steer_label_text(steer)

    def path_change_play_btn(self):
        location = filedialog.askopenfilename(filetypes=(("text files", ".txt"),))
        self.gui.set_play_path(location)
        return

    def record_btn(self):
        loc = self.gui.get_record_path()
        if len(loc) > 4:
            if not ".txt" == loc[-4:]:
                loc += ".txt"
            Simulator.start_recording(loc)
        return

    def stop_recording_btn(self):
        Simulator.stop_recording()
        return

    def play_btn(self):
        path = self.gui.get_play_path()
        Simulator.start_playback(path, self.__mqtt_connection)
        return

    def stop_playing_btn(self):
        Simulator.stop_playback()
        return

    def set_speed(self, speed):
        self.gui.speed_scale_set(speed)

    def set_steer(self, steer):
        self.gui.steer_scale_set(steer)
