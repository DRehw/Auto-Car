"""
Created on May 11, 2019

@author: Dave
"""

import paho.mqtt.client as mqtt
import time


def get_json_cmd(speed, steer):
    millis = int(round(time.time() * 1000))
    if speed < 60 or speed > 120:
        speed = 90
    if steer < 60 or steer > 120:
        steer = 90
    return "{{\"vehicle\": \"AADC2016\", \"type\": \"actuator\", \"drive\": {}, \"steering\": {}, \"brakelight\": 0,\"turnsignalright\": 0,\"turnsignalleft\": 0,\"dimlight\": 0,\"reverselight\": 0,\"timestamp\": {}}}".format(speed, steer, millis)


def send_cmd(client, cmd):
    if client is not None:
        client.publish("aadc/rc", cmd)
    else:
        print("No active connection!")


def subscribe(client, *topics):
    mid = -1
    topics = list(topics)
    liste = []
    for t in topics:
        liste.append((t, 1))
    topics = liste
    string = "Subscribing to: "
    for tupl in topics:
        string += tupl[0] + ", "
    print(string[:-2])
    if client is not None:
        a = client.subscribe(topics)
        mid = a[1]
    else:
        print("No active connection!")
    return mid    


def connect(client, host):
    client.loop_start()
    client.connect_async(host)


def get_client(name, on_connect, on_subscribe, on_message, on_disconnect):
    client = mqtt.Client(name)
    client.on_connect = on_connect
    client.on_subscribe = on_subscribe
    client.on_message = on_message
    client.on_disconnect = on_disconnect
    return client
