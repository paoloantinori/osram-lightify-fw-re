#!/usr/bin/env python3
"""Wrap the raw payload in a minimal ELF32 ARM file marked as Thumb.

llvm-objdump refuses raw binaries, and odd (Thumb) entry points are what tells
the disassembler to decode Thumb. The wrapper has one .text section loaded at
the given base with e_entry = base+0x21 (odd) and EABI5 e_flags. The default
base is 0x100000 and the 32-byte firmware header is skipped, per the
scatter-table anchor (see findings/0005).

Usage: python3 make_elf.py payload.bin out.elf [base]
Then: llvm-objdump --disassemble-all --triple=thumbv7m-none-eabi out.elf > full.asm
"""
import struct, sys

def build(data, base):
    EHS, PHS, SHS = 52, 32, 40
    shstr = b"\0.text\0.shstrtab\0"
    off_data = EHS + PHS
    off_shstr = off_data + len(data)
    shoff = (off_shstr + len(shstr) + 3) & ~3
    sh_null = b"\0" * SHS
    sh_text = struct.pack("<IIIIIIIIII", 1, 1, 6, base, off_data, len(data), 0, 0, 4, 0)
    sh_shstr = struct.pack("<IIIIIIIIII", 7, 3, 0, 0, off_shstr, len(shstr), 0, 0, 1, 0)
    ident = b"\x7fELF\x01\x01\x01\x00" + b"\0" * 8
    hdr = struct.pack("<HHIIIIIHHHHHH", 2, 40, 1, base + 0x21, EHS, shoff,
                      0x05000200, EHS, PHS, 1, SHS, 3, 2)
    ph = struct.pack("<IIIIIIII", 1, 4, 0, base, base, len(data), len(data), 0x1000)
    out = bytearray(ident + hdr + ph + data + shstr)
    out += b"\0" * (shoff - len(out))
    out += sh_null + sh_text + sh_shstr
    return bytes(out)

if __name__ == "__main__":
    src = sys.argv[1]
    dst = sys.argv[2] if len(sys.argv) > 2 else "payload.elf"
    base = int(sys.argv[3], 0) if len(sys.argv) > 3 else 0x100000
    open(dst, "wb").write(build(open(src, "rb").read()[32:], base)  # skip the 32-byte firmware header)
    print(f"wrote {dst} (base 0x{base:x})")
