# Finding 0007: proof and counter-proof on guardaroba_1 (causality closed)

**Date**: 2026-11-05, 20:03-20:07 local, maintainer-operated power cycles

Protocol: bulb turned ON by direct MQTT (bypassing the presence automations),
continuous surveillance of the device set-topic (every external command logged),
single mains cut per run.

- C01 config (flag=1, saved=OFF): cycle at 20:03:37, restored OFF at 20:03:39
  with ZERO external commands between announce and state (the presence
  automation's ON at 20:02:57 was logged BEFORE the cut; its OFF came at
  20:06:49 in the next run).
- C03 config (flag=1, saved=ON, applied 20:03:56, attrs {4:1,5:1,6:3,7:1}):
  cycle at 20:06:11, restored ON (maintainer visual + direct state query).

Same bulb, same protocol, only the two-byte command differs, opposite
outcomes: the power-on behavior is causally controlled by cluster 0xFC0F
command 0x0C. Evidence: evidence/PROVA-CONTROPROVA-guardaroba_1_2026-11-05.txt

Fleet at close: cantina C01 (verified), guardaroba_1 C01 (proven A/B, left in
place), guardaroba_2 C01 not effective (that unit actively rejects
manufacturer reads, UNSUP_MANUF_GENERAL_COMMAND; unit-specific anomaly, open).
