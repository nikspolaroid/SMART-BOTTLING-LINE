#!/usr/bin/env python3
"""
simulation/mqtt_to_modbus.py
Reads sensor data from MQTT and writes to OpenPLC via Modbus TCP
This bridges the Python simulator to the PLC
"""

import paho.mqtt.client as mqtt
from pymodbus.client import ModbusTcpClient
import sys
import os
import time
sys.path.insert(0, os.path.dirname(__file__))
from config import MQTT_BROKER, MQTT_PORT

# OpenPLC Modbus settings
PLC_HOST = "localhost"
PLC_PORT = 502

# Current values
values = {
    "tank_level": 0.0,
    "temperature": 0.0,
    "flow_in": 0.0,
}

def scale_to_modbus(value, min_val=0.0, max_val=100.0):
    """Scale a float value to Modbus register range 0-32767"""
    scaled = int((value - min_val) / (max_val - min_val) * 32767)
    return max(0, min(32767, scaled))

def write_to_plc():
    """Write current values to OpenPLC via Modbus TCP"""
    try:
        client = ModbusTcpClient(PLC_HOST, port=PLC_PORT)
        if client.connect():
            # Write to holding registers
            # Register 0 = tank_level (scaled)
            # Register 1 = temperature (scaled)
            # Register 2 = flow_in (scaled)
            client.write_register(0, scale_to_modbus(values["tank_level"]))
            client.write_register(1, scale_to_modbus(values["temperature"], 0, 100))
            client.write_register(2, scale_to_modbus(values["flow_in"], 0, 100))
            client.close()
            return True
        else:
            print("❌ Cannot connect to OpenPLC on port 502")
            return False
    except Exception as e:
        print(f"❌ Modbus error: {e}")
        return False

def on_connect(client, userdata, flags, rc):
    client.subscribe("bottling/#")
    print("✅ Connected to MQTT broker")
    print(f"   Writing to OpenPLC at {PLC_HOST}:{PLC_PORT}")
    print("   Press Ctrl+C to stop\n")

def on_message(client, userdata, msg):
    topic = msg.topic
    try:
        value = float(msg.payload.decode())
    except:
        return

    if topic == "bottling/tank/level":
        values["tank_level"] = value
        if write_to_plc():
            print(f"✅ tank_level={value:.1f}% → Modbus reg[0]={scale_to_modbus(value)}")
    elif topic == "bottling/tank/temperature":
        values["temperature"] = value
    elif topic == "bottling/tank/flow_in":
        values["flow_in"] = value

client = mqtt.Client(client_id="mqtt_to_modbus")
client.on_connect = on_connect
client.on_message = on_message
client.connect(MQTT_BROKER, MQTT_PORT)

try:
    client.loop_forever()
except KeyboardInterrupt:
    print("\n🛑 Bridge stopped")
    client.disconnect()
