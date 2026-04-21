#!/usr/bin/env python3

from pathlib import Path

INPUT_DIR = Path("./inputs/")
OUTPUT_DIR = Path("./outputs/")
MISSING_MANIFEST = Path("./missing_jobs_manifest.txt")


def main():
    json_files = sorted(INPUT_DIR.glob("*.json"))

    if not json_files:
        raise SystemExit(f"No JSON files found in {INPUT_DIR}")

    missing = []

    for json_path in json_files:
        base_name = json_path.stem
        expected_output_dir = OUTPUT_DIR / f"{base_name}_output"

        if not expected_output_dir.is_dir():
            missing.append(json_path.resolve())

    MISSING_MANIFEST.parent.mkdir(parents=True, exist_ok=True)

    with open(MISSING_MANIFEST, "w") as f:
        for path in missing:
            f.write(str(path) + "\n")

    print(f"Total input JSONs: {len(json_files)}")
    print(f"Missing outputs:   {len(missing)}")
    print(f"Wrote manifest:    {MISSING_MANIFEST}")


if __name__ == "__main__":
    main()