#!/usr/bin/env python3
"""Extract a partition from a FULL CrAU v2 A/B OTA payload.

Supports only REPLACE, REPLACE_BZ, and REPLACE_XZ operations.
Checks per-operation blob hashes (when supplied) and the final partition hash.
This does NOT validate Amazon's cryptographic package signatures.
Reads its input; writes only the requested local output image. Never flashes hardware.
"""
import argparse
import bz2
import hashlib
import lzma
import struct
import zipfile
from pathlib import Path


def varint(data, pos):
    value = 0
    for shift in range(0, 70, 7):
        if pos >= len(data):
            raise ValueError("Truncated protobuf varint")
        char = data[pos]
        pos += 1
        value |= (char & 127) << shift
        if char < 128:
            return value, pos
    raise ValueError("Oversized protobuf varint")


def fields(data):
    pos = 0
    while pos < len(data):
        tag, pos = varint(data, pos)
        field, kind = tag >> 3, tag & 7
        if kind == 0:
            value, pos = varint(data, pos)
        elif kind == 2:
            length, pos = varint(data, pos)
            if length > len(data) - pos:
                raise ValueError("Invalid protobuf length")
            value = data[pos:pos + length]
            pos += length
        elif kind in (1, 5):
            length = 8 if kind == 1 else 4
            value = data[pos:pos + length]
            pos += length
        else:
            raise ValueError("Unsupported protobuf field")
        yield field, value


def one(data, field_number):
    return next((value for number, value in fields(data) if number == field_number), None)


def extract(ota_path, partition_name, output_path):
    with zipfile.ZipFile(ota_path) as archive:
        with archive.open("payload.bin") as payload:
            header = payload.read(24)
            if len(header) != 24:
                raise ValueError("Truncated payload header")
            magic, version, manifest_length, signature_length = struct.unpack(">4sQQI", header)
            if magic != b"CrAU" or version != 2 or manifest_length > 20_000_000:
                raise ValueError("Expected CrAU v2 payload")
            manifest = payload.read(manifest_length)

        block_size = one(manifest, 3)
        partitions = {
            one(part, 1).decode("ascii"): part
            for number, part in fields(manifest)
            if number == 13
        }
        if partition_name not in partitions:
            raise ValueError("Partition unavailable: " + partition_name)

        part = partitions[partition_name]
        new_info = one(part, 7)
        expected_size, expected_hash = one(new_info, 1), one(new_info, 2)
        if expected_size is None or expected_hash is None or expected_size > 2**32:
            raise ValueError("Invalid partition image metadata")
        data_start = 24 + manifest_length + signature_length
        operations = [value for number, value in fields(part) if number == 8]

        with archive.open("payload.bin") as payload, open(output_path, "wb+") as output:
            output.truncate(expected_size)
            for operation in operations:
                op_type, offset, length = (one(operation, n) for n in (1, 2, 3))
                if op_type not in (0, 1, 8) or offset is None or length is None:
                    raise ValueError("Unsupported operation: not a full replacement")
                payload.seek(data_start + offset)
                compressed = payload.read(length)
                if len(compressed) != length:
                    raise ValueError("Truncated operation")
                blob_hash = one(operation, 8)
                if blob_hash is not None and hashlib.sha256(compressed).digest() != blob_hash:
                    raise ValueError("Operation SHA-256 mismatch")
                if op_type == 0:
                    decoded = compressed
                elif op_type == 1:
                    decoded = bz2.decompress(compressed)
                else:
                    decoded = lzma.decompress(compressed)
                extents = [value for number, value in fields(operation) if number == 6]
                cursor = 0
                for extent in extents:
                    start = one(extent, 1) * block_size
                    size = one(extent, 2) * block_size
                    chunk = decoded[cursor:cursor + size]
                    if start + len(chunk) > expected_size:
                        raise ValueError("Operation exceeds partition")
                    output.seek(start)
                    output.write(chunk)
                    cursor += size
                if cursor != len(decoded):
                    raise ValueError("Operation length/extent mismatch")

    digest = hashlib.sha256()
    with open(output_path, "rb") as result:
        for block in iter(lambda: result.read(4 * 1024 * 1024), b""):
            digest.update(block)
    if digest.digest() != expected_hash:
        raise ValueError("Reconstructed image SHA-256 mismatch")
    print(f"{partition_name}: {expected_size} bytes, SHA-256 {digest.hexdigest()}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ota", type=Path)
    parser.add_argument("partition", help="Partition name, e.g. system, boot, lk")
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    extract(args.ota, args.partition, args.output)


if __name__ == "__main__":
    main()
