"""
Hallo
"""
import json


class Logic:

    def __init__(self, mqtt_connection):
        self.mqtt_connection = mqtt_connection
        self.mqtt_connection.set_callback_methods(on_message=self.on_mqtt_message)
        self.lidar_json = None
        self.sensor_json = None
        return

    def on_mqtt_message(self, client, userdata, message):
        print("Logic")
        a = 0
        if message.topic == "aadc/lidar":
            self.lidar_json = json.loads(str(message.payload.decode("utf-8")))
            a += 1
        elif message.topic == "aadc/sensor":
            self.sensor_json = json.loads(str(message.payload.decode("utf-8")))
            a += 1
        if a > 0:
            self.main_logic()
        return

    def main_logic(self):
        pass
