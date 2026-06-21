#!/usr/bin/env python3
"""
simulation/level_to_file.py
Reads tank level from MQTT and writes to a shared file
that Ignition Timer Script reads every 500ms
"""
import paho.mqtt.client as mqtt
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from config import MQTT_BROKER, MQTT_PORT, TOPIC_TANK_LEVEL

FILE_PATH = "/tmp/tank_level.txt"

def on_connect(client, userdata, flags, rc):
    client.subscribe(TOPIC_TANK_LEVEL)
    print(f"✅ Connected — writing to {FILE_PATH}")

def on_message(client, userdata, msg):
    level = float(msg.payload.decode())
    with open(FILE_PATH, "w") as f:
        f.write(str(level))
    print(f"Level: {level:.1f}%")

client = mqtt.Client(client_id="level_to_file")
client.on_connect = on_connect
client.on_message = on_message
client.connect(MQTT_BROKER, MQTT_PORT)

try:
    client.loop_forever()
except KeyboardInterrupt:
    print("\n🛑 Stopped")
    client.disconnect()
