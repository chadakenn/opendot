# OpenDot research status

_Updated 2026-10-17. This project has **not** flashed or modified a retail device._

## Research goal

Convert a stock Echo Dot 3rd Gen **C78MP8 / Crumpet** to a fully local Home Assistant Assist satellite. Prefer an initial Wi-Fi-only install; consider one-time physical access only if needed, then enable independent OTA updates.

## Device known state

- Reported device: retail Echo Dot C78MP8, unpowered for approximately three years.
- Alexa app displays software version **8624646532**, but this may be historical/cached. **The installed firmware has not been independently checked on-device.**
- Former Wi-Fi network name and password are unknown. No isolated first-boot networking experiments have yet occurred.
- No factory reset, UART wiring, USB/fastboot session, NAND read, or flash write has been performed on the actual Echo Dot.

## Offline package work

Two official-looking Crumpet OTA files were provided for research:

- **NS6555/4307** from November 2022, build **8087720836**
- **NS6559/4660** from June 2023, build **9094444164**

Both full-file SHA-256 hashes were independently recomputed on the uploaded files. The A/B metadata and partition manifests were examined. Boot/LK partitions were reconstructed and hash checked; see [firmware comparison](firmware-comparison.md).

### Confirmed observations from package comparison

- Both packages claim `pre-device=crumpet` and contain nine A/B update partitions.
- Package-level SHA-256 checksums are not equivalent to Amazon code-signing signatures.
- Boot, system, LK and partition table contents differ between package generations.
- TEE partition hashes are equal across packages.
- Both inspected boot ramdisks retain retail-oriented properties such as `ro.secure=1` and `ro.adb.secure=1`.
- Both releases reference LK one-time-unlock logic; no usable retail unlock certificate has been obtained.
- No preloader image is shipped in these two OTA payloads, limiting what they can tell us about an existing unit's first boot stage.

### Findings reported by a separate firmware analyzer, NOT independently reproduced here

The June 2023 system reportedly contains an A/B `update_engine`, `otad`, `ace_otad`, and SoftAP setup service `oobed` with Thrift RPC at `/OOBE`. Reported static tracing suggests `oobed` can request update status but does not expose a firmware upload method. Details and caveats: [OTA architecture](ota-architecture.md).

## Current blockers

1. Installed device version and boot/security state have not been measured.
2. There is **no confirmed Wi-Fi-only entry point** for initial code installation.
3. The stock OTA path validates cryptographic signatures and cannot be repurposed simply by editing hashes.
4. No custom image, local voice service or audio/LED driver port has been built or tested.
5. No validated backup, recovery, or rollback method exists for this exact unit.

## Research discipline

Label every future result **confirmed by test**, **static artifact evidence**, or **hypothesis/reported**. Keep device identity and credentials out of public documentation. Do not risk a flash write until a reproducible restore procedure is available.
