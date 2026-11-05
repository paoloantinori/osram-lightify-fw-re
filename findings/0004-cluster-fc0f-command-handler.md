# CORRECTION 2026-11-05 (post adversarial review by astra, verified mechanically)

Two semantic claims in this finding are retracted/corrected:

1. The boot path description was imprecise. 0x103E96 does NOT embed the 3-bit
   mode into the callback object word: it stores a FUNCTION POINTER (literal
   0x10A989, a pointer table at 0x10A988) into the local's first word, and the
   masked mode (config[0x24]&7) goes into a separate stack word; the sequence
   tail-calls ROM helper 0x60C8 with the mode as argument. Reading: callback
   registration into the ROM scheduler with the mode as callback argument, not
   a "power-on event with embedded mode".
2. The claim that 0x10A9C8 reports the mode as an attribute is RETRACTED: it
   feeds ROM 0x60C8, not the ZCL send helper 0x1031EC (which is what the
   dispatcher uses at 0x100BCE/0x100C38).

Unchanged and re-verified after the base-shift challenge: load base 0x100020
stands (pointer-literal vs function-start alignment histogram shows exact
delta-0 hits and no 0x40 dominance; the two candidate -0x40 pointers resolve
to a data pointer-table at 0x10A988 and to a branch-skipped div-helper entry
at 0x100B92, not to shifted copies of published functions). The dispatcher
itself, the save/reset paths, the 0xAA magic write and the undocumented
commands 0/9/0x0A are unaffected. The cmd-0 branch remains NOT proven to have
executed in the live probe.

---

# Finding 0004: the manuSpecificOsram (0xFC0F) command handler and its undocumented commands

**Date**: 2026-11-05
**Artifact**: cla60_w_clear_payload.bin, function at 0x100BD2 (dispatch), persistent struct at 0x11F7F4

## The handler

Function 0x100BD2 (push {r4,r5,lr}) dispatches on its first argument, which
behaves as the 0xFC0F command ID. It is the only place in the whole image
where the immediate 0xFC0F appears in code (movw r0,#0xfc0f at 0x100C34,
feeding ZCL-send helper 0x1031EC, the same helper used for genOnOff reports
with cluster 6 at 0x100BCE).

The handler writes a persistent config block at 0x11F7F4 (0x28 bytes, the
same size malloc'd at boot for the config shadow copy) and commits it to NVM
via 0x104536 after every state change.

## Confirmed known commands

- **cmd 1 (saveStartupParams)** at 0x100C40: if [ctx+0x12] set and
  config[0x25]==2, writes config[0x23] from the message; then
  `config[0x24] = 0xAA`; `config[0x1C]` from the message; NVM save; clears
  [ctx+0x12]. The 0xAA byte is the "startup params valid" magic: at boot the
  firmware reads config[0x24], masks it with 7 (yielding 2 when saved), and
  feeds it into the power-on restore event (boot init 0x11C1D2 →
  0x103E96(mode,&local) → 0x1126B0(&local) → event enqueue). 0x10A9C8 also
  reports (config[0x24]&7)|0x20 through the same send helper, i.e. the
  persisted power-on mode is exposed as an attribute.
- **cmd 2 (resetStartupParams)** at 0x100C88: zeroes the u16 at config[0x0A]
  and commits to NVM.

## Undocumented commands

- **cmd 0** at 0x100C1E: replies on cluster 0xFC0F with the 2-byte payload
  `0x12 0x34`. Looks like a probe/identify exchange the gateway uses.
- **cmd 0x0A** at 0x100C92: calls 0x100A46, then a nibble state machine on
  config[0x11]: if low nibble == 3, writes 0x53 ('S') there and commits; if
  low nibble == 5, manipulates [ctx+0x0B] (0xFF sentinel handling, calls
  0x100D28/0x100D04) and reports through 0x101628.
- **cmd 9** at 0x100CCC: mirrors the same config[0x11] state machine: low
  nibble 5 → [ctx+0x0B] handling; low nibble 3 → writes 0x33 there and
  commits.

config[0x11] carries a two-nibble state (observed writes 0x53 and 0x33; reads
compare low nibble against 3 and 5). Semantics not yet decoded; candidates
are commissioning/touchlink phases or the OSRAM "gateway ownership" state.

## Why this matters for the power-on problem

The power-on restore reads config[0x24]&7 (mode 2 after a save). The restore
event built at boot (0x1126B0, 0x45-byte event struct, fields +0x14/+0x18/
+0x20 copied from a local whose word 0 embeds the 3-bit mode) is consumed by
the queue the scheduler loop (0x4660) drains. The on/off decision lives in
that consumer. Next step: find the event consumer and check whether any mode
value (0..7, some reachable through the undocumented commands) restores the
bulb to OFF.

## Caveats

- The dispatch-on-first-arg reading rests on the match of selectors 1 and 2
  with the community-documented save/reset commands and on the NVM commit
  pattern; selectors 0/9/0xA are labeled as command IDs under the same
  reading.
- The identity of struct 0x11F7F4 as the block behind boot-time pointer cell
  0x11FA34 is inferred from the matching 0x28 size and the magic byte
  semantics, not yet proven by following the NVM layer (0x103BF4/0x104536).
