# Finding 0001: the ZLL_MK OSRAM OTA images are plaintext firmware

**Date**: 2026-11-05
**Artifact**: ZLL_MK_0x01020510_CLA60_W_CLEAR.ota (AC03641, LIGHTIFY Classic A60 W clear)

The zigbee-OTA index hosts two families of OSRAM images. The `A60_DIM_Z3_*`
files are fully encrypted end to end (entropy 7.99 on the whole sub-element,
no visible structure). The `ZLL_MK_*` files are not: the sub-element 0x0000
payload of ZLL_MK_0x01020510_CLA60_W_CLEAR.ota is 122,776 bytes of plaintext
ARM Thumb code with entropy 6.79 and readable identity strings.

Identity block at payload offset 0xd80-0xe60:

- `OSRAM`
- `V1.05.10`
- `Classic A60 W clear - LIGHTIFY`
- `20140331CNEF****`

A second identity string at offset 0xfc6c:

- `OSRAMIQL&BCLASSIC_A60_W_CLEAR_1.05.10#`

OTA header of the file: manufacturer 0x110C, imageType 19, fileVersion
0x01020510. Z2M matches this exact image when checking updates for an AC03641
and reports `update_available: false` on firmware 0x01020510, i.e. the
analyzed image IS the latest official firmware for these bulbs, and the same
major version the fleet runs.

Practical consequence: full static analysis (disassembly, decompilation) of
the exact firmware that runs on AC03641 bulbs is possible from a public
artifact. The earlier community claim that OSRAM firmware cannot be analyzed
comes from the encrypted A60_DIM_Z3 family and does not generalize.
