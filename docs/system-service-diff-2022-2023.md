# Full system-file comparison: NS6555 (2022) vs NS6559 (2023)

**Date:** 2026-10-17  
**Source:** Two user-supplied Crumpet OTA archives; offline and read-only analysis.  
**Status:** Independently reproduced with manifest-verified reconstruction of both `system` partitions, SquashFS filesystem traversal, and SHA-256 of every regular file.

## Summary

| Observation | November 2022: NS6555/4307 | June 2023: NS6559/4660 |
|---|---:|---:|
| Partition image size | 136,626,176 B | 136,626,176 B |
| Actual SquashFS bytes used | 120,865,548 B | 95,734,874 B |
| SquashFS compression | LZ4 | Zstandard |
| SquashFS inodes | 2,804 | 2,845 |
| Regular files | 2,391 | 2,430 |
| Full-replacement payload operations (`system`) | 66 | 66 |
| Reconstructed system SHA-256 | `53bec617d2b9b2d3b2ca5ae10eeb30e09ad57390530519fa156f24fafd8cc020` | `f8335b744c31f04c77daa24fc0978041c952a0fe9536e749ed94b6019a1caa3f` |

Comparing files at the **same relative path**:

- **1,801** identical regular files by SHA-256.
- **582** present in both releases, but different SHA-256.
- **47** files added in 2023.
- **8** files removed from 2022.

**Important:** A change in executable hash does not establish an exploit, a security patch, or a changed signature policy. Different build paths, compiler options, constants, and dependencies also alter hashes.

## OTA/provisioning components of particular interest

| Path (under extracted system root) | 2022 vs 2023 |
|---|---|
| `system/bin/update_engine` | **Identical SHA-256** |
| `system/lib/libdoppleroobe.so` | **Identical SHA-256** |
| `system/lib/libcivetweb.so` | **Identical SHA-256** |
| `system/etc/security/otacerts.zip` | **Identical SHA-256** |
| `system/etc/update_engine/update-payload-key.pub.pem` | **Identical SHA-256** |
| `system/etc/init/on_demand_update_engine.rc` | **Identical SHA-256** |
| `system/etc/init/init.ace.otad.rc` | **Identical SHA-256** |
| `system/bin/oobed` | Changed |
| `system/bin/ace_otad` | Changed |
| `system/bin/otad` | Changed |
| `system/lib/libace_ota.so` | Changed |
| `system/lib/libace_ota_downloader.so` | Changed |
| `system/lib/libace_ota_dsts.so` | Changed |
| `system/lib/libnative_dev_ota.so` | Changed |

Selected independent hashes:

| File | 2022 SHA-256 | 2023 SHA-256 |
|---|---|---|
| `update_engine` | `03dd12c11643da8500d46e07083d72f93c3695cfb728daa7c2b0a8e569738412` | same |
| `libdoppleroobe.so` | `7bb75f692c0e8e3b45a50809050bf062a9401c78dd63be758297da804131ee4d` | same |
| `libcivetweb.so` | `48cfe2ad0803ac98921014898d996d02e8d522969650fbc54a22d488629b9d0b` | same |
| `update-payload-key.pub.pem` | `a8daa18a171775e19f0595ec6393d4e3dd9b7e6eb57151240e3accb92a1716c0` | same |
| `otacerts.zip` | `741dcd1bf1a2135d43539f64ce2667448879ac4f91a97cdd53bb64c4a0d6a8d7` | same |
| `oobed` | `1187080a5d6de8c07dd95f891e8b809bb524512373dcde0086b50916096b33e4` | `52758de944deaa30be0d2c56b07ecb26b260b4a3c4bb93873db67928a81deb4c` |

### Additional static observations

- `oobed` is **526,044 bytes** in both images but its content differs. Its companion `libdoppleroobe.so` is unchanged.
- `ace_otad` is **26,184 bytes** in both images but differs; the downloader and DSTS libraries also changed.
- The newer `otad` contains additional printable diagnostics referring to **signature matches/mismatches**. Presence of a log message is **not evidence** that the comparison was absent from the older code.
- The newer system adds components around `minerva_service`, `luma_svc`, `FFRegd` and related libraries. These additions may be unrelated to OTA handling.
- Both release images have identical trusted payload public-key bytes and `otacerts.zip`. This weighs against the hypothesis that simple re-signing with an arbitrary key would work on either release.

## What this means for OpenDot

The stock A/B update engine and its trusted key material did not change between these two packages. Our next useful offline comparison should concentrate on **behavioral and configuration differences in Amazon's update orchestration services**, especially `otad`, `ace_otad` and their downloader libraries. There is still **no confirmed Wi-Fi-only custom-code installation path**.

The Alexa app's previously displayed build `8624646532` is not one of the images in this comparison. The actual device remains unplugged, and its installed software is not confirmed.

## How to reproduce on Windows with WSL2 Ubuntu

Install tools **inside WSL Ubuntu**:

```bash
sudo apt-get update
sudo apt-get install -y python3 squashfs-tools
```

From a clone of this repository, substitute your own locally downloaded OTA filenames:

```bash
python3 tools/extract_partition.py /path/to/2022-crumpet-ota.bin system /tmp/opendot-2022-system.img
python3 tools/extract_partition.py /path/to/2023-crumpet-ota.bin system /tmp/opendot-2023-system.img

unsquashfs -d /tmp/opendot-2022-root /tmp/opendot-2022-system.img
unsquashfs -d /tmp/opendot-2023-root /tmp/opendot-2023-system.img

python3 tools/compare_extracted_systems.py /tmp/opendot-2022-root /tmp/opendot-2023-root
```

The partition extractor checks the reconstructed image SHA-256 against the payload manifest; this verifies bytes **relative to the provided archive**, not the vendor's release signature. Keep the downloaded Amazon firmware files and extracted images **out of Git**.

## Remaining open questions

1. Which software version is really installed on the offline C78MP8?
2. Are the observed changes in Amazon binaries functional differences or rebuild noise?
3. Does any **authorized** installation/diagnostic path exist on the installed retail firmware?
4. Is a recoverable hardware-assisted first-install method available, if Wi-Fi-only installation is not?

None of these questions is answered by these hashes alone.
