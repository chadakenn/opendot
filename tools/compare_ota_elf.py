#!/usr/bin/env python3
"""Compare OTA-related ELF objects from two extracted Crumpet system roots.

Requires GNU binutils (readelf and strings). Read-only: binaries never run.
Use with locally obtained/extracted vendor firmware; does not dump firmware.
"""
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

TARGETS = (
    "system/bin/oobed", "system/bin/ace_otad", "system/bin/otad",
    "system/bin/update_engine", "system/lib/libdoppleroobe.so",
    "system/lib/libcivetweb.so", "system/lib/libace_ota.so",
    "system/lib/libace_ota_downloader.so", "system/lib/libace_ota_dsts.so",
    "system/lib/libnative_dev_ota.so",
)
KEYWORDS = re.compile(
    r"ota|update|sign|cert|verify|auth|manifest|signature|rollback|recovery|payload|oobe",
    re.I,
)


def command(*args):
    return subprocess.run(args, capture_output=True, text=True, check=True).stdout


def sections(path):
    found = {}
    for line in command("readelf", "-SW", str(path)).splitlines():
        match = re.match(
            r"^\s*\[\s*\d+\]\s+(\S+)\s+\S+\s+[0-9a-fA-F]+\s+"
            r"([0-9a-fA-F]+)\s+([0-9a-fA-F]+)\s+", line
        )
        if match:
            name, offset, size = match.groups()
            found[name] = (int(offset, 16), int(size, 16))
    return found


def symbols(path):
    imports, exports = set(), set()
    for line in command("readelf", "--dyn-syms", "-W", str(path)).splitlines():
        match = re.search(
            r"^\s*\d+:\s+[0-9a-fA-F]+\s+\d+\s+\w+\s+\w+\s+\w+\s+"
            r"(\S+)\s+(.+)$", line
        )
        if match:
            name = match.group(2).strip().split()[0]
            (imports if match.group(1) == "UND" else exports).add(name)
    return imports, exports


def linked_libraries(path):
    return set(re.findall(
        r"Shared library: \[(.+?)\]",
        command("readelf", "-d", str(path)),
    ))


def printable_strings(path):
    return set(command("strings", "-a", "-n", "9", str(path)).splitlines())


def compare(old, new, include_strings=False):
    a, b = old.read_bytes(), new.read_bytes()
    sa, sb = sections(old), sections(new)
    ia, ea = symbols(old)
    ib, eb = symbols(new)
    la, lb = linked_libraries(old), linked_libraries(new)
    report = {
        "old_size": len(a), "new_size": len(b),
        "old_sha256": hashlib.sha256(a).hexdigest(),
        "new_sha256": hashlib.sha256(b).hexdigest(),
        "identical": a == b,
        "imports_added": sorted(ib - ia),
        "imports_removed": sorted(ia - ib),
        "exports_added": sorted(eb - ea),
        "exports_removed": sorted(ea - eb),
        "libraries_added": sorted(lb - la),
        "libraries_removed": sorted(la - lb),
        "sections": {},
    }
    for name in (".text", ".rodata", ".data", ".dynstr"):
        if name not in sa or name not in sb:
            continue
        oa, na = sa[name]
        ob, nb = sb[name]
        aa, bb = a[oa:oa + na], b[ob:ob + nb]
        report["sections"][name] = {
            "old_size": na, "new_size": nb,
            "identical": aa == bb,
            "different_byte_positions": (
                sum(x != y for x, y in zip(aa, bb)) if na == nb else None
            ),
        }
    if include_strings:
        first, second = printable_strings(old), printable_strings(new)
        # Keep these locally: unreviewed strings can include sensitive values.
        report["relevant_strings_added"] = sorted(
            x for x in second - first if KEYWORDS.search(x)
        )
        report["relevant_strings_removed"] = sorted(
            x for x in first - second if KEYWORDS.search(x)
        )
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("older", type=Path, help="Older extracted SquashFS root")
    parser.add_argument("newer", type=Path, help="Newer extracted SquashFS root")
    parser.add_argument("--json-out", type=Path, help="Save details to local JSON")
    parser.add_argument(
        "--include-strings", action="store_true",
        help="Include strings in local JSON (review before sharing)"
    )
    args = parser.parse_args()
    result = {}
    print(f"{'ELF':43} {'FILE':10} {'CODE':10}  +imports -imports")
    for relative in TARGETS:
        old, new = args.older / relative, args.newer / relative
        if not old.exists() or not new.exists():
            print(f"{relative:43} MISSING")
            continue
        if old.is_symlink() or new.is_symlink():
            print(f"{relative:43} SYMLINK (skipped)")
            continue
        info = compare(old, new, args.include_strings)
        result[relative] = info
        text_section = info["sections"].get(".text", {})
        print(
            f"{relative:43} "
            f"{('SAME' if info['identical'] else 'CHANGED'):10} "
            f"{('SAME' if text_section.get('identical') else 'CHANGED'):10}  "
            f"{len(info['imports_added']):>4}     {len(info['imports_removed']):>4}"
        )
    if args.json_out:
        args.json_out.write_text(json.dumps(result, indent=2) + "\n")
        print(f"Detailed local report: {args.json_out}")
    print("Read-only comparison complete; no firmware executed or flashed.")


if __name__ == "__main__":
    main()
