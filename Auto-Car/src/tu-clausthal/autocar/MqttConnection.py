"""

"""
import paho.mqtt.client as mqtt
from time import time


class MqttConnection:
    """
    Doc
    """

    def __init__(self):
        self.client = mqtt.Client("Auto-Car-Client")
        self._is_connected = False
        self._is_connecting = False
        self._last_sub_mid_list = []
        self.host = None
        self.on_message = None
        self.on_subscribe = None
        self.on_connect = None
        self.on_disconnect = None
        self.on_new_data = None
        self.client.on_message = self._on_message
        self.client.on_subscribe = self._on_subscribe
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect

    @staticmethod
    def get_json_cmd(speed, steer):
        millis = int(round(time() * 1000))
        if speed < 60 or speed > 120:
            speed = 90
        if steer < 60 or steer > 120:
            steer = 90
        return "{{\"vehicle\": \"AADC2016\", \"type\": \"actuator\", \"drive\": {}, \"steering\": {}, \"brakelight\": 0,\"turnsignalright\": 0,\"turnsignalleft\": 0,\"dimlight\": 0,\"reverselight\": 0,\"timestamp\": {}}}".format(
            speed, steer, millis)

    def set_callback_methods(self, on_message=None, on_subscribe=None, on_connect=None, on_disconnect=None, on_new_data=None):
        if on_message is not None:
            self.on_message = on_message
        if on_subscribe is not None:
            self.on_subscribe = on_subscribe
        if on_connect is not None:
            self.on_connect = on_connect
        if on_disconnect is not None:
            self.on_disconnect = on_disconnect
        if on_new_data is not None:
            self.on_new_data = on_new_data

    def connect(self, host="localhost"):
        if ~self._is_connecting and ~self._is_connected:
            self._is_connecting = True
            self.host = host
            self.client.loop_start()
            self.client.connect_async(host)

    def is_connected(self):
        return self._is_connected

    def is_connecting(self):
        return self._is_connecting

    def publish(self, topic, msg):
        if ~self._is_connecting and self._is_connected:
            self.client.publish(topic, msg)

    def send_car_command(self, speed, steer):
        self.publish("aadc/rc", MqttConnection.get_json_cmd(speed, steer))

    def disconnect(self):
        self.client.disconnect()

    def subscribe(self, *topics):
        if ~self._is_connecting and self._is_connected:
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

    def _on_message(self, client, userdata, message):
        if self.on_message is not None:
            self.on_message(client, userdata, message)
        return

    def _on_subscribe(self, client, userdata, mid, granted_qos):
        if self._last_sub_mid_list is not None:
            if mid in self._last_sub_mid_list:
                self._last_sub_mid_list.remove(mid)
                print("Subscribed successively!")
            else:
                print("Subscription not successful!")
        else:
            print("No previous subscription attempt ?!")

        if self.on_subscribe is not None:
            self.on_subscribe(client, userdata, mid, granted_qos)
        return

    def _on_connect(self, client, userdata, flags, rc):
        if rc != 0:
            print("Could not connect!")
            self.host = None
        else:
            print("Connected successively!")
            self._is_connected = True

        self._is_connecting = False

        if self.on_connect is not None:
            self.on_connect(client, userdata, flags, rc)
        return

    def _on_disconnect(self, client, userdata, rc):
        if rc != 0:
            print("Unexpected disconnect!")
        else:
            print("Disconnected successively!")
            self.client.loop_stop()

        self._is_connected = False

        if self.on_disconnect is not None:
            self.on_disconnect(client, userdata, rc)
        return
