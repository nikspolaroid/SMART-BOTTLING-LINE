#!/usr/bin/env python3
"""
simulation/conveyor_sim.py
──────────────────────────
Phase 2 — Conveyor process simulator

Simulates a bottle conveyor belt with:
  - Belt running / stopped / fault states
  - Bottle position tracking
  - Bottle counter (filled bottles)
  - Speed variation with noise
  - Publishes all values to MQTT every 500ms

Run:
    python simulation/conveyor_sim.py

Watch in MQTT Explorer or:
    mosquitto_sub -t "bottling/conveyor/#" -v
"""

import time
import random
import paho.mqtt.client as mqtt
from config import (
    MQTT_BROKER, MQTT_PORT, MQTT_QOS,
    TOPIC_CONVEYOR_SPEED, TOPIC_CONVEYOR_COUNT,
    TOPIC_CONVEYOR_STATE, TOPIC_ALARM_FAULT,
    PUBLISH_INTERVAL_S
)

# ── Conveyor constants ─────────────────────────────────────────
BELT_NOMINAL_SPEED   = 1.2    # m/min
BOTTLE_SPACING_M     = 0.15   # distance between bottle centres
FILL_STATION_POS_M   = 1.0    # where the filler head sits
BELT_LENGTH_M        = 3.0    # total belt visible length
FAULT_PROBABILITY    = 0.002  # chance of random fault per cycle


# ── Conveyor state ────────────────────────────────────────────
class ConveyorSimulator:
    def __init__(self):
        self.running         = True
        self.fault           = False
        self.speed_m_min     = BELT_NOMINAL_SPEED
        self.bottles_filled  = 0
        self.belt_pos_m      = 0.0     # tracks virtual belt position
        self._next_bottle_at = 0.0     # belt pos where next bottle appears
        self._fault_timer    = 0.0     # how long fault has been active

    def step(self, dt_s: float):
        """Advance simulation by dt_s seconds."""

        # ── Random fault injection ─────────────────────────────────────
        if not self.fault and random.random() < FAULT_PROBABILITY:
            self.fault   = True
            self.running = False
            print("⚠️  Conveyor fault injected — motor overload simulated")

        # ── Auto-recover from fault after 8 seconds ────────────────────
        if self.fault:
            self._fault_timer += dt_s
            if self._fault_timer >= 8.0:
                self.fault         = False
                self.running       = True
                self._fault_timer  = 0.0
                print("✅ Conveyor fault cleared — restarting")

        # ── Belt movement ──────────────────────────────────────────────
        if self.running:
            # Small speed variation: ±5% of nominal
            self.speed_m_min = BELT_NOMINAL_SPEED + random.uniform(-0.06, 0.06)
            distance_m = (self.speed_m_min / 60.0) * dt_s
            self.belt_pos_m += distance_m

            # ── Count a bottle each time one passes the fill station ───
            if self.belt_pos_m >= self._next_bottle_at + FILL_STATION_POS_M:
                self.bottles_filled  += 1
                self._next_bottle_at  = self.belt_pos_m
        else:
            self.speed_m_min = 0.0

        # ── Build state dict ───────────────────────────────────────────
        if self.fault:
            state_str = "fault"
        elif self.running:
            state_str = "running"
        else:
            state_str = "stopped"

        return {
            "state":          state_str,
            "speed_m_min":    round(self.speed_m_min, 3),
            "bottles_filled": self.bottles_filled,
            "fault":          self.fault,
        }


# ── MQTT callbacks ────────────────────────────────────────────
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Connected to MQTT broker")
    else:
        print(f"❌ Connection failed — code {rc}")


# ── Main ──────────────────────────────────────────────────────
def main():
    print("🏭 Smart Bottling Line — Conveyor Simulator")
    print(f"   Broker : {MQTT_BROKER}:{MQTT_PORT}")
    print(f"   Topics : bottling/conveyor/#")
    print(f"   Rate   : every {PUBLISH_INTERVAL_S}s")
    print("   Press Ctrl+C to stop\n")

    client = mqtt.Client(client_id="conveyor_simulator")
    client.on_connect = on_connect
    client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
    client.loop_start()

    conveyor  = ConveyorSimulator()
    last_time = time.time()

    try:
        while True:
            now = time.time()
            dt  = now - last_time
            last_time = now

            state = conveyor.step(dt)

            # ── Publish ────────────────────────────────────────────────
            client.publish(TOPIC_CONVEYOR_SPEED, state["speed_m_min"],    qos=MQTT_QOS)
            client.publish(TOPIC_CONVEYOR_COUNT, state["bottles_filled"],  qos=MQTT_QOS)
            client.publish(TOPIC_CONVEYOR_STATE, state["state"],           qos=MQTT_QOS)

            if state["fault"]:
                client.publish(TOPIC_ALARM_FAULT, "conveyor_motor_overload", qos=MQTT_QOS)

            # ── Console readout ────────────────────────────────────────
            print(
                f"Conveyor: {state['state']:8s}  "
                f"Speed: {state['speed_m_min']:4.2f} m/min  "
                f"Bottles filled: {state['bottles_filled']:4d}"
            )

            time.sleep(PUBLISH_INTERVAL_S)

    except KeyboardInterrupt:
        print("\n🛑 Conveyor simulator stopped")
    finally:
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    main()
