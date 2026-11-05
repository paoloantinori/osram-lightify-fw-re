# CORRECTION 2026-11-05 (astra caught a conflation): the cluster IS declared

The original note implied the 0xFC0F cluster was absent from the unit's
descriptor. Wrong: the simple descriptor (inClusterList, from the device) is
IDENTICAL on all three A60s and INCLUDES 64527 (0xFC0F). What is missing on
guardaroba_2 is Z2M's per-cluster CACHE entry (created on first successful
interaction): its reads have never succeeded, so no cache. The earlier table
was built from that cache, not from the descriptor.

Corrected facts: the V1.04.12 firmware DECLARES 0xFC0F but refuses
manufacturer-specific reads (UNSUP_MANUF_GENERAL_COMMAND, live) and ignores
commands 0x0B/0x0C (two controlled power-cycle tests, finding below). So the
older build implements the cluster differently, likely without the
0x0B/0x0C/0x00/9/A command set the V1.05.10 parser handles. This dovetails
with the documentation history: the 2020 sniffing (V1.04-era bulbs) only ever
saw commands 0x01/0x02, which matches an older, smaller command set; the
power-on setters plausibly arrived with V1.05.x. Firmware confirmation would
require a V1.04.12 artifact, not available publicly.

---

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
