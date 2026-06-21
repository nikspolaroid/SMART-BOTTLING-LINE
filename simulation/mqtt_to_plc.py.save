#!/usr/bin/env python3
"""
simulation/mqtt_to_plc.py
Reads tank level from MQTT and writes it into OpenPLC simulator
"""

import paho.mqtt.client as mqtt
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from config import MQTT_BROKER, MQTT_PORT, TOPIC_TANK_LEVEL

current_level = 0.0

def on_connect(client, userdata, flags, rc):
    client.subscribe(TOPIC_TANK_LEVEL)
    print(f"✅ Connected — watching {TOPIC_TANK_LEVEL}")

def on_message(client, userdata, msg):
    global current_level
    current_level = float(msg.payload.decode())
    print(f"Tank level received: {current_level:.1f}%")

client = mqtt.Client(client_id="mqtt_to_plc")
client.on_connect = on_connect
client.on_message = on_message
client.connect(MQTT_BROKER, MQTT_PORT)

try:
    client.loop_forever()
except KeyboardInterrupt:
    print("\n🛑 Bridge stopped")
    client.disconnect()
