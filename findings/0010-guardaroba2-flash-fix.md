# Finding 0010: guardaroba_2 fixed by same-version official OTA reflash

**Date**: 2026-11-05, 20:51-21:03, maintainer-approved

The anomalous unit (V1.04.12 app, OTA metadata desynced to 0x01020510) was
reflashed with the ORIGINAL official OSRAM 1.05.10 image from zigbee-OTA,
byte-identical to the artifact analyzed in this repo. Delivery: Z2M per-request
OTA index (payload.url to a local one-entry JSON with force:true), the
sender-side force path verified in the installed code by astra; no header or
signature modification, no global config override, no schedule left armed.

Sequence: check via inline index -> update_available true; update ran to 100%;
device rebooted (announce 21:02:05). Read-only post checks: genBasic now
{"appVersion":16,"swBuildId":"V1.05.10"}; the manuSpecificOsram cluster is
readable (was UNSUP_MANUF_GENERAL_COMMAND); baseline attrs match the fleet
profile; C01 applied and verified (attr7 0->1).

Final power-cycle verification pending maintainer. With it, the whole AC03641
fleet (3/3) plus one AB32840 run the restore-OFF config; Scale (AB32840)
remains pending mesh reachability.
