# OSRAM LIGHTIFY firmware RE

Reverse engineering of the OSRAM LIGHTIFY Zigbee bulb firmware served through
the public [Koenkk/zigbee-OTA](https://github.com/Koenkk/zigbee-OTA) index,
targeting the LIGHTIFY Classic A60 W clear family (AC03641 and siblings).

## Why

OSRAM LIGHTIFY bulbs always turn back ON after a mains power cycle. The
standard Zigbee attribute `genOnOff.startUpOnOff` (0x4003) returns
UNSUPPORTED_ATTRIBUTE, and the manufacturer cluster `manuSpecificOsram`
(0xFC0F) only exposes two known commands, `saveStartupParams` (0x01) and
`resetStartupParams` (0x02), discovered by community sniffing in 2020: they
persist brightness and color, never the on/off state. Questions this project
tries to answer from the firmware itself:

1. Is there an undocumented command in cluster 0xFC0F that covers on/off?
2. Where is the power-on restore logic and what does it actually restore?

## Key findings so far

- The `ZLL_MK_*` OSRAM images in zigbee-OTA are **plaintext ARM Thumb
  firmware**, not encrypted (the `A60_DIM_Z3_*` files are a different product
  line and ARE encrypted; do not confuse them). See
  [findings/0001](findings/0001-plaintext-ota-images.md).
- Cortex-M class SoC, flash-mapped image with app code at 0x100020, and a
  persistent region at 0x11E000-0x120000 that is NOT shipped in the OTA
  payload but holds the ZCL cluster/command tables (and apparently some code).
  See [findings/0002](findings/0002-pipeline-and-memory-layout.md).
- Endpoint registration confirms input clusters 03/04/05/06/08/FC0F; an
  OSRAM-specific application quarter sits around 0x10e020-0x112020 with 85
  indexed functions. See
  [findings/0003](findings/0003-osram-app-quarter.md) and
  [disasm/MAP_quarter.md](disasm/MAP_quarter.md).
- The cluster 0xFC0F command handler is found and decoded: beyond the two
  known commands it implements UNDOCUMENTED commands 0, 9 and 0x0A, and the
  save command writes a 0xAA magic into the persisted power-on mode byte the
  firmware consults at boot. See
  [findings/0004](findings/0004-cluster-fc0f-command-handler.md).

## Reproduce

```bash
python3 tools/extract_payload.py                       # downloads + extracts payload
python3 tools/make_elf.py cla60_w_clear_payload.bin cla60.elf
llvm-objdump --disassemble-all --triple=thumbv7m-none-eabi cla60.elf > full.asm
python3 tools/func_index.py full.asm cla60_w_clear_payload.bin 0x10e020 0x112020
```

## Layout

- `tools/` extraction, ELF wrapping, function indexing
- `disasm/` full Thumb disassembly, function index, annotated quarter map
- `findings/` numbered, dated findings

The original `.ota` files are NOT committed: they are already publicly hosted
in the zigbee-OTA repository linked above. `disasm/` contains the extracted
sub-element payload and its disassembly for research purposes, with
attribution.

## Contributing

If you own a LIGHTIFY gateway with root access, or ever dumped a bulb, the
missing piece is the 0x11E000-0x120000 persistent region of the flash (8 KB
per device): it contains the ZCL cluster/command tables this project cannot
see from the OTA image alone. Issues and PRs welcome.
