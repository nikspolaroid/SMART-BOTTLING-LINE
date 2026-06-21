#!/usr/bin/env python3
"""
simulation/mqtt_to_ignition.py
Reads MQTT data and writes values into Ignition tags via REST API
"""

import paho.mqtt.client as mqtt
import requests
import json
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from config import MQTT_BROKER, MQTT_PORT

# Ignition REST API settings
IGNITION_URL = "http://localhost:8088/system/webdev"
GATEWAY_URL  = "http://localhost:8088"

def write_tag(tag_name, value):
    """Write a value to an Ignition memory tag via REST API"""
    url = f"{GATEWAY_URL}/system/tag/write"
    payload = {
        "tags": [f"[default]{tag_name}"],
        "values": [value]
    }
    try:
        r = requests.post(url, json=payload, auth=("admin", "admin123"))
        return r.status_code
    except Exception as e:
        print(f"Error writing tag {tag_name}: {e}")
        return None

def on_connect(client, userdata, flags, rc):
    client.subscribe("bottling/#")
    print("✅ Connected to MQTT broker — forwarding to Ignition tags")

def on_message(client, userdata, msg):
    topic = msg.topic
    try:
        value = float(msg.payload.decode())
    except:
        value = msg.payload.decode()

    # Map MQTT topics to Ignition tags
    if topic == "bottling/tank/level":
        write_tag("tank_level", value)
        print(f"tank_level → {value:.1f}%")
    elif topic == "bottling/alarm/overflow":
        write_tag("alarm_overflow", bool(int(value)))
    elif topic == "bottling/alarm/underflow":
        write_tag("alarm_low", bool(int(value)))

client = mqtt.Client(client_id="mqtt_to_ignition")
client.on_connect = on_connect
client.on_message = on_message
client.connect(MQTT_BROKER, MQTT_PORT)

try:
    client.loop_forever()
except KeyboardInterrupt:
    print("\n🛑 Bridge stopped")
    client.disconnect()
