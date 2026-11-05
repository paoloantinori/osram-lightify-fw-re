# Finding 0005: the real 0xFC0F parser, commands 0x0B/0x0C, and the C01 live result

**Date**: 2026-11-05
**Contributors**: astra (pantinor-77 session) found the base error, the scatter-table anchor, the RLE .data reconstruction and the parser; this session verified everything independently on the corrected map and ran the live probes. Static proof bundle by astra: ~/claudedocs/osram_astra_proof_2026-11-05.txt; assessment: research_osram-lightify-assessment_2026-11-05.md.

## Map correction (supersedes parts of findings 0002 and 0004)

- The load base was WRONG in findings 0001-0004: the app code (payload after the
  32-byte firmware header) links at 0x100000, not 0x100020. All addresses
  published before 2026-11-05 17:00 are +0x40 too high. The anchor: the runtime
  scatter table at 0x100040 whose relative entries resolve exactly onto the
  zero-init routine (0x105FDA) and the Thumb decompressor (0x11D6EE) under the
  corrected base.
- The "persistent flash region 0x11E000-0x120000 not served in OTA" claim is
  RETRACTED: that range is .data (an RLE-compressed block, in_len 0x3C6,
  decompressed at boot into 0x11DF78 for 0x767 bytes) plus .bss (zeroed from
  0x11E6E0, length 0x14A8). The 679 out-of-image pointers are normal
  references to RAM globals. No missing flash exists.
- Corrected artifacts: disasm/full_thumb.asm (regenerated at base 0x100000),
  disasm/func_index.json.

## The real parser and the two new commands

The actual 0xFC0F command parser is at 0x1041C6 (found via the reconstructed
.data descriptor). It dispatches EIGHT command IDs: 0, 1, 2, 4, 9, 0x0A go
through the application callback (the function previously published as the
whole dispatcher, actually the callback at 0x100B92); 0x0B and 0x0C are
handled in the parser itself:

- **cmd 0x0B** (payload 1/2/3): writes the snapshot-branch state: payload 01
  sets persisted on/off (config 0x11F817) = 0 (OFF), payload 03 = 1 (ON),
  payload 02 leaves it (snapshot current). Also sets flag 0x11F819. NVM commit.
- **cmd 0x0C** (payload 1/3): writes the fallback-branch state: payload 01
  sets u16 config+0xC = 0 AND flag 0x11F804 (= config+0x10) = 1; payload 03
  sets u16+0xC = 1 and the flag = 1. NVM commit.

Boot applier at 0x100120: if magic 0xAA at config+0x24 (written only by the
OTA upgrade-end path per astra) it restores the snapshot on/off at +0x23
(= 0x11F817, the SAME byte cmd 0x0B writes); otherwise the fallback branch:
if flag +0x10 == 1 restore u16+0xC, else DEFAULT ON. The always-on behavior
of stock bulbs is the flag=0 default branch.

## Live result (osram_cantina, 2026-11-05)

- Baseline read of FC0F attributes 0-7: {0:52, 1:0, 2:0, 3:0, 4:1, 5:0, 6:3,
  7:0}. attr7 = 0 confirms the default-ON branch live.
- C01 sent (cmd 0x0C payload 01).
- Post read: {4:1, 5:0, 6:3, 7:1}. attr7 0->1 and attr5 = 0: exactly the
  predicted fallback-OFF state (flag=1, saved value=0).
- Evidence: evidence/probe-C01-osram_cantina_2026-11-05.txt and
  evidence/converter-console-logs_2026-11-05.txt (converter stdout =
  endpoint.read() return values; raw ZCL frames not captured; declared).

## Status

Power-on restore of OFF after a mains cycle is PREDICTED and staged but NOT
VERIFIED: the decisive test is a power cycle with the bulb ON; it must come
back OFF. Rollback note: cmd 0x0C payload 03 restores default ON but leaves
the flag at 1 (not byte-identical); cmd 0x02 does not revert B/C.
