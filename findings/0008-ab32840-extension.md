# Finding 0008: C01 works on the AB32840 (Classic B40 TW) too

**Date**: 2026-11-05, 20:17-20:20

The external converter was extended to zigbeeModel "Classic B40 TW - LIGHTIFY"
(AB32840). Stella (staircase bulb): baseline FC0F attrs {4:1,5:0,6:3,7:0}
(attr7=0, same default-ON profile as the A60 family), C01 applied, post-read
{4:1,5:0,6:3,7:1} (attr7 0->1), maintainer power cycle at 20:19:37, restored
OFF (visual + direct query). Caveat: this cycle started from OFF, so alone it
does not discriminate default-OFF from last-state restore; the discrimination
is already proven by the guardaroba_1 A/B (finding 0007). Scale (the other
AB32840) is currently unreachable (MAC_NO_ACK, marginal mesh child): C01
pending for it.

Fleet status after tonight: cantina AC03641 C01 (verified 19:17 + attrs),
guardaroba_1 AC03641 C01 (A/B proven, in place), guardaroba_2 AC03641 C01
sent, unit rejects verification reads and its post-cycle state report may
have been cache; the room also holds a Philips LTW010 (Guardaroba_3) which
may have been the "one bulb on" during the first cycle, Stella AB32840 C01
(cycle-verified), Scale AB32840 pending reachability.
