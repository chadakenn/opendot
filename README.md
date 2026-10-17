# OpenDot 🔧

**Research into repurposing the Amazon Echo Dot 3rd generation C78MP8 (Crumpet) as a local Home Assistant Assist voice satellite.**

> **Status: research only.** No working Crumpet custom firmware, OTA installer, or stock-firmware unlock is provided here. No modification has been made to the target device.

## Goal

1. **Preferred:** install custom software for Home Assistant **over Wi-Fi**, starting from stock firmware.
2. **Fallback:** one-time hardware-assisted installation, only if an appropriate, recoverable method is established.
3. **After initial installation:** run local wake word, audio input/output and Home Assistant Assist, with independent signed OTA updates.

The intended end result is an Alexa-free voice satellite using the existing microphone array, speaker, buttons and LED ring where technically possible. Device drivers and audio support are **not yet implemented**.

## Target device

| Item | Known state |
|---|---|
| Model | Echo Dot 3rd Gen **C78MP8** |
| Hardware codename | **Crumpet** |
| Firmware family | Fire OS / Android 7.1.2-based, MediaTek MT8167 |
| Installed firmware | **Unverified**; Alexa app previously showed `8624646532` (may be cached) |
| Device condition | Unpowered for roughly three years; no flash writes or factory reset performed |
| Wi-Fi credentials | Old SSID not known; no live network testing performed |

## Research completed

- Collected **November 2022** (`8087720836`, Fire OS 6.5.5.5) and **June 2023** (`9094444164`, Fire OS 6.5.5.9) Crumpet OTA packages.
- Verified SHA-256 hashes of the two complete OTA archives.
- Inspected full A/B OTA metadata, payload manifests, nine partition entries and boot properties.
- Reconstructed and compared boot and LK images from both releases; compared manifest hashes, OTA certificates, ramdisk files and selected verification-related properties.
- Reconstructed and validated **both system images** and compared the contents of all regular files: 1,801 identical, 582 changed, 47 added, 8 removed. The stock `update_engine`, `libdoppleroobe.so`, `libcivetweb.so`, and OTA trust-key files were byte-identical across these two releases.
- ELF-level comparisons verified a transition from `lws_sspc_*` to `lws_ss_*` networking imports, a Minerva metrics migration, and additional `otad` diagnostics. **None proves a signature bypass.**
- Found that **LK differs**, while `tee1` and `tee2` manifest hashes are **identical** across these releases.
- Earlier third-party/assistant-assisted static analysis reported `oobed`, `ace_otad`, `otad`, A/B `update_engine` and Amazon one-time-unlock logic. These more detailed function-level conclusions **have not been independently reproduced in this repository**.

**No successful unsigned OTA installation or verified Wi-Fi software execution method has been demonstrated.** An editable SHA-256 field does not substitute for a trusted cryptographic signature.

## Documentation

- [**Primary C78MP8 hardware reference: no-alexa wiki, UART, fastboot, NAND**](docs/no-alexa-hardware-reference.md)
- [Research status, confirmed facts and open questions](docs/research-status.md)
- [November 2022 vs June 2023 firmware comparison](docs/firmware-comparison.md)
- [Full SquashFS system service diff (actual file hashes)](docs/system-service-diff-2022-2023.md)
- [Detailed ELF OTA service changes](docs/ota-elf-diff-2022-2023.md)
- [Audio hardware inventory for Home Assistant](docs/audio-hardware-inventory.md)
- [Safe isolated first-boot plan](docs/isolated-first-boot.md)
- [Macronix NAND write protection vs. Amazon secure boot](docs/nand-protection-vs-secure-boot.md)
- [**Amonet/kamakiri Crumpet hardware access research**](docs/amonet-kamakiri-crumpet.md)
- [OTA and provisioning architecture: reported findings vs confirmed checks](docs/ota-architecture.md)
- [Next milestones](docs/roadmap.md)

## Read-only inspection on Windows

The metadata tool uses Python 3 and its standard library; it reads a **locally obtained** Amazon OTA package and prints the whole-file SHA-256, OTA metadata, and `payload.bin` header:

```powershell
python tools/inspect_ota.py "C:\path\to\update-kindle-crumpet-NS6555_user_4307_0008087720836.bin"
```

For repeatable system comparisons, use `tools/extract_partition.py`, `tools/compare_extracted_systems.py`, and `tools/compare_ota_elf.py` with WSL2 and `squashfs-tools`; see the [comparison report](docs/system-service-diff-2022-2023.md).

These scripts do not connect to, change, unlock, or flash a device. **Do not commit OTA binaries** or extracted Amazon images into this repo.

## Safety and scope

- Research targets a personally owned device; avoid flashing until a full recovery path exists.
- Keep the target device offline until its installed build can be recorded without an unintended update.
- Treat any findings from another analyzer as hypotheses until reproduced and logged with evidence.
- **Do not upload** vendor firmware, device serial numbers (DSNs), private keys, registration tokens, Wi-Fi credentials, or personal network captures.
- This public repository contains original notes and a metadata reader only. Amazon binaries remain with their respective owners.

### Related community work

- [**No-Alexa: hardware and firmware research**](https://github.com/jvandewiel/no-alexa) · [wiki](https://github.com/jvandewiel/no-alexa/wiki) (primary hardware reference)
- [Echo Dot Assist research](https://github.com/Gamer92000/echo-dot-assist)

_Research notes last updated 2026-10-17._
