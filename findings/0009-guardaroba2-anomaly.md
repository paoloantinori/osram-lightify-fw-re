# Finding 0009: guardaroba_2 ignores the entire 0xFC0F write path (unit anomaly)

**Date**: 2026-11-05, 20:22-20:24, controlled conditions

With the bulb as the ONLY lit one in its room (siblings and the Philips LTW010
turned off), fresh C01 re-applied, then B01 (0x0B snapshot-branch setter), one
mains cycle after each: restored ON both times (direct query + maintainer
visual). The unit also actively rejects manufacturer-specific attribute reads
(UNSUP_MANUF_GENERAL_COMMAND) since first contact. Every other tested unit
(cantina, guardaroba_1, Stella) applies the commands and accepts the reads.

Conclusion: unit 0x7cb03eaa00afa9df ignores the whole 0xFC0F read/write path
while running the same firmware version. Cause open (batch, build, or NVM
state). Fleet scoreboard: cantina solved (verified), guardaroba_1 solved
(A/B proven), Stella solved (cycle-verified), guardaroba_2 anomalous (this
finding), Scale pending (unreachable at time of campaign, MAC_NO_ACK).
