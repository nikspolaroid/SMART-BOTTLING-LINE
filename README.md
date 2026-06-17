# 🏭 Smart Bottling Line — PLC + HMI + SCADA on macOS

Built entirely on macOS Apple Silicon M2. No hardware required.

## 🎯 What this project does
- Tank fills with liquid at a controlled rate
- Conveyor moves bottles into position
- Sensors detect level, temperature and flow
- PLC logic controls fill sequences and alarms
- HMI displays live process state in browser (coming soon)

## 📋 Development phases

| Phase | What we build | Status |
|---|---|---|
| 1 | Environment setup — Homebrew, Mosquitto, Python, Docker, OpenPLC | ✅ Done |
| 2 | Process simulation — tank_sim.py, conveyor_sim.py | ✅ Done |
| 3 | PLC logic — Structured Text in OpenPLC simulator | ✅ Done |
| 4 | Protocols — OPC UA client, Modbus TCP | 🔄 In progress |
| 5 | HMI — Ignition Maker Edition | ⏳ Upcoming |
| 6 | Polish — fault injection, portfolio | ⏳ Upcoming |

## 🧰 Tech stack

| Tool | Role | Status |
|---|---|---|
| Python 3 | Process simulation | ✅ |
| paho-mqtt | MQTT client | ✅ |
| Mosquitto | MQTT broker | ✅ |
| OpenPLC Editor | PLC programming + simulator | ✅ |
| Docker Desktop | Container runtime | ✅ |
| Ignition Maker | HMI + SCADA | ⏳ |

## 🚀 Quick start
```bash
git clone https://github.com/nikspolaroid/PLC-PROJECT_1.git
cd PLC-PROJECT_1
pip3 install paho-mqtt
python3 simulation/tank_sim.py
python3 protocols/mqtt_monitor.py
```

## 👤 Author
Learning project for Industry 4.0 automation engineering roles in Germany.