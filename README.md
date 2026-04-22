# Predicting FLS2-flg22 Binding Behavior
This repository contains scripts and workflows used to predict the binding bahevior of a given flg22 sequence to a given FLS2 sequence. AlphaFold3 (AF3) is used to predict the FLS2-flg22-BAK1 complex, and the AF3 scoring metrics (ipTM, pAE, etc.) are used to train simple machine learning models. 

This work was completed as part of a course project, and the aim of this repo is to provide the necessary information to recreate our work on MSU's HPCC. 

---
## Datasets
Two main datasets were used in this analysis. 
1. "Li Dataset" - T. Li et al., Unlocking expanded flagellin perception through rational receptor engineering, *Nature Plants* **11**, 1628-1641 (2025). https://doi.org/10.1038/s41477-025-02049-y
    * This dataset provides pairs of FLS2 and flagellin sequences (97 from *A. thaliana* and 122 from other plant species) which are labeled as "Perceived" or "Not Perceived." In the study, the authors demonstrated that AF3 ipTM score could be used to classify the perception. 
2. "Colaianni Dataset" - N. Colaianni et al., A complex immune response to flagellin epitope variation in commensal communities, *Cell Host & Microbe* **29**, 635-649 (2021). https://doi.org/10.1016/j.chom.2021.02.006 
    * This dataset provides 97 flagellin peptides which are labeled as "Canonical/Immunogenic," "Deviant," "Antagonistic," or "Evading."

---
## Recreating the Results of Li et al.
As a first step, we chose to recreate the result from Li et al. which demonstrated that AF3 ipTM score could be used to differentiate between "Perceived" and "Not Perceived." 

#### Preparation of Input Files
The sequences used in Li et al. were downloaded from the paper's supplementary file (these can be found in the input_prep directory: Li_FullComplex_At.csv (*A. thaliana* samples), Li_FullComplex_NonAt.csv (other species samples)). THese .csv files contain all of the sequences for the flagellin peptides and the name of the corresponding FLS2 sequence. The FLS2 sequences can be found in input_prep/Li_all_FLS2_LRR.fasta, which have been trimmed to only the LRR (extracellular) domain for modeling. 

Additionally, the BAK1/SERK3 coreceptor was also modeled in AF3 based on the results of Li et al., which indicate that accuracy increases when the full ternary complex is modeled. Each BAK1/SERK3 sequence is contained within a separate .fasta file. To determine which coreceptor sequence to use with each, the Zenodo dataset rfom Li et al. was examined:
* AtBAK1 was paired with all AtFLS2 samples (*A. thaliana*)
* SlSERK3 was paired with all SlFLS2 samples (Tomato)
* GmBAK1 was paired with all GmFLS2a and GmFLS2b samples (Soybean)
* NbSERK3A was paired with all others (*N. Benthamiana*)

To predict the structure of each complex using AF3, an input .json file is needed. The scripts make_At_jsons.py and make_nonAt_jsons.py (in the input_prep folder) can be used to generate these inputs:

`python3 make_At_jsons.py  
python3 make_nonAt_jsons.py`

This will specify that AF3 should be run three times with different seeds, as is done in Li et al.