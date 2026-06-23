# Smart Bottling Line

A complete industrial automation simulation I built to learn and demonstrate the kind of skills needed for Industry 4.0 roles — PLC programming, SCADA/HMI, and industrial networking protocols. Everything runs on a MacBook with no physical hardware.

---

## What it simulates

A bottling plant where:
- A liquid tank fills and drains based on control logic
- A conveyor moves bottles to a filler head
- The filler checks tank level before starting a fill cycle
- Alarms fire when the tank overflows or runs dry
- An operator HMI shows everything live in a browser

---

## How it actually works

The project has four layers that talk to each other:

**Python simulators** generate fake sensor data — tank level, temperature, flow rates, conveyor speed. They publish this over MQTT every 500ms, mimicking real field devices.

**MQTT broker (Mosquitto)** acts as the message bus. Everything publishes and subscribes through it. A bridge script writes all the live data to a shared JSON file.

**PLC logic** lives in two places. The OpenPLC Editor has the real IEC 61131-3 Structured Text program (tank fill control, overflow alarms, valve interlocks). Since connecting OpenPLC to the rest of the stack on Apple Silicon proved unreliable, the same logic runs as a soft PLC inside an Ignition Gateway Timer Script — this is documented intentionally rather than hidden.

**Ignition Maker Edition** reads the JSON file every 500ms, updates memory tags, and drives the HMI. The browser-based Perspective interface shows a live tank graphic, valve states, alarm indicators, temperature, and bottle counter.

An OPC UA Python client connects to Ignition's built-in OPC UA server on port 62541 and reads all tags live — demonstrating the protocol that's central to Industry 4.0 integration.

---

## Protocols used

| Protocol | Port | What it does |
|---|---|---|
| MQTT | 1883 | Sensor data from simulators to broker |
| OPC UA | 62541 | Python client reads live tags from Ignition |
| Modbus TCP | 502 | Documented in PLC I/O map, used in OpenPLC |
| HTTP/WebSocket | 8088 | Ignition Perspective HMI in browser |

---

## Project structure

```
smart-bottling-line/
├── simulation/
│   ├── tank_sim.py          Main tank simulator with PLC logic built in
│   ├── conveyor_sim.py      Conveyor and bottle fill cycle simulator
│   ├── level_to_file.py     MQTT bridge — writes all data to JSON file
│   └── config.py            MQTT topics and shared settings
├── plc/
│   └── tank_control/        OpenPLC Editor project (IEC 61131-3 ST)
├── protocols/
│   ├── mqtt_monitor.py      Terminal dashboard showing all live MQTT topics
│   └── opcua_client.py      OPC UA client reading live tags from Ignition
├── docs/
│   ├── architecture.md      System architecture notes
│   ├── mqtt_topics.md       Full MQTT topic reference
│   └── plc_io_map.md        PLC register and I/O mapping
├── scripts/
│   ├── start_all.sh         Start Mosquitto + simulators
│   └── stop_all.sh          Stop everything cleanly
└── requirements.txt
```

---

## Running it

You need: Python 3, Homebrew, Mosquitto, Ignition Maker Edition, OpenPLC Editor.

```bash
# Terminal 1 — MQTT broker
/opt/homebrew/opt/mosquitto/sbin/mosquitto -c /opt/homebrew/etc/mosquitto/mosquitto.conf

# Terminal 2 — Tank simulator
python3 simulation/tank_sim.py

# Terminal 3 — Conveyor simulator
python3 simulation/conveyor_sim.py

# Terminal 4 — File bridge to Ignition
python3 simulation/level_to_file.py

# Terminal 5 — OPC UA monitor (optional)
python3 protocols/opcua_client.py
```

Then open the HMI at `http://localhost:8088/data/perspective/client/bottling_line`

---

## PLC logic

The tank control logic mirrors what's in the OpenPLC Structured Text program:

- Level drops below 20% → open inlet valve
- Level rises above 80% → close inlet valve
- Level hits 90% → open outlet valve + fire overflow alarm
- Bottle filling active → drain 10 L/min from tank
- Interlock: filler skips if tank below 30%
- Bottle cycle: arrives every 5 seconds, fills for 3 seconds

---

## What I learned building this

Getting industrial software to talk to each other on a consumer Mac is genuinely difficult. Docker images for OpenPLC either didn't support Apple Silicon or had broken compilers. Ignition's REST API wasn't straightforward for tag writes. The file-bridge approach for pushing Python data into Ignition was a pragmatic workaround that actually works well in practice.

The most valuable insight: in real industrial systems, the PLC is the single source of truth for control decisions. Sensors feed it data, the HMI just displays what the PLC decided. Getting that data flow right — even in simulation — made the protocol stack make a lot more sense.

---

## Tools

Python 3 · paho-mqtt · opcua · pymodbus · Mosquitto · OpenPLC Editor · Ignition Maker 8.3.7 · Docker Desktop · VS Code

---

## Why I built this

Targeting automation engineering roles in Germany — Siemens, Beckhoff, Phoenix Contact. The German automation industry runs on OPC UA, IEC 61131-3, and increasingly MQTT/Sparkplug B. This project covers all of them in a way that's actually demonstrable.