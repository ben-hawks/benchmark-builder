#!/usr/bin/env python3
"""Fetch the reference-model weights and verify their checksums.

    python scripts/fetch_weights.py --out $BENCH_WEIGHTS
    python scripts/fetch_weights.py --out $BENCH_WEIGHTS --from-local /path/to/checkpoints

File names, download URLs and sha256 sums come from weights/MANIFEST.json. Small derived
artifacts the checkpoints need (normalization stats, caps; listed in SMALL_ARTIFACTS) are
versioned in weights/ and copied rather than downloaded. Exits 1 on any checksum mismatch.

ADAPT (assets/repo/fetch_weights.py in the benchmark-builder skill): set SMALL_ARTIFACTS.
Run downloads on a node with internet (a login node on most clusters); jobs never download.
"""

import argparse
import hashlib
import json
import os
import shutil
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
WEIGHTS_DIR = os.path.join(HERE, "..", "weights")
SMALL_ARTIFACTS = []  # e.g. ["normalization_stats.json"]


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def download(url, dest):
    tmp = dest + ".part"
    with urllib.request.urlopen(url) as r, open(tmp, "wb") as f:
        shutil.copyfileobj(r, f, length=1 << 20)
    os.replace(tmp, dest)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--out", required=True)
    p.add_argument("--from-local", help="copy checkpoints from this directory instead of downloading")
    args = p.parse_args()

    with open(os.path.join(WEIGHTS_DIR, "MANIFEST.json")) as f:
        manifest = json.load(f)
    os.makedirs(args.out, exist_ok=True)
    for name in SMALL_ARTIFACTS:
        shutil.copy(os.path.join(WEIGHTS_DIR, name), args.out)

    ok = True
    for name, info in manifest["files"].items():
        dest = os.path.join(args.out, name)
        if not (os.path.exists(dest) and sha256(dest) == info["sha256"]):
            if args.from_local:
                shutil.copy(os.path.join(args.from_local, name), dest)
            else:
                print(f"downloading {info['url']}")
                download(info["url"], dest)
        got = sha256(dest)
        good = got == info["sha256"]
        ok &= good
        print(f"{name} [{info.get('role', 'reference')}]: {'ok' if good else f'CHECKSUM MISMATCH (got {got})'}")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
