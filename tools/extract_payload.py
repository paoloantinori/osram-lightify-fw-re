#!/usr/bin/env python3
"""Extract the app payload from an OSRAM ZLL_MK Zigbee OTA file.

Downloads (or reads a local copy of) one of the plaintext OSRAM images hosted in
Koenkk/zigbee-OTA and dumps the sub-element 0x0000 payload, plus a parse of all
sub-elements.

Usage:
  python3 extract_payload.py [ota-file-or-url] [out.bin]
Default target: ZLL_MK_0x01020510_CLA60_W_CLEAR.ota (OSRAM LIGHTIFY Classic A60
W clear, the AC03641 family).
"""
import struct, sys, urllib.request

DEFAULT_URL = ("https://raw.githubusercontent.com/Koenkk/zigbee-OTA/master/"
               "images/Osram/ZLL_MK_0x01020510_CLA60_W_CLEAR.ota")

def load(src):
    if src.startswith("http"):
        print(f"downloading {src}")
        return urllib.request.urlopen(src, timeout=60).read()
    return open(src, "rb").read()

def main():
    src = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_URL
    out = sys.argv[2] if len(sys.argv) > 2 else "cla60_w_clear_payload.bin"
    d = load(src)
    magic, hv, hl, fc, manuf, img = struct.unpack("<IHHHHH", d[:14])
    fv, sv = struct.unpack("<IH", d[14:20])
    hs = d[24:56].split(b"\0")[0].decode(errors="replace")
    print(f"magic={magic:#x} manuf={manuf:#x} imageType={img} fileVersion={fv:#x} headerString={hs!r}")
    off, payload = hl, None
    while off < len(d) - 6:
        tag, ln = struct.unpack("<HI", d[off:off + 6])
        print(f"sub-element @ {off}: tag=0x{tag:04x} len={ln}")
        if tag == 0x0000 and payload is None:
            payload = d[off + 6:off + 6 + ln]
        off += 6 + ln
    if payload is None:
        sys.exit("no 0x0000 sub-element found")
    open(out, "wb").write(payload)
    print(f"wrote {out} ({len(payload)} bytes); load base 0x100020, entry 0x100020+0x20")

if __name__ == "__main__":
    main()
