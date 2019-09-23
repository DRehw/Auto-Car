"""
MqttConnection handles the connection and communication with the MQTT broker, which provides the sensor/lidar data from
the car and receives the steering data.
"""

from json import loads
from time import time
from traceback import print_exc

import paho.mqtt.client as mqtt
from CurrentData import CurrentData


class MqttConnection:

    def __init__(self):
        """
        Constructor
        """
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
        self.show_msg_time = False
        self.last_msg_ts = None
        self.last_ts_msg = None

    @staticmethod
    def get_json_cmd(speed, steer):
        """
        Generates and returns the json string relating to a specific speed and steer command, which is to be sent to
        the car.
        """
        millis = int(round(time() * 1000))
        if speed < 75 or speed > 105:
            speed = 90
        if steer < 60 or steer > 120:
            steer = 90
        return "{{\"vehicle\": \"AADC2016\", \"type\": \"actuator\", \"drive\": {}, \"steering\": {}," \
               " \"brakelight\": 0,\"turnsignalright\": 0,\"turnsignalleft\": 0,\"dimlight\": 0,\"reverselight\": 0," \
               "\"timestamp\": {}}}".format(speed, steer, millis)

    def add_callback_methods(self, on_message=None, on_subscribe=None, on_connect=None, on_disconnect=None):
        """
        Used to register a method to get a callback whenever new data is recevied / a topic is subscribed to /
        the local client connects to the MQTT broker / the local client disconnects from the MQTT broker
        """
        if on_message is not None:
            self.on_message.append(on_message)
        if on_subscribe is not None:
            self.on_subscribe.append(on_subscribe)
        if on_connect is not None:
            self.on_connect.append(on_connect)
        if on_disconnect is not None:
            self.on_disconnect.append(on_disconnect)

    def connect(self, host="localhost"):
        """
        Connects local mqtt-client to mqtt-broker
        """
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
        """
        Helper method for publishing data via MQTT
        """
        if ~self.__is_connecting and self.__is_connected:
            self.client.publish(topic, msg)

    def send_car_command(self, speed, steer):
        """
        Sends/publishes a specific speed and steer command to the car
        """
        self.publish("aadc/rc", MqttConnection.get_json_cmd(speed, steer))

    def disconnect(self):
        """
        Disonnects local mqtt-client from mqtt-broker
        """
        self.client.disconnect()

    def subscribe(self, *topics):
        """
        Helper method for subscribing to topics
        """
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
        """
        Called whenever a new message is received, notifying every registered method (see add_callback_methods)
        """
        if message.topic == "aadc/sensor" and self.show_msg_time:
            cur_ts = int(round(time()*1000))
            cur_ts_msg = CurrentData.get_value_from_tag_from_sensor("timestamp")
            if self.last_msg_ts and self.last_ts_msg:
                act_d = cur_ts-self.last_msg_ts
                sup_d = cur_ts_msg-self.last_ts_msg
                print("{} {}".format(act_d, sup_d))
            self.last_msg_ts = cur_ts
            self.last_ts_msg = cur_ts_msg
        for func in self.on_message:
            try:
                func(client, userdata, message)
            except (Exception) as e:
                print("Function {} not working!".format(str(func).split(" ")[2]))
        if message.topic == "aadc/lidar":
            CurrentData.set_lidar_json(loads(str(message.payload.decode("utf-8"))))
        elif message.topic == "aadc/sensor":
            CurrentData.set_sensor_json(loads(str(message.payload.decode("utf-8"))))
        return


    def __on_subscribe(self, client, userdata, mid, granted_qos):
        """
        Called whenever the response to a subscription attempt is received, notifying every registered method
        (see add_callback_methods)
        """
        if self._last_sub_mid_list is not None:
            if mid in self._last_sub_mid_list:
                self._last_sub_mid_list.remove(mid)
                print("Subscribed successively!")
            else:
                print("Subscription not successful!")
        else:
            print("No previous subscription attempt ?!")

        for func in self.on_subscribe:
            try:
                func(client, userdata, mid, granted_qos)
            except Exception:
                print_exc()
        return


    def __on_connect(self, client, userdata, flags, rc):
        """
        Called whenever the response to a connection attempt is received, or if no response has occurred (rc == 0),
        notifying every registered method (see add_callback_methods)
        """
        if rc != 0:
            print("Could not connect!")
            self.host = None
        else:
            print("Connected successively!")
            self.__is_connected = True

        self.__is_connecting = False

        if self.__is_connected:
            for func in self.on_connect:
                try:
                    func(client, userdata, flags, rc)
                except Exception:
                    print_exc()
        return


    def __on_disconnect(self, client, userdata, rc):
        """
        Called whenever a disconnect has occurred, notifying every registered method (see add_callback_methods)
        """
        if rc != 0:
            print("Unexpected disconnect!")
        else:
            print("Disconnected successively!")
            self.client.loop_stop()

        self.__is_connected = False
        for func in self.on_disconnect:
            try:
                print(func)
                func(client, userdata, rc)
            except Exception:
                print_exc()
        return
