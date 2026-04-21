#!/usr/bin/env python3

"""
Create AlphaFold3 input JSON files for FLS2–flg22–coreceptor complexes.

For each row in the CSV:
- FLS2 name comes from the 'receptor' column
- FLS2 sequence comes from Li_all_FLS2_LRR.fasta
- flg22 sequence comes from the 'ligand_sequence' column
- flg22 name comes from the 'ligand_name' column
- coreceptor sequence comes from:
    * GmBAK1.fasta     if receptor is GmFLS2a or GmFLS2b
    * SlSERK3A.fasta   if receptor is SlFLS2
    * NbSERK3A.fasta   for all others

Output JSON filename:
    {receptor}_{ligand_name}_{coreceptor_name}.json

The job name inside the JSON is the same as the filename stem.
"""

from pathlib import Path
import json
import re

import pandas as pd
from Bio import SeqIO


# =========================
# USER-EDITABLE PATHS
# =========================

CSV_PATH = Path("/mnt/home/schul787/CHE882/li_recreation/input_prep/Li_FullComplex_NonAt.csv")
FLS2_FASTA_PATH = Path("/mnt/home/schul787/CHE882/li_recreation/input_prep/Li_all_FLS2_LRR.fasta")

# Directory containing:
#   GmBAK1.fasta
#   SlSERK3A.fasta
#   NbSERK3A.fasta
CORECEPTOR_FASTA_DIR = Path("/mnt/home/schul787/CHE882/li_recreation/input_prep")

# Directory where output JSON files should be written
OUTPUT_JSON_DIR = Path("/mnt/home/schul787/CHE882/li_recreation/inputs")


# =========================
# CONSTANTS
# =========================

MODEL_SEEDS = [1, 2, 3]

CORECEPTOR_RULES = {
    "GmFLS2a": "GmBAK1.fasta",
    "GmFLS2b": "GmBAK1.fasta",
    "SlFLS2": "SlSERK3A.fasta",
}
DEFAULT_CORECEPTOR_FASTA = "NbSERK3A.fasta"


# =========================
# HELPERS
# =========================

def sanitize_name(text: str) -> str:
    """
    Make a string safe for filenames/job names.
    Keeps letters, numbers, underscores, hyphens, and dots.
    Replaces other characters with underscores.
    """
    text = str(text).strip()
    text = re.sub(r"[^\w.\-]+", "_", text)
    text = re.sub(r"_+", "_", text)
    return text.strip("_")


def load_fasta_to_dict(fasta_path: Path) -> dict:
    """
    Load a FASTA file into a dict: {record.id: sequence}.
    """
    seq_dict = {}
    for record in SeqIO.parse(str(fasta_path), "fasta"):
        seq_dict[record.id] = str(record.seq).replace("\n", "").strip()
    return seq_dict


def load_single_fasta_sequence(fasta_path: Path) -> tuple[str, str]:
    """
    Load the first sequence from a FASTA file.
    Returns:
        (sequence_name, sequence_string)
    """
    records = list(SeqIO.parse(str(fasta_path), "fasta"))
    if not records:
        raise ValueError(f"No sequences found in FASTA: {fasta_path}")
    record = records[0]
    return record.id, str(record.seq).replace("\n", "").strip()


def choose_coreceptor_fasta(receptor_name: str) -> str:
    """
    Return the appropriate coreceptor FASTA filename for a given receptor.
    """
    return CORECEPTOR_RULES.get(receptor_name, DEFAULT_CORECEPTOR_FASTA)


def build_af3_json(jobname: str, fls2_seq: str, flg22_seq: str, coreceptor_seq: str) -> dict:
    """
    Build AlphaFold3 input JSON with three protein sequences.
    """
    return {
        "name": jobname,
        "sequences": [
            {
                "protein": {
                    "id": "A",
                    "sequence": fls2_seq
                }
            },
            {
                "protein": {
                    "id": "B",
                    "sequence": flg22_seq
                }
            },
            {
                "protein": {
                    "id": "C",
                    "sequence": coreceptor_seq
                }
            }
        ],
        "modelSeeds": MODEL_SEEDS,
        "dialect": "alphafold3",
        "version": 1
    }


# =========================
# MAIN
# =========================

def main():
    OUTPUT_JSON_DIR.mkdir(parents=True, exist_ok=True)

    # Load FLS2 receptor sequences
    fls2_sequences = load_fasta_to_dict(FLS2_FASTA_PATH)

    # Read CSV
    # The attached CSV appears to have the true header on the second row,
    # so header=1 is used here.
    df = pd.read_csv(CSV_PATH, header=1)

    required_columns = ["receptor", "ligand_name", "ligand_sequence"]
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise ValueError(
            f"Missing required columns in CSV: {missing}\n"
            f"Found columns: {list(df.columns)}"
        )

    n_written = 0

    for i, row in df.iterrows():
        receptor = str(row["receptor"]).strip()
        ligand_name = str(row["ligand_name"]).strip()
        ligand_sequence = str(row["ligand_sequence"]).strip().replace(" ", "")

        if receptor not in fls2_sequences:
            raise KeyError(
                f"Receptor '{receptor}' from CSV row {i} was not found in "
                f"{FLS2_FASTA_PATH.name}"
            )

        fls2_sequence = fls2_sequences[receptor]

        coreceptor_fasta_name = choose_coreceptor_fasta(receptor)
        coreceptor_fasta_path = CORECEPTOR_FASTA_DIR / coreceptor_fasta_name

        if not coreceptor_fasta_path.exists():
            raise FileNotFoundError(
                f"Coreceptor FASTA not found: {coreceptor_fasta_path}"
            )

        coreceptor_name, coreceptor_sequence = load_single_fasta_sequence(coreceptor_fasta_path)

        jobname = sanitize_name(f"{receptor}_{ligand_name}_{coreceptor_name}")
        output_path = OUTPUT_JSON_DIR / f"{jobname}.json"

        af3_input = build_af3_json(
            jobname=jobname,
            fls2_seq=fls2_sequence,
            flg22_seq=ligand_sequence,
            coreceptor_seq=coreceptor_sequence,
        )

        with open(output_path, "w") as f:
            json.dump(af3_input, f, indent=2)

        n_written += 1

    print(f"Wrote {n_written} AlphaFold3 JSON files to: {OUTPUT_JSON_DIR}")


if __name__ == "__main__":
    main()