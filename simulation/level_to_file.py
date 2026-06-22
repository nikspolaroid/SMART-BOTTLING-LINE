#!/usr/bin/env python3
"""
simulation/level_to_file.py
Subscribes to all MQTT topics and writes to JSON file.
Ignition Timer Script reads this file every 500ms.
"""
import paho.mqtt.client as mqtt
import json
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from config import MQTT_BROKER, MQTT_PORT

FILE_PATH = "/tmp/bottling_data.json"

data = {
    "tank_level":    0.0,
    "temperature":   0.0,
    "flow_in":       0.0,
    "flow_out":      0.0,
    "alarm_overflow": 0,
    "alarm_low":     0,
    "inlet_valve":   0,
    "outlet_valve":  0,
    "conveyor_speed": 0.0,
    "conveyor_state": "stopped",
    "bottles_filled": 0,
    "filler_active":  False
}

def on_connect(client, userdata, flags, rc):
    client.subscribe("bottling/#")
    print(f"Connected — writing all data to {FILE_PATH}")

def on_message(client, userdata, msg):
    topic = msg.topic
    try:
        value = msg.payload.decode()

        if topic == "bottling/tank/level":
            data["tank_level"] = float(value)
        elif topic == "bottling/tank/temperature":
            data["temperature"] = float(value)
        elif topic == "bottling/tank/flow_in":
            data["flow_in"] = float(value)
        elif topic == "bottling/tank/flow_out":
            data["flow_out"] = float(value)
        elif topic == "bottling/alarm/overflow":
            data["alarm_overflow"] = int(float(value))
        elif topic == "bottling/alarm/underflow":
            data["alarm_low"] = int(float(value))
        elif topic == "bottling/inlet/valve":
            data["inlet_valve"] = int(float(value))
        elif topic == "bottling/outlet/valve":
            data["outlet_valve"] = int(float(value))
        elif topic == "bottling/conveyor/speed":
            data["conveyor_speed"] = float(value)
        elif topic == "bottling/conveyor/state":
            data["conveyor_state"] = value
        elif topic == "bottling/conveyor/count":
            data["bottles_filled"] = int(float(value))
        elif topic == "bottling/conveyor/filler_active":
            data["filler_active"] = value == "True"

        with open(FILE_PATH, "w") as f:
            json.dump(data, f)

        print(
            f"Tank: {data['tank_level']:.1f}%  "
            f"Inlet: {'OPEN' if data['inlet_valve'] else 'CLOSED'}  "
            f"Outlet: {'OPEN' if data['outlet_valve'] else 'CLOSED'}  "
            f"Bottles: {data['bottles_filled']}"
        )

    except Exception as e:
        print(f"Error: {e}")

client = mqtt.Client(client_id="level_to_file")
client.on_connect = on_connect
client.on_message = on_message
client.connect(MQTT_BROKER, MQTT_PORT)

try:
    client.loop_forever()
except KeyboardInterrupt:
    print("\nStopped")
    client.disconnect()