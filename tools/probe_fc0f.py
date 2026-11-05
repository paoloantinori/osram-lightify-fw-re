#!/usr/bin/env python3
"""Send an osram_raw probe command to an OSRAM bulb through the Z2M external converter.

Usage:
  python3 probe_fc0f.py <friendly_name> <cmd_id>
  cmd 0 = read probe (harmless, expect 0x1234 reply)
  cmds 9, 10 (0x0A) mutate persistent NVM state: require --dangerous

Credentials come from env (PROBE_MQTT_HOST/USER/PASS); never hardcoded.
Prints every message observed after the send (timestamped), and the process
exits non-zero if no evidence of delivery is seen.
"""
import json, os, re, sys, time
import paho.mqtt.client as mqtt

HOST = os.environ.get("PROBE_MQTT_HOST", "192.168.20.110")
PORT = int(os.environ.get("PROBE_MQTT_PORT", "1883"))
USER = os.environ.get("PROBE_MQTT_USER")
PW = os.environ.get("PROBE_MQTT_PASS")

DANGEROUS = {9, 10}


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    dev = sys.argv[1]
    raw = sys.argv[2]
    if not re.fullmatch(r"(0[xX][0-9a-fA-F]+|[0-9]+)", raw):
        sys.exit(f"rejecting non-numeric command {raw!r}")
    cmd = int(raw, 0)
    if cmd in DANGEROUS and "--dangerous" not in sys.argv:
        sys.exit(f"cmd {cmd} mutates persistent device state; pass --dangerous to confirm")
    if not USER or not PW:
        sys.exit("set PROBE_MQTT_USER / PROBE_MQTT_PASS in the environment")

    events = []  # (monotonic_time, topic, payload): appended, never overwritten
    connack = {}

    def on_connect(c, u, f, rc, props=None):
        if isinstance(rc, int):
            connack["rc"] = rc
        else:
            connack["rc"] = 0 if not getattr(rc, "is_failure", True) else 1
    def on_msg(c, u, m):
        events.append((time.monotonic(), m.topic, m.payload.decode(errors="replace")[:400]))
    def on_disconnect(c, u, f, rc, props=None):
        connack.setdefault("disc", rc)

    c = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="probe-%d" % int(time.time() * 1000 % 1e9))
    c.on_connect, c.on_message, c.on_disconnect = on_connect, on_msg, on_disconnect
    c.username_pw_set(USER, PW)
    c.connect(HOST, PORT, 10)
    c.loop_start()
    t0 = time.monotonic()
    while time.monotonic() - t0 < 5 and "rc" not in connack:
        time.sleep(0.2)
    rc = connack.get("rc", -1)
    if rc != 0:
        c.loop_stop()
        sys.exit(f"MQTT CONNACK refused rc={rc}: command NOT sent")
    c.subscribe([("zigbee2mqtt/bridge/logging", 0), ("zigbee2mqtt/" + dev, 0),
                 ("zigbee2mqtt/bridge/#", 0)])
    time.sleep(1)
    sent_at = time.monotonic()
    c.publish(f"zigbee2mqtt/{dev}/set", json.dumps({"osram_raw": cmd}))
    while time.monotonic() - sent_at < 25:
        time.sleep(0.5)
    c.loop_stop()
    c.disconnect()

    post = [e for e in events if e[0] > sent_at]
    print(f"--- {len(post)} messages AFTER the send (stale pre-send messages ignored):")
    delivered = False
    for ts, t, v in post:
        print(f"{ts - sent_at:6.1f}s {t} -> {v}")
        if t.endswith("/" + dev) and "osram_raw_last" in v:
            delivered = True
    if not delivered:
        print("NO EVIDENCE OF DELIVERY (no post-send state update): treat as not executed")
        sys.exit(2)


if __name__ == "__main__":
    main()
