# simulation/config.py
# Shared configuration for all simulators and protocol clients

# ── MQTT broker ──────────────────────────────────────────────
MQTT_BROKER   = "localhost"
MQTT_PORT     = 1883
MQTT_QOS      = 1          # At least once delivery

# ── MQTT topics ──────────────────────────────────────────────
# Sensors publish to these topics
TOPIC_TANK_LEVEL      = "bottling/tank/level"        # float  0.0–100.0 %
TOPIC_TANK_TEMP       = "bottling/tank/temperature"  # float  °C
TOPIC_TANK_FLOW_IN    = "bottling/tank/flow_in"      # float  L/min
TOPIC_TANK_FLOW_OUT   = "bottling/tank/flow_out"     # float  L/min

TOPIC_CONVEYOR_SPEED  = "bottling/conveyor/speed"    # float  m/min
TOPIC_CONVEYOR_COUNT  = "bottling/conveyor/count"    # int    bottles filled
TOPIC_CONVEYOR_STATE  = "bottling/conveyor/state"    # str    running/stopped/fault

TOPIC_ALARM_OVERFLOW  = "bottling/alarm/overflow"    # bool   1/0
TOPIC_ALARM_UNDERFLOW = "bottling/alarm/underflow"   # bool   1/0
TOPIC_ALARM_FAULT     = "bottling/alarm/fault"       # str    fault description

# ── PLC (OPC UA) ──────────────────────────────────────────────
OPC_UA_URL    = "opc.tcp://localhost:4840"

# ── PLC (Modbus TCP) ──────────────────────────────────────────
MODBUS_HOST   = "localhost"
MODBUS_PORT   = 502

# ── Simulation parameters ─────────────────────────────────────
PUBLISH_INTERVAL_S    = 0.5    # How often simulators publish (seconds)
TANK_MAX_VOLUME_L     = 1000   # Litres
TANK_FILL_RATE_L_MIN  = 50     # Litres per minute (inlet)
TANK_DRAIN_RATE_L_MIN = 40     # Litres per minute (outlet/filler)
TANK_HIGH_ALARM       = 90.0   # % level → overflow alarm
TANK_LOW_ALARM        = 10.0   # % level → underflow alarm
