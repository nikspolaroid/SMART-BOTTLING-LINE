#!/usr/bin/env python3
"""
simulation/tank_sim.py
Tank process simulator with PLC logic built in.
Publishes sensor data AND valve states via MQTT.
PLC logic mirrors the OpenPLC Structured Text program.
"""

import time
import random
import paho.mqtt.client as mqtt
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from config import (
    MQTT_BROKER, MQTT_PORT, MQTT_QOS,
    TOPIC_TANK_LEVEL, TOPIC_TANK_TEMP,
    TOPIC_TANK_FLOW_IN, TOPIC_TANK_FLOW_OUT,
    TOPIC_ALARM_OVERFLOW, TOPIC_ALARM_UNDERFLOW,
    PUBLISH_INTERVAL_S,
    TANK_MAX_VOLUME_L, TANK_FILL_RATE_L_MIN,
    TANK_DRAIN_RATE_L_MIN, TANK_HIGH_ALARM, TANK_LOW_ALARM
)

TOPIC_INLET_VALVE  = "bottling/inlet/valve"
TOPIC_OUTLET_VALVE = "bottling/outlet/valve"


class TankSimulator:
    def __init__(self):
        self.volume_L      = 300.0
        self.inlet_open    = True
        self.outlet_open   = False
        self.temperature_C = 20.0

    def step(self, dt_s: float):
        level_pct = self.volume_L / TANK_MAX_VOLUME_L * 100

        # ── PLC logic (mirrors OpenPLC ST program) ─────────────
        if level_pct <= 20.0:
            self.inlet_open = True
        if level_pct >= 80.0:
            self.inlet_open = False
        if level_pct >= 90.0:
            self.outlet_open = True
        else:
            self.outlet_open = False

        # ── Flow rates ─────────────────────────────────────────
        flow_in  = (TANK_FILL_RATE_L_MIN / 60.0 + random.uniform(-0.2, 0.2)) \
                   if self.inlet_open else 0.0
        flow_out = (TANK_DRAIN_RATE_L_MIN / 60.0 + random.uniform(-0.1, 0.1)) \
                   if self.outlet_open else 0.0

        # ── Volume update ──────────────────────────────────────
        self.volume_L += (flow_in - flow_out) * dt_s
        self.volume_L  = max(0.0, min(self.volume_L, TANK_MAX_VOLUME_L))

        # ── Temperature drift ──────────────────────────────────
        self.temperature_C += (22.0 - self.temperature_C) * 0.01 \
                              + random.uniform(-0.05, 0.05)

        level_pct = self.volume_L / TANK_MAX_VOLUME_L * 100

        return {
            "level_pct":   round(level_pct, 2),
            "volume_L":    round(self.volume_L, 2),
            "temperature": round(self.temperature_C, 2),
            "flow_in":     round(flow_in * 60, 2),
            "flow_out":    round(flow_out * 60, 2),
            "inlet_open":  self.inlet_open,
            "outlet_open": self.outlet_open,
        }


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT broker")
    else:
        print(f"Connection failed — code {rc}")


def main():
    print("Smart Bottling Line — Tank Simulator")
    print(f"   Broker : {MQTT_BROKER}:{MQTT_PORT}")
    print("   PLC logic: level<20 open inlet, level>80 close inlet, level>90 open outlet")
    print("   Press Ctrl+C to stop\n")

    client = mqtt.Client(client_id="tank_simulator")
    client.on_connect = on_connect
    client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
    client.loop_start()

    tank      = TankSimulator()
    last_time = time.time()

    try:
        while True:
            now  = time.time()
            dt   = now - last_time
            last_time = now

            state = tank.step(dt)

            # ── Publish sensor data ────────────────────────────
            client.publish(TOPIC_TANK_LEVEL,    state["level_pct"],   qos=MQTT_QOS)
            client.publish(TOPIC_TANK_TEMP,     state["temperature"], qos=MQTT_QOS)
            client.publish(TOPIC_TANK_FLOW_IN,  state["flow_in"],     qos=MQTT_QOS)
            client.publish(TOPIC_TANK_FLOW_OUT, state["flow_out"],    qos=MQTT_QOS)

            # ── Publish valve states ───────────────────────────
            client.publish(TOPIC_INLET_VALVE,  int(state["inlet_open"]),  qos=MQTT_QOS)
            client.publish(TOPIC_OUTLET_VALVE, int(state["outlet_open"]), qos=MQTT_QOS)

            # ── Publish alarms ─────────────────────────────────
            overflow  = 1 if state["level_pct"] >= TANK_HIGH_ALARM else 0
            underflow = 1 if state["level_pct"] <= TANK_LOW_ALARM  else 0
            client.publish(TOPIC_ALARM_OVERFLOW,  overflow,  qos=MQTT_QOS)
            client.publish(TOPIC_ALARM_UNDERFLOW, underflow, qos=MQTT_QOS)

            # ── Console readout ────────────────────────────────
            inlet_str  = "OPEN  " if state["inlet_open"]  else "CLOSED"
            outlet_str = "OPEN  " if state["outlet_open"] else "CLOSED"
            alarm_str  = " OVERFLOW!" if overflow else ""
            print(
                f"Level: {state['level_pct']:5.1f}%  "
                f"Temp: {state['temperature']:4.1f}C  "
                f"Inlet: {inlet_str}  "
                f"Outlet: {outlet_str}"
                f"{alarm_str}"
            )

            time.sleep(PUBLISH_INTERVAL_S)

    except KeyboardInterrupt:
        print("\nTank simulator stopped")
    finally:
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    main()