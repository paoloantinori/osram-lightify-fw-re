# Finding 0003: the OSRAM application quarter

**Date**: 2026-11-05
**Artifact**: cla60_w_clear_payload.bin, address window 0x10E020-0x112020 (payload file offsets 0xE000-0x12000)

85 functions index in this window; the region contains the second identity
string and code with OSRAM-specific logic. Full listing in
[disasm/MAP_quarter.md](../disasm/MAP_quarter.md).

## Endpoint registration (payload tail)

At payload offset 0x1DE80 the endpoint descriptor lists input clusters:
0003 (Identify), 0004 (Groups), 0005 (Scenes), 0006 (OnOff), 0008 (Level),
**0xFC0F (manuSpecificOsram)**. The ZCL implementation tables for these
clusters point into the persistent region (finding 0002).

## Functions worth reading first

- 0x10FC8C: second identity string `OSRAMIQL&BCLASSIC_A60_W_CLEAR_1.05.10#`.
  Immediately after it, a small Thumb function (push at ~0x10FCB4) classifies
  an input byte against 'J' (0x4A), 'P' (0x50), 'R' (0x52), 'S' (0x53),
  'o' (0x6F) and 0xFF, returning distinct small codes (1/2/4/8 pattern).
  Candidate: product-family or manufacturer-protocol parser. Unconfirmed.
- 0x10E518-0x10E6A8 (402 B): references persistent table 0x11F107.
- 0x10F734-0x10F81C (234 B): references persistent table 0x11F200.
- 0x10FAF8-0x10FC86 (400 B): references persistent table 0x11FAA4, sits right
  before the identity string; strong candidate for OSRAM cluster handling.
- 0x1113E4-0x11175E (892 B): references 0x11E5E4.
- 0x111F3E-0x112366 (1066 B): references 0x11E698.
- Large init function 0x102D00-0x103540 registers the endpoints (literals
  0x11DF78 / 0x11DFA0) and is the entry path for boot-time restore logic.

## Ruled out

The 1-vs-2 dispatch at 0x103508 returns ZCL stack status codes
(0x300000F / 0x30000C), not handlers: it is NOT the saveStartupParams /
resetStartupParams switch despite the tempting shape.

## Next

Read 0x10FAF8 and the classifier after 0x10FCB4 against the Z2M-documented
behavior of cluster 0xFC0F; walk the init function for calls that read the
persistent region at boot (power-on restore).
