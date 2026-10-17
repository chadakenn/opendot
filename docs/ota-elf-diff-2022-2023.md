# ELF-level OTA service comparison (NS6555 vs NS6559)

_2026-10-17 · Read-only static analysis of two Crumpet OTA system filesystems._

## Reproducibility and evidence

The 2022 and 2023 `system` partitions were independently reconstructed from the two OTA payloads. The selected binaries and libraries were extracted from their SquashFS filesystems, and **all 28 extracted file hashes** matched the prior complete filesystem inventories (14 files per release). Their ELF sections and dynamic symbols were then compared using GNU `readelf`, `strings`, and Python.

**No executable was run from the firmware; no device was powered on or flashed.** The 2022 and 2023 packages are both **not** confirmed to match the older firmware displayed for the unplugged target Dot (`8624646532`).

## Results

| ELF object | Whole file | `.text` section | Imported symbol changes |
|---|---|---|---|
| `system/bin/update_engine` | Identical | Identical | None |
| `system/lib/libdoppleroobe.so` | Identical | Identical | None |
| `system/lib/libcivetweb.so` | Identical | Identical | None |
| `system/bin/oobed` | Changed | Changed (20 more bytes) | None |
| `system/bin/ace_otad` | Changed | Changed (184 more bytes) | One removed |
| `system/bin/otad` | Changed | Changed (92 fewer bytes) | None |
| `system/lib/libace_ota.so` | Changed | Changed (448 more bytes) | None |
| `system/lib/libace_ota_downloader.so` | Changed | Changed (68 more bytes) | 8 added / 8 removed |
| `system/lib/libace_ota_dsts.so` | Changed | Changed (864 more bytes) | 16 added / 11 removed |
| `system/lib/libnative_dev_ota.so` | Changed | Changed (628 more bytes) | 2 added |

`oobed`, `ace_otad`, and `otad` have unchanged overall file sizes despite changes to their code and data sections. This fact does **not** establish that functionality is equivalent.

### Finding A: Downloader networking API transition

The 2022 `libace_ota_downloader.so` imports the `lws_sspc_*` family, while the 2023 build instead imports `lws_ss_*` variants:

| 2022 API | 2023 API |
|---|---|
| `lws_sspc_create` | `lws_ss_create` |
| `lws_sspc_client_connect` | `lws_ss_client_connect` |
| `lws_sspc_request_tx` | `lws_ss_request_tx` |
| `lws_sspc_set_metadata` | `lws_ss_set_metadata` |
| `lws_sspc_get_metadata` | `lws_ss_get_metadata` |
| `lws_sspc_start_timeout` | `lws_ss_start_timeout` |
| `lws_sspc_cancel_timeout` | `lws_ss_cancel_timeout` |
| `acm_sspc_init` | `acm_init` |

**Interpretation:** There is a concrete SDK / networking interface migration. Imported-symbol differences don't prove a change to how package signatures are verified or how requests are authorized.

### Finding B: OTA metrics migration

The 2023 `libace_ota_dsts.so` adds a dynamic dependency on `libace_minerva_metrics_api.so` and imports `aceMinerva_*` metrics functions. Older `ace_metric_pmet_*` imports are absent from the new build. `libnative_dev_ota.so` also gains `ota_add_number_metric` and `ota_record_metric` imports.

**Interpretation:** Telemetry/metrics implementation changed. Not evidence of a new code-execution or OTA acceptance path.

### Finding C: Diagnostic string changes in `otad`

A comparison of printable strings shows additions in the 2023 `otad`, including:

- `Signature matches`
- `Signatures don't match`
- `/data/ota_package/target.blocklist`
- A `CareMapDownloader.cpp` source-path reference

**Interpretation:** The newer build has extra signature/care-map-related diagnostics. We cannot conclude the security check was absent in 2022, nor that the messages are reachable on the target device, from strings alone.

### Finding D: Setup interface library unchanged

Both `libdoppleroobe.so` and `libcivetweb.so` are identical in the two archives. The `oobed` executable differs but its imported and linked-library name sets are unchanged.

**Interpretation:** There is no observed expansion in the dynamic imports for the entry executable, but this does not rule out changes to internal logic or dynamically resolved calls.

## Reproduce on Windows / WSL2

First obtain and extract your **own local** copies of both OTA archives following [system comparison instructions](system-service-diff-2022-2023.md). In Ubuntu, install binutils:

```bash
sudo apt-get install binutils
python3 tools/compare_ota_elf.py /path/to/2022-extracted-root /path/to/2023-extracted-root --json-out /tmp/opendot-elf-diff.json
```

For detailed **local-only** printable-string differences, add `--include-strings`. Review that output for proprietary or sensitive material before sharing it.

The comparison script only opens files and invokes `readelf`/`strings`. It does **not** execute binaries extracted from Amazon firmware or interact with an Echo Dot.

## Next focused work

1. Distinguish changes caused by SDK/library migrations from genuine `otad` control-flow differences, with careful function-level mapping and reproducible evidence.
2. Document any changed *legitimate* OTA update status, manifest handling, and care-map behavior.
3. Verify firmware actually present on the physical C78MP8 before drawing conclusions about its older update logic.
4. Keep the original problem explicit: **Wi-Fi-only first installation of custom firmware is not demonstrated**; no SHA-256 spoof can substitute for Amazon's private signing key.

No bypass, signed custom OTA, or reliable initial installation path has been established.
