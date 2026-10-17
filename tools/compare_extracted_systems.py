#!/usr/bin/env python3
"""Compare regular-file SHA-256 inventories from two extracted root filesystems.

Read-only: no files are modified. Symlinks and nonregular filesystem objects
are omitted, to avoid following links out of the supplied root directories.
"""
import argparse
import hashlib
from pathlib import Path


WATCH = [
    "/system/bin/update_engine",
    "/system/bin/oobed",
    "/system/bin/ace_otad",
    "/system/bin/otad",
    "/system/lib/libdoppleroobe.so",
    "/system/lib/libcivetweb.so",
    "/system/lib/libace_ota.so",
    "/system/lib/libace_ota_downloader.so",
    "/system/lib/libace_ota_dsts.so",
    "/system/lib/libnative_dev_ota.so",
    "/system/etc/security/otacerts.zip",
    "/system/etc/update_engine/update-payload-key.pub.pem",
]


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def inventory(root):
    found = {}
    for path in root.rglob("*"):
        if path.is_symlink() or not path.is_file():
            continue
        name = "/" + path.relative_to(root).as_posix()
        found[name] = (digest(path), path.stat().st_size)
    return found


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("older", type=Path, help="Older extracted system directory")
    parser.add_argument("newer", type=Path, help="Newer extracted system directory")
    args = parser.parse_args()
    for root in (args.older, args.newer):
        if not root.is_dir():
            parser.error("Not a directory: " + str(root))
    older = inventory(args.older)
    newer = inventory(args.newer)
    old_set, new_set = set(older), set(newer)
    both = old_set & new_set
    changed = {path for path in both if older[path][0] != newer[path][0]}
    print(f"Regular files: older={len(older)}, newer={len(newer)}")
    print(f"Unchanged={len(both - changed)}, changed={len(changed)}, "
          f"added={len(new_set - old_set)}, removed={len(old_set - new_set)}")
    print("\nOTA-related files:")
    for path in WATCH:
        if path not in older:
            status = "ADDED" if path in newer else "ABSENT"
        elif path not in newer:
            status = "REMOVED"
        else:
            status = "CHANGED" if path in changed else "IDENTICAL"
        print(f"{status:9} {path}")
        if path in both:
            print(f"          {older[path][0]} -> {newer[path][0]}")

    print("\nAdded files:")
    for path in sorted(new_set - old_set):
        print(" +", path)
    print("\nRemoved files:")
    for path in sorted(old_set - new_set):
        print(" -", path)


if __name__ == "__main__":
    main()
