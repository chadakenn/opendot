# Crumpet OTA comparison: November 2022 vs June 2023

_Research date: 2026-10-17. Read-only analysis of two user-supplied Amazon OTA archives; **not** an on-device experiment._

## OTA packages

| Property | November 2022 | June 2023 |
|---|---|---|
| Filename | `update-kindle-crumpet-NS6555_user_4307_0008087720836.bin` | `update-kindle-crumpet-NS6559_user_4660_0009094444164.bin` |
| Fire OS | 6.5.5.5 | 6.5.5.9 |
| Build / release | 8087720836, NS6555/4307 | 9094444164, NS6559/4660 |
| Device in OTA metadata | `crumpet` | `crumpet` |
| Whole-archive SHA-256 | `e1d5138f1fa283c336139c7601099a6b87a3d1ff79220fa78ccb5568daf2e83e` | `1a84d094b8b5fe51514e1c1ed773645204720a47c460a17f391100ad8e8d6e6d` |
| `payload.bin` size | 104,452,212 bytes | 110,635,208 bytes |
| Android release | 7.1.2 | 7.1.2 |
| Security patch property | 2022-01-01 | 2022-01-01 |
| OTA format | Full A/B update, payload format v2 | Full A/B update, payload format v2 |

Both complete-file hashes above were **recalculated from the uploaded OTA archives on 2026-10-17**. Hashes can verify that two downloaded files match; they cannot authorize a modified OTA package.

## Partition manifest comparison

| Partition | 2022 uncompressed bytes | 2023 uncompressed bytes | Same image SHA-256? |
|---|---:|---:|---|
| `system` | 136,626,176 | 136,626,176 | No |
| `boot` | 9,990,144 | 9,879,552 | No |
| `lk` | 237,568 | 237,568 | No |
| `tee1` | 2,367,488 | 2,367,488 | Yes |
| `tee2` | 2,367,488 | 2,367,488 | Yes |
| `brhgptpl_0` | 184,320 | 184,320 | No |
| `brhgptpl_1` | 184,320 | 184,320 | No |
| `brhgptpl_2` | 184,320 | 184,320 | No |
| `brhgptpl_3` | 184,320 | 184,320 | No |

These comparisons use the image hashes included in the OTA payload manifests. The `boot` and `lk` images were also reconstructed and recomputed against those hashes for both releases. The 2023 images were previously reconstructed more broadly, but the 2022 system/TEE images were not all reconstructed in this pass.

## Further static observations

- Neither OTA payload contains a **preloader** image.
- The `lk` files differ despite both being 237,568 bytes; a prior byte comparison counted **83,248 different byte positions**. This does **not** by itself identify any security behavior change.
- Printable strings in both `lk` files reference Amazon one-time-unlock checks and `androidboot.verifiedbootstate` values (`green`, `orange`, `yellow`, `red`). **Strings are not proof of an accessible unlock path.**
- Both extracted boot ramdisks contain `ro.secure=1`, `ro.debuggable=0`, `ro.adb.secure=1`, and `ro.oem_unlock_supported=1`.
- Both ramdisks' `fstab.mt8167` specify a SquashFS system mount with `wait,verify,slotselect`.
- The kernel command lines reference the same `veritykeyid`; this does not establish identical bootloaders.
- Both extracted boot ramdisks contained 132 regular files; 120 matched by SHA-256 and 12 differed, including `init`, `adbd`, `recovery` and SELinux policy-related files.
- `META-INF/com/android/otacert` bytes were identical in the two archives. This byte comparison is **not** a full cryptographic signature-validation procedure.
- `system/build.prop` reports product `crumpet`, model `AEOCP`, and `ro.build.characteristics=headless`.
- Presence of `ro.boot.selinux=disable` in properties does not independently establish the running SELinux state.

## What this comparison does *not* tell us

- The installed firmware of the actual, currently unplugged Dot. Alexa app software `8624646532` may be cached.
- Whether a stock retail Crumpet will accept an unsigned image (nothing examined here demonstrates it).
- Which preloader version exists on the target board.
- Whether the 2022 and 2023 `oobed` and `ace_otad` compiled binaries have materially different behavior (not compared at the code level in this report).
- Whether the zip's complete vendor-signature validation passed: **hash comparisons alone are not signature validation**.

## Reproduce the whole-archive hashes

Windows PowerShell:

```powershell
Get-FileHash "C:\path\to\update-kindle-crumpet-NS6555_user_4307_0008087720836.bin" -Algorithm SHA256
Get-FileHash "C:\path\to\update-kindle-crumpet-NS6559_user_4660_0009094444164.bin" -Algorithm SHA256
```

Or use `python tools/inspect_ota.py <file>` from this repository.

**No Amazon OTA archive or extracted partition image is distributed by OpenDot.**
