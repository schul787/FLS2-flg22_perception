#!/usr/bin/env python3

from pathlib import Path
import json
import re
import pandas as pd
from Bio import SeqIO


# =========================
# USER PATHS
# =========================

CSV_PATH = Path("/mnt/home/schul787/CHE882/li_recreation/input_prep/Li_FullComplex_At.csv")

# Same FASTA used previously
FLS2_FASTA_PATH = Path("/mnt/home/schul787/CHE882/li_recreation/input_prep/Li_all_FLS2_LRR.fasta")

ATBAK1_FASTA_PATH = Path("/mnt/home/schul787/CHE882/li_recreation/input_prep/AtBAK1.fasta")

OUTPUT_JSON_DIR = Path("/mnt/home/schul787/CHE882/li_recreation/inputs")


# =========================
# CONSTANTS
# =========================

FLS2_NAME = "AtFLS2"
MODEL_SEEDS = [1, 2, 3]


# =========================
# HELPERS
# =========================

def sanitize_name(text):
    text = str(text).strip()
    text = re.sub(r"[^\w.\-]+", "_", text)
    text = re.sub(r"_+", "_", text)
    return text.strip("_")


def load_fasta_dict(fasta_path):
    seq_dict = {}
    for record in SeqIO.parse(str(fasta_path), "fasta"):
        seq_dict[record.id] = str(record.seq).replace("\n", "").strip()
    return seq_dict


def load_single_sequence(fasta_path):
    records = list(SeqIO.parse(str(fasta_path), "fasta"))
    record = records[0]
    return record.id, str(record.seq).replace("\n", "").strip()


def build_af3_json(jobname, fls2_seq, flg22_seq, coreceptor_seq):

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

    # Load all FLS2 sequences
    fls2_sequences = load_fasta_dict(FLS2_FASTA_PATH)

    if FLS2_NAME not in fls2_sequences:
        raise ValueError(f"{FLS2_NAME} not found in {FLS2_FASTA_PATH}")

    fls2_sequence = fls2_sequences[FLS2_NAME]

    # Load AtBAK1
    coreceptor_name, coreceptor_sequence = load_single_sequence(ATBAK1_FASTA_PATH)

    # Read CSV
    df = pd.read_csv(CSV_PATH, header=1)

    n_written = 0

    for _, row in df.iterrows():

        ligand_name = str(row["ligand_name"]).strip()
        ligand_sequence = str(row["ligand_sequence"]).strip().replace(" ", "")

        jobname = sanitize_name(f"{FLS2_NAME}_{ligand_name}_{coreceptor_name}")

        json_path = OUTPUT_JSON_DIR / f"{jobname}.json"

        af3_json = build_af3_json(
            jobname,
            fls2_sequence,
            ligand_sequence,
            coreceptor_sequence
        )

        with open(json_path, "w") as f:
            json.dump(af3_json, f, indent=2)

        n_written += 1

    print(f"Wrote {n_written} JSON files to {OUTPUT_JSON_DIR}")


if __name__ == "__main__":
    main()