#!/usr/bin/env python3
"""
protocols/mqtt_monitor.py
─────────────────────────
Subscribes to all bottling line topics and prints
a live formatted table in the terminal.

Useful for:
  - Verifying simulators are publishing
  - Debugging protocol issues
  - Showing all live values at once

Run:
    python protocols/mqtt_monitor.py
"""

import paho.mqtt.client as mqtt
from datetime import datetime
import sys
import os

# Add parent dir so we can import config
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'simulation'))
from config import MQTT_BROKER, MQTT_PORT

# ── Live state store ──────────────────────────────────────────
state = {}

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        client.subscribe("bottling/#")
        print("✅ Connected — watching all bottling/# topics\n")
    else:
        print(f"❌ Failed to connect — code {rc}")

def on_message(client, userdata, msg):
    topic = msg.topic
    try:
        value = float(msg.payload.decode())
        state[topic] = value
    except ValueError:
        state[topic] = msg.payload.decode()

    print_state()

def print_state():
    """Clear screen and print current state table."""
    print("\033[2J\033[H", end="")   # clear terminal
    print(f"🏭 Bottling Line — Live MQTT Monitor   {datetime.now().strftime('%H:%M:%S')}")
    print("─" * 55)
    print(f"{'Topic':<38} {'Value'}")
    print("─" * 55)
    for topic, value in sorted(state.items()):
        if isinstance(value, float):
            print(f"  {topic:<36} {value:.2f}")
        else:
            print(f"  {topic:<36} {value}")
    print("─" * 55)
    print("Press Ctrl+C to stop")

def main():
    client = mqtt.Client(client_id="mqtt_monitor")
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)

    try:
        client.loop_forever()
    except KeyboardInterrupt:
        print("\n🛑 Monitor stopped")
        client.disconnect()

if __name__ == "__main__":
    main()
