# Finding 0006: VERIFIED. C01 makes the AC03641 restore OFF after a power cycle

**Date**: 2026-11-05, 19:17 local
**Test**: osram_cantina, protocol ON-before-cycle (discriminates default-OFF
from last-state restore), physical mains cycle by the maintainer.

- 19:16:31 bulb ON, brightness 254 (presence sensor)
- 19:17:37 device announce (power restored)
- 19:17:39 state OFF, brightness 254
- maintainer visual confirmation: OFF
- post-reboot FC0F attrs {4:1, 5:0, 6:3, 7:1}: the persisted config survived
  the reboot; the setting is durable

The command: cluster manuSpecificOsram (0xFC0F), manufacturer code 0x110C,
command 0x0C, payload byte 0x01. In Z2M terms it is reachable with a small
external converter (see evidence/ and tools/ in this repo).

Fleet status at publication: cantina VERIFIED physically; guardaroba_1 applied
and attribute-verified; guardaroba_2 sent, bulb actively rejects verification
reads (UNSUP_MANUF_GENERAL_COMMAND), physical verification pending.

This closes the original problem for the OSRAM LIGHTIFY Classic A60 W clear
family: the always-on-after-blackout behavior is a config default (fallback
branch flag=0), not a hard limit, and it is switchable over the air.
