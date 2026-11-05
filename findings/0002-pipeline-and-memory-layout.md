# Finding 0002: pipeline, SoC class and flash memory layout

**Date**: 2026-11-05
**Artifact**: cla60_w_clear_payload.bin (SHA-256 b5fe2c77c08ab676fa39a809e90530c22a44202aa19d3ae0db5ae35e48e2188f)

## Pipeline

The payload is a raw Cortex-M Thumb image; Ghidra raw import (ARM:LE:32:v7)
disassembles it in ARM mode and produces junk unless functions are reached
through Thumb pointers. The working pipeline wraps the payload in a minimal
ELF32 ARM file with an ODD entry point (base+0x21) and EABI5 flags, then
disassembles with llvm-objdump forcing `thumbv7m-none-eabi`. 659 functions
index cleanly from push{lr}..pop{pc} pairs. See tools/.

## SoC class

Cortex-M confirmed by literal constants in code: NVIC ISER/ICER/IPR at
0xE000E100 / 0xE000E180 / 0xE000E280, plus 0xE0002000 (DWT control).

## Flash layout (inferred from pointers)

- The image links at base 0x100020 after a 32-byte firmware header
  (word 0 at offset 8 is the payload length 0x1DF78; word 3.. header
  fields; identity strings from 0xd80).
- 869 four-byte words in the payload point into 0x100020-0x11DFB8 (self,
  consistent) and 679 words point into 0x11E000-0x120000: an 8 KB persistent
  region immediately after the OTA-served app.
- The OTA file has four sub-elements: 0x0000 (the app), 0xFF01 (516 B),
  0xFF3E (504 B), 0xFF46 (8 B). The latter three are signature/certificate
  material, not code.

The persistent region is NOT shipped in the OTA. It contains, among other
things:

- the ZCL attribute/command permission tables (a decompiled walker reads its
  table pointer from 0x11F14C and iterates 16 entries of 6 bytes:
  {u16 id, u8 flags with low 3 bits = access, u8 pad, u16 id2}),
- at least one odd (Thumb) code pointer, 0x11E6D7, so some code lives there
  too,
- install-code material: strings `ZigBeeAlliance09` and `ZggBeeAlliance09`
  sit at the payload tail next to the endpoint descriptors with a CRC table
  fragment (0xC0..0xCF).

Implication: anything table-driven (including the full command list of the
manufacturer cluster 0xFC0F) resolves into that region, so enumerating
commands from this artifact requires following the in-app code that walks
those tables, not the tables themselves. A physical dump of the 8 KB region
(from a bulb or a rooted gateway) would close the gap immediately.
