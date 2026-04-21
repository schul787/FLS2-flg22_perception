import pandas as pd

# ---------- file paths ----------
summary_file = "alphafold_summary_scores.csv"
li_at_file = "../input_prep/Li_FullComplex_At.csv"
li_nonat_file = "../input_prep/Li_FullComplex_NonAt.csv"
output_file = "alphafold_scores_with_known.csv"


# ---------- read the summary csv ----------
summary_df = pd.read_csv(summary_file)

# Make sure the expected column exists
if "Name" not in summary_df.columns:
    raise ValueError("Could not find 'Name' column in summary CSV.")


# ---------- read the Li csv files ----------
# These files have the true header on the second row, so use header=1
li_at_df = pd.read_csv(li_at_file, header=1)
li_nonat_df = pd.read_csv(li_nonat_file, header=1)

# Keep only the columns we need
li_at_df = li_at_df[["receptor", "ligand_name", "Known_outcome"]]
li_nonat_df = li_nonat_df[["receptor", "ligand_name", "Known_outcome"]]

# Combine them
li_df = pd.concat([li_at_df, li_nonat_df], ignore_index=True)

# Remove rows missing needed values
li_df = li_df.dropna(subset=["receptor", "ligand_name", "Known_outcome"])

# Build the matching prefix: receptor_ligand_name
li_df["match_prefix"] = (
    li_df["receptor"].astype(str).str.strip() + "_" +
    li_df["ligand_name"].astype(str).str.strip()
)

# Create a lookup dictionary
prefix_to_outcome = dict(zip(li_df["match_prefix"], li_df["Known_outcome"]))


# ---------- match to summary dataframe ----------
def find_known_outcome(name):
    name = str(name).strip()
    for prefix, outcome in prefix_to_outcome.items():
        if name.startswith(prefix):
            return outcome
    return pd.NA

summary_df["Known Outcome"] = summary_df["Name"].apply(find_known_outcome)


# ---------- save output ----------
summary_df.to_csv(output_file, index=False)

print(f"Saved updated file to: {output_file}")
print(f"Matched {summary_df['Known Outcome'].notna().sum()} of {len(summary_df)} rows.")