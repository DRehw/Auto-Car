"""

"""
from json import loads
from time import time

import paho.mqtt.client as mqtt
from CurrentData import CurrentData


class MqttConnection:
    """
    Doc
    """

    def __init__(self):
        self.client = mqtt.Client("Auto-Car-Client")
        self.__is_connected = False
        self.__is_connecting = False
        self._last_sub_mid_list = []
        self.host = None
        self.on_message = []
        self.on_subscribe = []
        self.on_connect = []
        self.on_disconnect = []
        self.client.on_message = self.__on_message
        self.client.on_subscribe = self.__on_subscribe
        self.client.on_connect = self.__on_connect
        self.client.on_disconnect = self.__on_disconnect

    @staticmethod
    def get_json_cmd(speed, steer):
        millis = int(round(time() * 1000))
        if speed < 60 or speed > 120:
            speed = 90
        if steer < 60 or steer > 120:
            steer = 90
        return "{{\"vehicle\": \"AADC2016\", \"type\": \"actuator\", \"drive\": {}, \"steering\": {}, \"brakelight\": 0,\"turnsignalright\": 0,\"turnsignalleft\": 0,\"dimlight\": 0,\"reverselight\": 0,\"timestamp\": {}}}".format(
            speed, steer, millis)

    def add_callback_methods(self, on_message=None, on_subscribe=None, on_connect=None, on_disconnect=None):
        if on_message is not None:
            self.on_message.append(on_message)
        if on_subscribe is not None:
            self.on_subscribe.append(on_subscribe)
        if on_connect is not None:
            self.on_connect.append(on_connect)
        if on_disconnect is not None:
            self.on_disconnect.append(on_disconnect)

    def connect(self, host="localhost"):
        if ~self.__is_connecting and ~self.__is_connected:
            print("Trying to connect")
            self.__is_connecting = True
            self.host = host
            self.client.loop_start()
            self.client.connect_async(host)

    def is_connected(self):
        return self.__is_connected

    def is_connecting(self):
        return self.__is_connecting

    def publish(self, topic, msg):
        if ~self.__is_connecting and self.__is_connected:
            self.client.publish(topic, msg)

    def send_car_command(self, speed, steer):
        print("Sending command")
        self.publish("aadc/rc", MqttConnection.get_json_cmd(speed, steer))

    def disconnect(self):
        self.client.disconnect()

    def subscribe(self, *topics):
        if ~self.__is_connecting and self.__is_connected:
            topics = list(topics)
            for i in range(len(topics)):
                topics[i] = (topics[i], 0)

            string = "Subscribing to: "
            for t in topics:
                string += t[0] + ", "
            print(string[:-2])

            a = self.client.subscribe(topics)
            self._last_sub_mid_list.append(a[1])
            return

    def get_host(self):
        return self.host

    def __on_message(self, client, userdata, message):
        for func in self.on_message:
            try:
                func(client, userdata, message)
            except (Exception) as e:
                print("Function {} not working!".format(str(func).split(" ")[2]))
        if message.topic == "aadc/lidar":
            CurrentData.set_lidar_json(loads(str(message.payload.decode("utf-8"))))
        elif message.topic == "aadc/sensor":
            print(str(message.payload.decode("utf-8")))
            CurrentData.set_sensor_json(loads(str(message.payload.decode("utf-8"))))
        return

    def __on_subscribe(self, client, userdata, mid, granted_qos):
        if self._last_sub_mid_list is not None:
            if mid in self._last_sub_mid_list:
                self._last_sub_mid_list.remove(mid)
                print("Subscribed successively!")
            else:
                print("Subscription not successful!")
        else:
            print("No previous subscription attempt ?!")

        for func in self.on_subscribe:
            func(client, userdata, mid, granted_qos)
        return

    def __on_connect(self, client, userdata, flags, rc):
        if rc != 0:
            print("Could not connect!")
            self.host = None
        else:
            print("Connected successively!")
            self.__is_connected = True

        self.__is_connecting = False

        if self.__is_connected:
            for func in self.on_connect:
                func(client, userdata, flags, rc)
        return

    def __on_disconnect(self, client, userdata, rc):
        if rc != 0:
            print("Unexpected disconnect!")
        else:
            print("Disconnected successively!")
            self.client.loop_stop()

        self.__is_connected = False

        for func in self.on_disconnect:
            func(client, userdata, rc)
        return
