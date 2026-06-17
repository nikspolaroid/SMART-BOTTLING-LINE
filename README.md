# 🏭 Smart Bottling Line — PLC + HMI + SCADA on macOS

A fully simulated industrial automation project built entirely on macOS.
No hardware required. Covers real PLC logic, industrial networking protocols,
and a browser-based HMI — the same stack used in modern German industry (Siemens, Beckhoff, Phoenix Contact).

---

## 🎯 What this project does

Simulates a bottling plant production line:
- A **tank** fills with liquid at a controlled rate
- A **conveyor** moves bottles into position under the filler
- **Sensors** detect level, temperature, and flow
- **PLC logic** controls fill sequences, interlocks, and alarms
- **HMI** displays live process state in a browser
- **SCADA** logs history, manages alarms, and generates reports

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│     Layer 4 — HMI / SCADA              │
│     Ignition Maker Edition              │
│     Perspective HMI · Alarms · Trends  │
└────────────┬────────────────────────────┘
             │ OPC UA (port 4840)
┌────────────▼────────────────────────────┐
│     Layer 3 — Protocol Layer           │
│     MQTT (Mosquitto :1883)             │
│     OPC UA (OpenPLC built-in)          │
│     Modbus TCP (port 502)              │
└────────────┬────────────────────────────┘
             │ virtual I/O tags
┌────────────▼────────────────────────────┐
│     Layer 2 — Soft PLC                 │
│     OpenPLC Runtime (Docker)           │
│     IEC 61131-3 Ladder + ST logic      │
└────────────┬────────────────────────────┘
             │ MQTT sensor data
┌────────────▼────────────────────────────┐
│     Layer 1 — Process Simulation       │
│     Python scripts                     │
│     Tank · Conveyor · Sensors          │
└─────────────────────────────────────────┘
```

---

## 🧰 Tech stack

| Tool | Role | Version |
|---|---|---|
| Python 3.11+ | Process simulation | `python --version` |
| paho-mqtt | MQTT client library | 1.6.x |
| Docker Desktop | Runs OpenPLC container | latest |
| OpenPLC Runtime | Soft PLC (IEC 61131-3) | v3 |
| OpenPLC Editor | Write Ladder / ST programs | latest |
| Mosquitto | MQTT broker | 2.x |
| Ignition Maker | HMI + SCADA + historian | 8.x |
| MQTT Explorer | Debug MQTT messages | latest |
| VS Code | Editor | latest |

---

## 📡 Protocols covered

| Protocol | Port | Role |
|---|---|---|
| MQTT | 1883 | Sensor data (pub/sub) |
| OPC UA | 4840 | PLC tag access (client/server) |
| Modbus TCP | 502 | Register reads from Ignition |
| HTTP/WebSocket | 8088 | Ignition Perspective HMI |

---

## 📁 Project structure

```
smart-bottling-line/
├── simulation/           # Python process simulators
│   ├── tank_sim.py       # Tank fill/drain simulation
│   ├── conveyor_sim.py   # Conveyor belt + bottle counter
│   ├── sensor_sim.py     # Temperature, flow, level sensors
│   └── config.py         # Shared MQTT config
├── plc/                  # OpenPLC programs
│   ├── tank_control.st   # Structured Text — tank fill logic
│   ├── conveyor.st       # Conveyor sequence logic
│   └── alarms.st         # Alarm detection logic
├── protocols/            # Protocol test clients
│   ├── mqtt_monitor.py   # Subscribe and print all topics
│   ├── opcua_client.py   # Read PLC tags via OPC UA
│   └── modbus_client.py  # Read registers via Modbus TCP
├── hmi/                  # Ignition project exports + docs
│   └── screens/          # HMI screen design notes
├── docs/                 # Architecture diagrams, notes
│   ├── architecture.md
│   ├── mqtt_topics.md
│   └── plc_io_map.md
├── scripts/              # Helper shell scripts
│   ├── start_all.sh      # Start broker + Docker + simulators
│   └── stop_all.sh       # Stop everything cleanly
├── docker-compose.yml    # OpenPLC container config
├── requirements.txt      # Python dependencies
└── README.md
```

---

## 🚀 Quick start

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/smart-bottling-line.git
cd smart-bottling-line
```

### 2. Install Python dependencies
```bash
pip install -r requirements.txt
```

### 3. Start Mosquitto broker
```bash
brew services start mosquitto
```

### 4. Start OpenPLC (Docker)
```bash
docker-compose up -d
# OpenPLC dashboard → http://localhost:8080
```

### 5. Run the process simulator
```bash
python simulation/tank_sim.py
```

### 6. Open Ignition
```
http://localhost:8088
```

---

## 📋 Development phases

| Phase | What we build | Status |
|---|---|---|
| 1 | Environment setup — Docker, Mosquitto, Python, Ignition | ✅ Done |
| 2 | Process simulation — tank_sim.py, conveyor_sim.py | 🔄 In progress |
| 3 | PLC logic — Ladder + ST in OpenPLC | ⏳ Upcoming |
| 4 | Protocols — OPC UA client, Modbus client | ⏳ Upcoming |
| 5 | HMI design — Ignition Perspective screens | ⏳ Upcoming |
| 6 | Polish — fault injection, data export, portfolio | ⏳ Upcoming |

---

## 🤝 Commit convention

Every commit follows this format:
```
[phase-N] short description of what was added

Examples:
[phase-1] add docker-compose for OpenPLC
[phase-2] add tank simulator with MQTT publish
[phase-3] add ladder logic for fill sequence
```

---

## 📚 Learning resources

- [OpenPLC Documentation](https://openplcproject.com)
- [Ignition Maker Edition](https://inductiveautomation.com/ignition/maker-edition)
- [Inductive University (free SCADA training)](https://inductiveuniversity.com)
- [MQTT Essentials](https://www.hivemq.com/mqtt-essentials/)
- [OPC UA Specification](https://opcfoundation.org/about/opc-technologies/opc-ua/)

---

## 👤 Author

Built as a learning project for industrial automation engineering.
Stack targets skills relevant to Industry 4.0 roles in Germany.
