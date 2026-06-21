#!/usr/bin/env python3
import paho.mqtt.client as mqtt
import json
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from config import MQTT_BROKER, MQTT_PORT

FILE_PATH = "/tmp/bottling_data.json"

data = {
    "tank_level": 0.0,
    "temperature": 0.0,
    "alarm_overflow": 0,
    "alarm_low": 0,
    "conveyor_speed": 0.0,
    "conveyor_state": "stopped",
    "bottles_filled": 0
}

def on_connect(client, userdata, flags, rc):
    client.subscribe("bottling/#")
    print(f"Connected — writing to {FILE_PATH}")

def on_message(client, userdata, msg):
    topic = msg.topic
    try:
        value = msg.payload.decode()
        if topic == "bottling/tank/level":
            data["tank_level"] = float(value)
        elif topic == "bottling/tank/temperature":
            data["temperature"] = float(value)
        elif topic == "bottling/alarm/overflow":
            data["alarm_overflow"] = int(float(value))
        elif topic == "bottling/alarm/underflow":
            data["alarm_low"] = int(float(value))
        elif topic == "bottling/conveyor/speed":
            data["conveyor_speed"] = float(value)
        elif topic == "bottling/conveyor/state":
            data["conveyor_state"] = value
        elif topic == "bottling/conveyor/count":
            data["bottles_filled"] = int(float(value))
        with open(FILE_PATH, "w") as f:
            json.dump(data, f)
        print(f"Tank: {data['tank_level']:.1f}%  Bottles: {data['bottles_filled']}")
    except Exception as e:
        print(f"Error: {e}")

client = mqtt.Client(client_id="level_to_file")
client.on_connect = on_connect
client.on_message = on_message
client.connect(MQTT_BROKER, MQTT_PORT)

try:
    client.loop_forever()
except KeyboardInterrupt:
    client.disconnect()