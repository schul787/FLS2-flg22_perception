#!/usr/bin/env python3

from pathlib import Path

# EDIT THESE
INPUT_DIR = Path("/mnt/home/schul787/CHE882/li_recreation/inputs")
MANIFEST = Path("/mnt/home/schul787/CHE882/li_recreation/af3_input_manifest.txt")

def main():
    json_files = sorted(INPUT_DIR.glob("*.json"))

    if not json_files:
        raise SystemExit(f"No .json files found in {INPUT_DIR}")

    MANIFEST.parent.mkdir(parents=True, exist_ok=True)

    with open(MANIFEST, "w") as f:
        for path in json_files:
            f.write(str(path.resolve()) + "\n")

    print(f"Wrote manifest with {len(json_files)} inputs to {MANIFEST}")

if __name__ == "__main__":
    main()