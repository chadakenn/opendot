# Primary hardware reference: jvandewiel/no-alexa

_Reviewed 2026-10-17. **This is third-party research, not a measurement of our physical Echo Dot.**_

## Why this source matters

[jvandewiel/no-alexa](https://github.com/jvandewiel/no-alexa) specifically documents reverse engineering the **third-generation Echo Dot**, and its [wiki](https://github.com/jvandewiel/no-alexa/wiki) is substantially more detailed than the short repository README. OpenDot should consult it first for hardware-level Crumpet research, rather than borrow pins or procedure from another Echo variant.

### Core links

- [Hardware inventory](https://github.com/jvandewiel/no-alexa/wiki/Hardware)
- [UART logs and boot modes](https://github.com/jvandewiel/no-alexa/wiki/UART-logs)
- [Fastboot experiments](https://github.com/jvandewiel/no-alexa/wiki/Fastboot)
- [NAND dumping write-up](https://github.com/jvandewiel/no-alexa/wiki/Dumping-NAND-flash)
- [NAND scrambling and ECC](https://github.com/jvandewiel/no-alexa/wiki/Decoding-NAND-flash)
- [Original repo UART log files](https://github.com/jvandewiel/no-alexa/tree/main/logicanalyzer/uart_logs)
- [Original flash reader tools](https://github.com/jvandewiel/no-alexa/tree/main/dump_flash_tool)
- [Original NAND reader/descrambler tooling](https://github.com/jvandewiel/no-alexa/tree/main/descramble)
- [Original PCB/NAND reference pictures](https://github.com/jvandewiel/no-alexa/tree/main/pictures)

## Hardware observed by that researcher

| Assembly or component | Reported reference |
|---|---|
| Main logic board (MLB) | **30-004397 REV 01** |
| Microphone/LED board | **30-004398 REV 01** |
| CPU marking | **MTK8516BAAA** (MediaTek MT8516) |
| Separate SDRAM | **MT41K128M16JT-107** (2 Gb DDR3) |
| Raw NAND | **MX30LF4G28AD** (4 Gb = approx. 512 MiB, not 4 GB) |
| Speaker amplifier | **TI TAS2770** |
| Microphones | **4 MEMS microphones**, labeled MK1–MK4 |
| Audio ADCs | **2 × TLV320ADC3101** |
| LED driver | **IS31FL3236**, serving 12 RGB LEDs |
| Wi-Fi/Bluetooth | **MT7658CSN** |
| Buttons | **4**, S1–S4 |

Several hardware revisions and alternative NAND chips have been reported. **Do not assume this exact component list or pad mapping applies to the user's unopened C78MP8.** Note the distinction between the SoC chip marking **MT8516** and the **MT8167** software platform labels in Crumpet OTA files.

## UART: observed, read-only path

The wiki documents serial boot output from the main PCB's test pads:

- **115200 baud** at the preloader stage.
- **921600 baud** during later boot.
- Logs include bootloader build details, NAND detection, partition layout, active A/B slot, and security state. Actual log detail varies by software release.
- Researcher reports a fastboot entry via the **S4 (“uber”) button**, or by taking **TP54 to ground** on the tested board, with USB connected. A green ring was reported in this condition.
- The author's [comment on Issue #1](https://github.com/jvandewiel/no-alexa/issues/1#issuecomment-1579313148) says only two UART wires are needed for a basic observation and points to TP54 near the main board's connector.

**Caution:** These are research observations, **not verified connection instructions for our board**. TP54 location/identity, TX/GND and logic voltage must be checked against actual high-resolution board photos and a meter. Do **not** attach adapter VCC, assume 3.3 V logic, or deliberately short pads based solely on text descriptions.

## Fastboot: available != unlocked

The project's [fastboot report](https://github.com/jvandewiel/no-alexa/wiki/Fastboot) and [captured fastboot log](https://github.com/jvandewiel/no-alexa/blob/main/logicanalyzer/uart_logs/fastboot_stuff.txt) demonstrate:

- A USB-visible fastboot device reporting `product: CRUMPET`.
- `secure: yes`, `prod: 1`, **`unlock_status: false`**.
- Read-only `fastboot getvar all` reports build/security metadata.
- Privileged `fastboot oem` operations were **rejected** on locked hardware.

**Important:** Fastboot presence does not prove a safe flash dump, an unlocked bootloader, or a viable unsigned custom firmware installation. Also do not publish complete logs without redacting serial/OTU identifiers.

## NAND: destructive research, not our first step

See [Macronix NAND WP#/PT control vs verified boot](nand-protection-vs-secure-boot.md). The `MX30LF4G28AD` write-protection feature affects chip programming but **does not** unlock Amazon's verified boot or OTA signatures.


- The researcher **desoldered the NAND** and wired it into Raspberry Pi GPIO or FT2232H test adapters; this was **not** a demonstrated non-invasive in-circuit dump.
- The [flash reader README](https://github.com/jvandewiel/no-alexa/blob/main/dump_flash_tool/README.md) reads pages repeatedly, compares results and saves matching reads.
- NAND images involve scrambling and ECC corrections; the [decoding wiki](https://github.com/jvandewiel/no-alexa/wiki/Decoding-NAND-flash) documents PRBS scrambling and BCH parameters for the tested chip. Raw `*.bin` files cannot simply be treated as a mounted filesystem.
- Do not use the source's read/write experiment scripts on our device without independent electrical verification and a recoverable backup plan.

## No documented initial OTA bypass

The repository is primarily hardware reverse engineering and NAND analysis. Its documented fastboot operations are locked and its flash access involved physical chip removal. **It does not provide a demonstrated OTA-over-Wi-Fi installation of custom firmware for a stock Crumpet**.

External C78MP8 custom-voice projects likewise remain separate research efforts. Our future signed OTA solution would be a *post-installation* feature, not a substitute for initial access.

## Proposed next milestone for OpenDot

1. Preserve the existing firmware and Alexa-app cached version; no OTA or factory reset.
2. Compare clear photos of *our specific physical board* with no-alexa's MLB and MIC revisions.
3. Confirm appropriate ground and serial-voltage levels before any electrical connection.
4. If safe, capture only read-only UART logs to determine the board's original preloader, LK build and storage/boot state.
5. Consider read-only USB `fastboot getvar` only after the USB connection is positively identified; never issue `flash`, `erase`, `relock`, or boot-state modifications.
6. Return to firmware-port/OTA research with the **actual installed firmware version** confirmed.

**Attribution:** hardware photographs, wiki descriptions, logs, scripts, and NAND decoding are the research of the no-alexa author/contributors. OpenDot links to them and does not copy their binaries, photographs, or proprietary device dumps.
