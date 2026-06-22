#!/usr/bin/env python3
"""
protocols/opcua_client.py
OPC UA client that reads live tag values from Ignition.
Demonstrates OPC UA as a pull protocol — same way
a MES or analytics system would read from a SCADA.
"""
from opcua import Client
import time

IGNITION_OPC_URL = "opc.tcp://localhost:62541"
TAG_PROVIDER     = "ns=2;s=[default]"
TAGS = {
    "tank_level":     "ns=2;s=[default]/tank_level",
    "temperature":    "ns=2;s=[default]/temperature",
    "alarm_overflow": "ns=2;s=[default]/alarm_overflow",
    "alarm_low":      "ns=2;s=[default]/alarm_low",
    "inlet_valve":    "ns=2;s=[default]/inlet_valve",
    "outlet_valve":   "ns=2;s=[default]/outlet_valve",
    "bottles_filled": "ns=2;s=[default]/bottles_filled",
    "filler_active":  "ns=2;s=[default]/filler_active",
}
def read_tags(client):
    results = {}
    for name, node_id in TAGS.items():
        try:
            node  = client.get_node(node_id)
            value = node.get_value()
            results[name] = value
        except Exception as e:
            results[name] = f"ERROR: {e}"
    return results

def print_table(data):
    print("\033[2J\033[H", end="")
    print("=" * 55)
    print("  Smart Bottling Line — OPC UA Live Monitor")
    print("  Connected to Ignition OPC UA Server :62541")
    print("=" * 55)
    print(f"  {'Tag':<20} {'Value'}")
    print("-" * 55)
    for name, value in data.items():
        if isinstance(value, float):
            print(f"  {name:<20} {value:.2f}")
        elif isinstance(value, bool):
            state = "TRUE" if value else "FALSE"
            print(f"  {name:<20} {state}")
        else:
            print(f"  {name:<20} {value}")
    print("=" * 55)
    print("  Press Ctrl+C to stop")

def main():
    print(f"Connecting to Ignition OPC UA at {IGNITION_OPC_URL}...")
    client = Client(IGNITION_OPC_URL)

    try:
        client.connect()
        print("Connected! Reading tags every 1s...\n")

        while True:
            data = read_tags(client)
            print_table(data)
            time.sleep(1.0)

    except KeyboardInterrupt:
        print("\nOPC UA client stopped")
    finally:
        client.disconnect()

if __name__ == "__main__":
    main()