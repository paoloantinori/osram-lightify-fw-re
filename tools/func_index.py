#!/usr/bin/env python3
"""Index Thumb functions from an llvm-objdump listing and annotate an address range.

A function starts at `push {.., lr}` and ends at the matching `pop {.., pc}`.
For each function in the requested range the tool reports:
  - size and extent
  - literal words pointing into the persistent region (0x11E000-0x120000 by
    default: tables and code NOT shipped in the OTA payload)
  - references to known identity strings
  - bl call targets

Usage: python3 func_index.py full.asm payload.bin 0x10e020 0x112020 > map.md
"""
import re, struct, sys

BASE = 0x100020

def main():
    asm_path, bin_path = sys.argv[1], sys.argv[2]
    lo = int(sys.argv[3], 0) if len(sys.argv) > 3 else 0
    hi = int(sys.argv[4], 0) if len(sys.argv) > 4 else 0xFFFFFFFF
    d = open(bin_path, "rb").read()
    lines = open(asm_path).read().splitlines()
    addr_re = re.compile(r"^\s*([0-9a-f]+):\s")
    funcs, cur = [], None
    seg = {}
    last = None
    for ln in lines:
        m = addr_re.match(ln)
        if m:
            last = int(m.group(1), 16)
            if re.search(r"push\s+\{[^}]*lr\}", ln) and cur is None:
                cur = last
        if last is not None:
            seg.setdefault(last, []).append(ln)
        if re.search(r"pop\s+\{[^}]*pc\}", ln) and cur is not None:
            funcs.append((cur, last)); cur = None
    print(f"# {len(funcs)} functions indexed; range 0x{lo:x}-0x{hi:x}")
    print("")
    for s, e in funcs:
        if not (lo <= s <= hi):
            continue
        blob = d[s - BASE:e - BASE + 2]
        notes = []
        for o in range(0, max(0, len(blob) - 3), 2):
            w = struct.unpack_from("<I", blob, o)[0]
            if 0x11E000 <= w <= 0x120000:
                notes.append(f"PTR-PERSIST 0x{w:08x}")
                break
        calls = sorted({int(m.group(1), 16) for ln in seg.get(s, [])
                        if (m := re.search(r"\bbl\w*\s+0x([0-9a-f]+)", ln))})
        print(f"## 0x{s:08x}-0x{e:08x} ({e - s + 2}B)" + (" | " + " ".join(notes) if notes else ""))
        if calls:
            print("- calls: " + ", ".join(f"0x{c:08x}" for c in calls[:8]))
        print("")

if __name__ == "__main__":
    main()
