#!/usr/bin/env python3

import csv
import json
from pathlib import Path

# ========= USER-EDITABLE SETTINGS =========
OUTPUTS_DIR = Path("../outputs")
CSV_PATH = Path("alphafold_summary_scores.csv")
SEEDS = [1, 2, 3]
# ==========================================


def get_single_subdirectory(parent: Path):
    """Return the single subdirectory inside parent, or None if not found/ambiguous."""
    subdirs = [p for p in parent.iterdir() if p.is_dir()]
    if len(subdirs) != 1:
        return None
    return subdirs[0]


def load_json(json_path: Path):
    """Load a JSON file and return the parsed dict."""
    with open(json_path, "r") as f:
        return json.load(f)


def safe_get_matrix_value(matrix, i, j):
    """Safely get matrix[i][j], returning blank string if unavailable."""
    try:
        return matrix[i][j]
    except (IndexError, TypeError):
        return ""


def extract_seed_metrics(seed_json: dict):
    """
    Extract the requested metrics from one summary_confidences.json file.
    
    Returns a dict with:
      ptm
      iptm
      fls2_flg22_iptm   -> [0,1] from chain_pair_iptm
      fls2_flg22_pae    -> [0,1] from chain_pair_pae_min
      bak1_flg22_iptm   -> [2,1] from chain_pair_iptm
      bak1_flg22_pae    -> [2,1] from chain_pair_pae_min
    """

    chain_pair_iptm = seed_json.get("chain_pair_iptm", [])
    chain_pair_pae_min = seed_json.get("chain_pair_pae_min", [])

    return {
        "ptm": seed_json.get("ptm", ""),
        "iptm": seed_json.get("iptm", ""),
        "fls2_flg22_iptm": safe_get_matrix_value(chain_pair_iptm, 0, 1),
        "fls2_flg22_pae": safe_get_matrix_value(chain_pair_pae_min, 0, 1),
        "bak1_flg22_iptm": safe_get_matrix_value(chain_pair_iptm, 2, 1),
        "bak1_flg22_pae": safe_get_matrix_value(chain_pair_pae_min, 2, 1),
    }


def main():
    if not OUTPUTS_DIR.exists() or not OUTPUTS_DIR.is_dir():
        raise FileNotFoundError(f"Could not find outputs directory: {OUTPUTS_DIR}")

    rows = []

    # Build CSV header
    header = ["Name"]
    for seed in SEEDS:
        header.extend([
            f"Rep {seed} ptm",
            f"Rep {seed} iptm",
            f"Rep {seed} FLS2-flg22 iptm",
            f"Rep {seed} FLS2-flg22 pae",
            f"Rep {seed} BAK1-flg22 iptm",
            f"Rep {seed} BAK1-flg22 pae",
        ])

    # Iterate through each subdirectory in ./outputs
    for output_subdir in sorted([p for p in OUTPUTS_DIR.iterdir() if p.is_dir()]):
        row = {"Name": output_subdir.name}

        nested_dir = get_single_subdirectory(output_subdir)
        if nested_dir is None:
            print(f"Skipping {output_subdir}: expected exactly one subdirectory inside.")
            # Fill blanks for all expected seed columns
            for seed in SEEDS:
                row[f"Rep {seed} ptm"] = ""
                row[f"Rep {seed} iptm"] = ""
                row[f"Rep {seed} FLS2-flg22 iptm"] = ""
                row[f"Rep {seed} FLS2-flg22 pae"] = ""
                row[f"Rep {seed} BAK1-flg22 iptm"] = ""
                row[f"Rep {seed} BAK1-flg22 pae"] = ""
            rows.append(row)
            continue

        # Process each seed directory
        for seed in SEEDS:
            seed_dir = nested_dir / f"seed-{seed}_sample-0"
            json_path = seed_dir / "summary_confidences.json"

            if not json_path.exists():
                print(f"Missing file: {json_path}")
                row[f"Rep {seed} ptm"] = ""
                row[f"Rep {seed} iptm"] = ""
                row[f"Rep {seed} FLS2-flg22 iptm"] = ""
                row[f"Rep {seed} FLS2-flg22 pae"] = ""
                row[f"Rep {seed} BAK1-flg22 iptm"] = ""
                row[f"Rep {seed} BAK1-flg22 pae"] = ""
                continue

            try:
                data = load_json(json_path)
                metrics = extract_seed_metrics(data)

                row[f"Rep {seed} ptm"] = metrics["ptm"]
                row[f"Rep {seed} iptm"] = metrics["iptm"]
                row[f"Rep {seed} FLS2-flg22 iptm"] = metrics["fls2_flg22_iptm"]
                row[f"Rep {seed} FLS2-flg22 pae"] = metrics["fls2_flg22_pae"]
                row[f"Rep {seed} BAK1-flg22 iptm"] = metrics["bak1_flg22_iptm"]
                row[f"Rep {seed} BAK1-flg22 pae"] = metrics["bak1_flg22_pae"]

            except Exception as e:
                print(f"Error reading {json_path}: {e}")
                row[f"Rep {seed} ptm"] = ""
                row[f"Rep {seed} iptm"] = ""
                row[f"Rep {seed} FLS2-flg22 iptm"] = ""
                row[f"Rep {seed} FLS2-flg22 pae"] = ""
                row[f"Rep {seed} BAK1-flg22 iptm"] = ""
                row[f"Rep {seed} BAK1-flg22 pae"] = ""

        rows.append(row)

    # Write CSV
    with open(CSV_PATH, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} rows to {CSV_PATH}")


if __name__ == "__main__":
    main()
