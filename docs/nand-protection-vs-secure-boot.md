# MX30LF4G28AD NAND write protection vs Amazon secure boot

_2026-10-17 · Datasheet review only. **No physical C78MP8 NAND has been identified or programmed.**_

## Sources

- [Macronix MX30LF1G28AD / MX30LF2G28AD / MX30LF4G28AD datasheet, Rev. 1.3 (PM2579)](https://www.macronix.com/Lists/Datasheet/Attachments/8864/MX30LF4G28AD%2C%203V%2C%204Gb%2C%20v1.3.pdf)
  - See §6-15-5, *Block Protection*; Set/Get Feature definitions for `A0h`; Block Protection Status Read `7Ah`; Status Read `70h`.
- [no-alexa `flashdevice.py`](https://github.com/jvandewiel/no-alexa/blob/main/dump_flash_tool/flashdevice.py): NAND **reading** implementation, feature/status inspection, ONFI device detection.
- [no-alexa flash dumping README](https://github.com/jvandewiel/no-alexa/blob/main/dump_flash_tool/README.md): repeated page reads with comparison.
- [OpenDot hardware reference](no-alexa-hardware-reference.md): the Macronix part was observed in another researcher's sample, not identified on our user's exact board.

## Verified NAND behavior

**Write protection on the NAND chip and authorization to boot unsigned code on the Echo are completely different things.**

| Protection or control | Datasheet behavior / consequence |
|---|---|
| `WP#` | Active-low hardware write-protection input. Low disallows normal program/erase; high enables them *if no other protection prevents the operation*. |
| `PT` sampled on power-on | High selects NAND block-protection mode: block-protection bits initially protect **all blocks**. Low selects simple WP# protection mode. |
| ONFI feature address `A0h` | Stores volatile block protection fields: BP2, BP1, BP0, Invert, Complementary, Solid Protection (SP). Default `P1=38h` in PT-high mode. |
| `Get Feature` (`EEh`) | Allows querying supported feature configuration without changing it. |
| `Set Feature` (`EFh`) | May **change the NAND protection state** if PT mode and WP# conditions permit; changing protection is not necessary for reading a dump. |
| `Status Read` (`70h`) | Status bit 7 indicates `WP#` state; it does **not** by itself prove that PT block protection is disabled. |
| `Block Protection Status Read` (`7Ah`) | Reports individual block-protection status in PT-enabled mode. |
| `SP` bit | When set, latches the chosen block-protection state until next power cycle. |

The earlier analysis correctly identified the relationship between the WP# input, PT power-on selection, and the block-protection feature. **Do not infer from it that the actual Dot has PT high, that the NAND is the same part/package, or that an in-circuit programmer can safely override the SoC's bus.**

### Critical distinction: what a NAND 'unlock' cannot do

```text
MX30LF4G28AD WP#/PT ──► enables physical NAND program/erase
                                  │
                                  ▼
                          modified NAND contents
                                  │
                                  ▼
             Amazon preloader / LK / verified boot policy
                                  │
                            still verifies trust
                                  ▼
                   custom firmware may NOT boot
```

The stock OTA package's signed payload validation is independent of NAND write protection. Making the chip writable **does not** make an unsigned OTA valid, issue an Amazon one-time-unlock certificate, or switch the retail bootloader to an unlocked state.

## OpenDot priority

1. **Do not attempt physical writes or lift WP#/PT pins.** We have not established whether the board even uses this exact Macronix part.
2. First identify the **actual package markings** on the C78MP8 PCB.
3. Prefer non-destructive UART/USB diagnostic information and investigate full **read-only** backup methods.
4. If raw NAND reads become necessary, document page+OOB data, ECC, scrambling, bad-block tables, repeated-read verification and independent hashes **before any erase operation**.
5. Only then evaluate whether authorized/recoverable physical programming has any practical value for an install path, taking verified-boot behavior into account.

**Status: informational recovery research, not an unlock method.** No write-protect pins were manipulated; no NAND or boot partition has been changed.
