#!/usr/bin/env python3
"""Watch osram_cantina for the decisive power-cycle test (2026-11-05).

Emits one line per: device_announce (power restored), state change, and the
first full state message after any announce. The question it answers: after a
mains cycle with the bulb ON, does it come back OFF (C01 worked) or ON?
"""
import json, time
import paho.mqtt.client as mqtt

HOST, PORT = "192.168.20.110", 1883
import os
USER = os.environ.get("PROBE_MQTT_USER")
PW = os.environ.get("PROBE_MQTT_PASS")
DEV = "osram_cantina"
last_state = {}
announce_at = None

def stamp():
    return time.strftime("%H:%M:%S")

def on_connect(c, u, f, rc, props=None):
    c.subscribe([("zigbee2mqtt/bridge/event", 0), (f"zigbee2mqtt/{DEV}", 0),
                 (f"zigbee2mqtt/{DEV}/availability", 0)])
    print(f"{stamp()} MONITOR ATTIVO su {DEV}: attendo il power-cycle", flush=True)

def on_msg(c, u, m):
    global announce_at
    t = m.topic
    p = m.payload.decode(errors="replace")
    if t.endswith("bridge/event"):
        try:
            d = json.loads(p)
        except Exception:
            return
        if d.get("type") == "device_announce" and DEV in str(d.get("data", {})):
            announce_at = time.monotonic()
            print(f"{stamp()} ANNOUNCE: {DEV} ha ricevuto corrente. Stato al ritorno:", flush=True)
    elif t.endswith(f"{DEV}/availability"):
        print(f"{stamp()} availability: {p[:80]}", flush=True)
    elif t == f"zigbee2mqtt/{DEV}":
        try:
            d = json.loads(p)
        except Exception:
            return
        state = d.get("state")
        if state != last_state.get("state"):
            print(f"{stamp()} STATE: {state} (brightness {d.get('brightness')}, lqi {d.get('linkquality')})"
                  + ("   <== TORNA SPENTA: C01 FUNZIONA" if state == "OFF" and announce_at else ""), flush=True)
        last_state.update({k: d.get(k) for k in ("state", "brightness")})

c = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="pcmon%d" % int(time.time() * 1000 % 1e9))
c.on_connect = on_connect
c.on_message = on_msg
if not USER or not PW:
    raise SystemExit("set PROBE_MQTT_USER / PROBE_MQTT_PASS in the environment")
c.username_pw_set(USER, PW)
c.connect(HOST, PORT, 15)
c.loop_forever(retry_first_connection=True)
