# Crumpet OTA and provisioning architecture

**Evidence labels:** The OTA package format and boot/manifest properties are documented in [firmware-comparison.md](firmware-comparison.md). The detailed service descriptions below are from **earlier externally produced static-analysis notes of the June 2023 image** and **have not been independently reproduced or tested against the physical C78MP8**. Treat them as research leads, not established attack surfaces.

## Reported system components

```text
                     Echo Dot C78MP8 (reported design)
Alexa app  ──SoftAP──► oobed (HTTP/Thrift setup RPC)
                           │  AIPC status requests
                           ▼
                       ace_otad
                           │  cloud inventory + downloader
                           ▼
                     Amazon OTA service
                           │ signed payload URL/metadata
                           ▼
                  otad / update_engine
                           │ signature + integrity verification
                           ▼
                    inactive A/B partitions
                           │
                           ▼
                    LK / verified boot
```

This is **conceptual**, not a confirmed live traffic capture.

## Reported setup service (`oobed`)

Previous notes report:

- An HTTP server on port `8080` with `/OOBE` (Thrift RPC) and `/proxy.js` routes while in SoftAP provisioning mode.
- RPC methods for scanning networks, connecting/disconnecting/forgetting networks, device details, CSR/registration, setup completion and `getOTADetails`.
- `getOTADetails` requests **status**, not uploading or applying arbitrary firmware; the earlier enumeration did not find a firmware-upload RPC.
- An Amazon-domain browser CORS allowlist. **CORS is not device authentication** and its presence does not establish the security of native RPC clients.
- A PKCS#7-based provisioning credential exchange, as reported by the earlier analyzer; authorization and certificate lifetimes were not validated on actual hardware.

These claims should be checked using reproducible local evidence before stating that a specific build behaves this way.

## Reported OTA services

Previous analyzer notes described:

- `ace_otad` / related libraries initiate an outbound software inventory request to Amazon and receive a download URL, version and payload metadata.
- `otad` communicates with Android's A/B `update_engine` through **local Binder IPC**, rather than an exposed firmware-upload network listener.
- `update_engine` verifies signed payload metadata before applying the update to an inactive slot.
- Recovery/rollback and boot verification add protections beyond a ZIP filename or user-editable SHA-256 field.

**Implication:** A spoofed checksum or redirected URL is **not** enough to install a custom image. A complete, authorized initial installation path is still missing.

## Reported LK bootloader behavior

Earlier notes identified strings/functions relating to Amazon's one-time-unlock certificate flow and retail restrictions. Independently, both extracted LK images contain unlock-related printable strings and the two boot ramdisks retain retail security properties. **No authorized certificate, usable retail unlock, or reliable unsigned boot has been demonstrated.**

## Outstanding validation

1. Compare relevant executables and service configuration between NS6555 and NS6559.
2. Verify startup conditions, RPC inventory and authorization behavior against an isolated stock device without allowing cloud update.
3. Confirm installed firmware build and board revision; do not assume the June 2023 OTA matches the unplugged unit.
4. Keep the initial-install problem separate from designing future private OTA updates **after** custom code is executing.

This document contains **no recovered device secrets, signed firmware, or exploit implementation**.
