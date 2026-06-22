#!/usr/bin/env python3
import paho.mqtt.client as mqtt
import time
import json
import random
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from config import MQTT_BROKER, MQTT_PORT, PUBLISH_INTERVAL_S

TOPIC_SPEED = "bottling/conveyor/speed"
TOPIC_COUNT = "bottling/conveyor/count"
TOPIC_STATE = "bottling/conveyor/state"
TOPIC_FILLER = "bottling/conveyor/filler_active"
DATA_FILE = "/tmp/bottling_data.json"

def get_tank_level():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f).get("tank_level", 0.0)
    except:
        return 0.0

class ConveyorSimulator:
    def __init__(self):
        self.running = True
        self.fault = False
        self.speed = 1.2
        self.bottles_filled = 0
        self.filler_active = False
        self.filler_timer = 0.0
        self.bottle_timer = 0.0
        self.bottle_interval = 5.0
        self.fill_duration = 3.0
        self.state = "running"

    def step(self, dt):
        if self.fault:
            self.state = "fault"
            self.speed = 0.0
            return self._data()

        self.speed = 1.2 + random.uniform(-0.05, 0.05)
        self.state = "running"

        self.bottle_timer += dt
        if self.bottle_timer >= self.bottle_interval and not self.filler_active:
            tank_level = get_tank_level()
            if tank_level > 30.0:
                self.filler_active = True
                self.filler_timer = 0.0
                self.bottle_timer = 0.0
                print(f"Bottle arrived - filling (tank: {tank_level:.1f}%)")
            else:
                self.bottle_timer = 0.0
                print(f"Interlock - tank too low ({tank_level:.1f}%) skipping")

        if self.filler_active:
            self.filler_timer += dt
            self.state = "filling"
            if self.filler_timer >= self.fill_duration:
                self.bottles_filled += 1
                self.filler_active = False
                self.state = "running"
                print(f"Bottle filled! Total: {self.bottles_filled}")

        return self._data()

    def _data(self):
        return {
            "state": self.state,
            "speed": round(self.speed, 2),
            "bottles_filled": self.bottles_filled,
            "filler_active": self.filler_active
        }

def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT broker")

client = mqtt.Client(client_id="conveyor_simulator")
client.on_connect = on_connect
client.connect(MQTT_BROKER, MQTT_PORT)
client.loop_start()

conveyor = ConveyorSimulator()
last_time = time.time()

print("Conveyor Simulator running - bottle every 5s, fill cycle 3s")

try:
    while True:
        now = time.time()
        dt = now - last_time
        last_time = now
        state = conveyor.step(dt)
        client.publish(TOPIC_SPEED, state["speed"])
        client.publish(TOPIC_COUNT, state["bottles_filled"])
        client.publish(TOPIC_STATE, state["state"])
        client.publish(TOPIC_FILLER, str(state["filler_active"]))
        time.sleep(PUBLISH_INTERVAL_S)
except KeyboardInterrupt:
    print("Conveyor stopped")
    client.loop_stop()
    client.disconnect()