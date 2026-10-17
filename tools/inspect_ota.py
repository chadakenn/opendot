#!/usr/bin/env python3
"""Read-only inspection of Android A/B OTA package metadata (Python 3 standard library)."""

import argparse
import hashlib
import struct
import zipfile


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as infile:
        for chunk in iter(lambda: infile.read(4 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ota", help="local path to an Amazon Crumpet OTA .bin archive")
    args = parser.parse_args()

    print("Archive SHA-256:", sha256_file(args.ota))

    with zipfile.ZipFile(args.ota, "r") as ota:
        for name in (
            "META-INF/com/android/metadata",
            "ota.prop",
            "payload_properties.txt",
        ):
            try:
                contents = ota.read(name).decode("utf-8", errors="replace")
            except KeyError:
                print("\n###", name, "(not present)")
                continue
            print("\n###", name, "\n" + contents, sep="")

        with ota.open("payload.bin") as payload:
            header = payload.read(24)
            if len(header) != 24:
                raise ValueError("payload.bin header is truncated")
            magic, version, manifest_bytes, signature_bytes = struct.unpack(
                ">4sQQI", header
            )
            if magic != b"CrAU":
                raise ValueError("payload.bin does not have an A/B OTA header")
            print(
                "\nPayload header:",
                f"magic={magic!r}",
                f"version={version}",
                f"manifest_bytes={manifest_bytes}",
                f"metadata_signature_bytes={signature_bytes}",
            )

    print("\nRead-only inspection complete; no images extracted or flashed.")


if __name__ == "__main__":
    main()
