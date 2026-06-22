#!/usr/bin/env python3
"""
simulation/tank_sim.py
Tank simulator with correct PLC logic.
Subscribes to filler_active via MQTT directly.
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

TOPIC_INLET_VALVE    = "bottling/inlet/valve"
TOPIC_OUTLET_VALVE   = "bottling/outlet/valve"
TOPIC_FILLER_ACTIVE  = "bottling/conveyor/filler_active"

BOTTLE_VOLUME_L     = 0.5    # litres per bottle
FILLER_DRAIN_RATE   = 10.0   # L/min consumed while filling


class TankSimulator:
    def __init__(self):
        self.volume_L       = 300.0
        self.inlet_open     = True
        self.outlet_open    = False
        self.temperature_C  = 20.0
        self.filler_active  = False

    def step(self, dt_s: float):
        level_pct = self.volume_L / TANK_MAX_VOLUME_L * 100

        # ── PLC logic ──────────────────────────────────────────
        # Inlet: open below 20%, close above 80%
        if level_pct <= 20.0:
            self.inlet_open = True
        if level_pct >= 80.0:
            self.inlet_open = False

        # Outlet: open only on overflow above 90%
        if level_pct >= 90.0:
            self.outlet_open = True
        else:
            self.outlet_open = False

        # ── Flow rates (L/s) ───────────────────────────────────
        # Inlet flow
        flow_in = (TANK_FILL_RATE_L_MIN / 60.0
                   + random.uniform(-0.2, 0.2)) \
                  if self.inlet_open else 0.0

        # Overflow drain
        flow_overflow = (TANK_DRAIN_RATE_L_MIN / 60.0
                         + random.uniform(-0.1, 0.1)) \
                        if self.outlet_open else 0.0

        # Filler drain — liquid leaves tank when filling bottles
        flow_filler = (FILLER_DRAIN_RATE / 60.0) \
                      if self.filler_active else 0.0

        total_out = flow_overflow + flow_filler

        # ── Volume update ──────────────────────────────────────
        self.volume_L += (flow_in - total_out) * dt_s
        self.volume_L  = max(0.0, min(self.volume_L, TANK_MAX_VOLUME_L))

        # ── Temperature drift ──────────────────────────────────
        self.temperature_C += (22.0 - self.temperature_C) * 0.01 \
                              + random.uniform(-0.05, 0.05)

        level_pct = self.volume_L / TANK_MAX_VOLUME_L * 100

        return {
            "level_pct":     round(level_pct, 2),
            "volume_L":      round(self.volume_L, 2),
            "temperature":   round(self.temperature_C, 2),
            "flow_in":       round(flow_in * 60, 2),
            "flow_out":      round(total_out * 60, 2),
            "inlet_open":    self.inlet_open,
            "outlet_open":   self.outlet_open,
            "filler_active": self.filler_active,
        }


# ── Shared tank instance ───────────────────────────────────────
tank = TankSimulator()


# ── MQTT callbacks ─────────────────────────────────────────────
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Connected to MQTT broker")
        client.subscribe(TOPIC_FILLER_ACTIVE)
        print("   Subscribed to filler_active topic")
    else:
        print(f"❌ Connection failed — code {rc}")


def on_message(client, userdata, msg):
    if msg.topic == TOPIC_FILLER_ACTIVE:
        tank.filler_active = msg.payload.decode() == "True"


# ── Main ───────────────────────────────────────────────────────
def main():
    print("🏭 Smart Bottling Line — Tank Simulator")
    print("   PLC logic:")
    print("   Level < 20%  → open inlet valve")
    print("   Level > 80%  → close inlet valve")
    print("   Level > 90%  → open outlet valve")
    print("   Filler ON    → drain 10 L/min from tank")
    print("   Press Ctrl+C to stop\n")

    client = mqtt.Client(client_id="tank_simulator")
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
    client.loop_start()

    last_time = time.time()

    try:
        while True:
            now       = time.time()
            dt        = now - last_time
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
            filler_str = "FILLING" if state["filler_active"] else "IDLE   "
            alarm_str  = ""
            if overflow:  alarm_str = " ⚠️  OVERFLOW"
            if underflow: alarm_str = " ⚠️  LOW LEVEL"

            print(
                f"Level: {state['level_pct']:5.1f}%  "
                f"In: {state['flow_in']:5.1f} L/min  "
                f"Out: {state['flow_out']:5.1f} L/min  "
                f"Inlet: {inlet_str}  "
                f"Outlet: {outlet_str}  "
                f"Filler: {filler_str}"
                f"{alarm_str}"
            )

            time.sleep(PUBLISH_INTERVAL_S)

    except KeyboardInterrupt:
        print("\n🛑 Tank simulator stopped")
    finally:
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    main()