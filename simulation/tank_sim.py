#!/usr/bin/env python3
"""
simulation/tank_sim.py
──────────────────────
Phase 2 — Tank process simulator

Simulates a liquid tank with:
  - Controlled fill (inlet valve)
  - Controlled drain (outlet to filler)
  - Level calculated from flow rates
  - Overflow and underflow detection
  - Publishes all values to MQTT every 500ms

Run:
    python simulation/tank_sim.py

Watch in MQTT Explorer or:
    mosquitto_sub -t "bottling/tank/#" -v
"""

import time
import json
import random
import paho.mqtt.client as mqtt
from config import (
    MQTT_BROKER, MQTT_PORT, MQTT_QOS,
    TOPIC_TANK_LEVEL, TOPIC_TANK_TEMP,
    TOPIC_TANK_FLOW_IN, TOPIC_TANK_FLOW_OUT,
    TOPIC_ALARM_OVERFLOW, TOPIC_ALARM_UNDERFLOW,
    PUBLISH_INTERVAL_S,
    TANK_MAX_VOLUME_L, TANK_FILL_RATE_L_MIN,
    TANK_DRAIN_RATE_L_MIN, TANK_HIGH_ALARM, TANK_LOW_ALARM
)


# ── Tank state ────────────────────────────────────────────────
class TankSimulator:
    def __init__(self):
        self.volume_L        = 300.0   # start at 30% full
        self.inlet_open      = True    # inlet valve state
        self.outlet_open     = False   # outlet valve state (filler)
        self.temperature_C   = 20.0   # ambient start temp
        self._cycle          = 0      # internal step counter

    def step(self, dt_s: float):
        """Advance simulation by dt_s seconds."""
        self._cycle += 1

        # ── Auto cycle: open outlet when level > 60%, close when < 20% ──
        if self.volume_L / TANK_MAX_VOLUME_L * 100 >= 60.0:
            self.outlet_open = True
        if self.volume_L / TANK_MAX_VOLUME_L * 100 <= 20.0:
            self.outlet_open = False

        # ── Flow rates (L/s) with small random noise ──────────────────
        flow_in  = (TANK_FILL_RATE_L_MIN / 60.0 + random.uniform(-0.2, 0.2)) \
                   if self.inlet_open else 0.0
        flow_out = (TANK_DRAIN_RATE_L_MIN / 60.0 + random.uniform(-0.1, 0.1)) \
                   if self.outlet_open else 0.0

        # ── Volume update ──────────────────────────────────────────────
        self.volume_L += (flow_in - flow_out) * dt_s
        self.volume_L  = max(0.0, min(self.volume_L, TANK_MAX_VOLUME_L))

        # ── Temperature: slow drift toward 22°C + tiny noise ──────────
        self.temperature_C += (22.0 - self.temperature_C) * 0.01 \
                              + random.uniform(-0.05, 0.05)

        return {
            "level_pct":   round(self.volume_L / TANK_MAX_VOLUME_L * 100, 2),
            "volume_L":    round(self.volume_L, 2),
            "temperature": round(self.temperature_C, 2),
            "flow_in":     round(flow_in * 60, 2),   # back to L/min for display
            "flow_out":    round(flow_out * 60, 2),
            "inlet_open":  self.inlet_open,
            "outlet_open": self.outlet_open,
        }


# ── MQTT callbacks ────────────────────────────────────────────
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Connected to MQTT broker")
    else:
        print(f"❌ Connection failed — code {rc}")


def on_disconnect(client, userdata, rc):
    print("⚠️  Disconnected from MQTT broker")


# ── Main ──────────────────────────────────────────────────────
def main():
    print("🏭 Smart Bottling Line — Tank Simulator")
    print(f"   Broker : {MQTT_BROKER}:{MQTT_PORT}")
    print(f"   Topics : bottling/tank/#")
    print(f"   Rate   : every {PUBLISH_INTERVAL_S}s")
    print("   Press Ctrl+C to stop\n")

    # Set up MQTT client
    client = mqtt.Client(client_id="tank_simulator")
    client.on_connect    = on_connect
    client.on_disconnect = on_disconnect
    client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
    client.loop_start()

    tank = TankSimulator()
    last_time = time.time()

    try:
        while True:
            now = time.time()
            dt  = now - last_time
            last_time = now

            state = tank.step(dt)

            # ── Publish individual sensor topics ──────────────────────
            client.publish(TOPIC_TANK_LEVEL,   state["level_pct"],   qos=MQTT_QOS)
            client.publish(TOPIC_TANK_TEMP,    state["temperature"], qos=MQTT_QOS)
            client.publish(TOPIC_TANK_FLOW_IN, state["flow_in"],     qos=MQTT_QOS)
            client.publish(TOPIC_TANK_FLOW_OUT,state["flow_out"],    qos=MQTT_QOS)

            # ── Publish alarms ────────────────────────────────────────
            overflow  = 1 if state["level_pct"] >= TANK_HIGH_ALARM  else 0
            underflow = 1 if state["level_pct"] <= TANK_LOW_ALARM   else 0
            client.publish(TOPIC_ALARM_OVERFLOW,  overflow,  qos=MQTT_QOS)
            client.publish(TOPIC_ALARM_UNDERFLOW, underflow, qos=MQTT_QOS)

            # ── Console readout ───────────────────────────────────────
            alarm_str = ""
            if overflow:  alarm_str = " ⚠️  OVERFLOW"
            if underflow: alarm_str = " ⚠️  UNDERFLOW"
            print(
                f"Tank: {state['level_pct']:5.1f}%  "
                f"Temp: {state['temperature']:4.1f}°C  "
                f"In: {state['flow_in']:4.1f} L/min  "
                f"Out: {state['flow_out']:4.1f} L/min"
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
