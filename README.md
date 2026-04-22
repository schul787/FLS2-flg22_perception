# Predicting FLS2-flg22 Binding Behavior
This repository contains scripts and workflows used to predict the binding bahevior of a given flg22 sequence to a given FLS2 sequence. AlphaFold3 (AF3) is used to predict the FLS2-flg22-BAK1 complex, and the AF3 scoring metrics (ipTM, PAE, etc.) are used to train simple machine learning models. 

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
The files described in this section can be found in the input_prep folder. 

The sequences used in Li et al. were downloaded from the paper's supplementary file (Li_FullComplex_At.csv for *A. thaliana*, Li_FullComplex_NonAt.csv for other species samples). These .csv files contain all of the sequences for the flagellin peptides and the name of the corresponding FLS2 sequence. The FLS2 sequences can be found in input_prep/Li_all_FLS2_LRR.fasta, which have been trimmed to only the LRR (extracellular) domain for modeling. 

Additionally, the BAK1/SERK3 coreceptor was also modeled in AF3 based on the results of Li et al., which indicate that accuracy increases when the full ternary complex is modeled. Each BAK1/SERK3 sequence is contained within a separate .fasta file. To determine which coreceptor sequence to use with each, the Zenodo dataset from Li et al. was examined:
* AtBAK1 was paired with all AtFLS2 samples (*A. thaliana*)
* SlSERK3 was paired with all SlFLS2 samples (Tomato)
* GmBAK1 was paired with all GmFLS2a and GmFLS2b samples (Soybean)
* NbSERK3A was paired with all others (*N. Benthamiana*)

To predict the structure of each complex using AF3, an input .json file is needed. The scripts make_At_jsons.py and make_nonAt_jsons.py (in the input_prep folder) can be used to generate these inputs:

```python3 make_At_jsons.py
python3 make_nonAt_jsons.py
```

This will specify that AF3 should be run three times with different seeds, as is done in Li et al. For detailed information on AF3, see the GitHub page: https://github.com/google-deepmind/alphafold3. 

#### Running AlphaFold3
The files described in this section can all be found in the slurm folder.

To run AF3, a manifest must be created which lists the paths of each input file. First, the make_af3_manifest.py script should be run to generate the manifest, af3_input_manifest.txt. Then, the job script af3_array.sb can be run. This resource allocation and AlphaFold setup is specific to MSU's HPCC. Note that these scripts contain hard-coded file paths, which will need to be modified. 

```python3 make_af3_manifest.py
sbatch af3_array.sb
```

If not all of the jobs successfully run, the make_missing_manifest.py script can be used to search through the output directory and make a new manifest of the jobs that were not completed. 

#### "Perceived" vs. "Not Perceived" Classification
The files described in this section can be found in the analysis folder.

To test the ability of AF3 metrics to distinguish between these two classes, first those metrics must be collected from the individual AF3 output files.  The metrics of interest are pTM, ipTN, FLS2-flg22 ipTM, FLS2-flg22 PAE, BAK1-flg22 ipTM, and BAK1-flg22 PAE. 

Run get_af_scores.py to interate through the AF3 output directories and save the metrics to alphafold_summary_scores.csv. Then, to pair those scores with the actual label (Perceived or Not Perceived), run the add_known_to_score.py to match each complex with the original datasheet, storing both the scores and labels in alphafold_scores_with_known.csv.  

Finally, to compare the classification results with Li et al., run make_roc.py and make_violin_plots.py to plot a Receiver Operating Characteristic Curve and calculate the Area Under the Curve, and to generate violin plots of the ipTM scores. 

```python3 get_af_scores.py
python3 add_known_to_score.py
python3 make_roc.py
python3 make_violin_plots.py
```
---
## Predicting Antagonist vs. Agonist (Immunogenic) Flagellin Peptides
The files described in this section can be found in the notebooks folder. 

While predicting whether a flagellin peptide will be perceived by (i.e., elicit an immune response from) FLS2 is useful, there are other ways these peptides can modulate immune activity through interaction with FLS2. One important class of flagellin peptides are antagonists, which bind FLS2 but disrupt coreceptor binding, and can compete with agonist peptides (for simplicity, agonists will be referred to as immunogenic throughout this section).

Similar to the workflow performed in Li et al. and reproduced here, we used AF3 metrics to classift Antagonist vs. Immunogenic flagellin peptides. The AF3 input preparation and prediction was performed as described above. Specific scripts for this can be found here: https://github.com/aminoroa/FLS2_Project.

#### Proof-of-Concept ML on Perception Dataset
First, to test several strategies for feature ranking and several ML models, the "Perceived" vs. "Not Perceived" dataset from above was used. This enabled us to test different methods with a dataset which we knew could be succesfully classified. All the code is contained within Perception.ipynb. Briefly, feature ranking was done to determine important features, then 6 different ML models (Logistic Regression, Decision Tree, KNN, SVM, Random Forest, and Gradient Boosting) were trained to classify the data. ROC-AUC, balance accuracy, precision, recall, and F1 score were calculated to evaluate the models. 

#### Antagonist vs. Immunogenic Data Labeling
To prepare appropriately labeled data, the Li and Colaianni datasets were combined. Only sample from *Arabidosis thaliana* were used. Additionally, all peptides labeled as "Deviant" or "Evading" by Colaianni were removed. Peptides from the Li dataset labeled as "No Perception" that were not contained in the Colaianni dataset were removed, as there was not a way to definitively determine whether they were evading or antagonistic. Peptides labeled as "Perceived" by Li were kept and assumed to be immunogenic.

Some peptide sequences are labeled as "Antagonists" by Colaianni but are labeled as "Perceived" (implying they elicit an immune response) by Li: flg22-1186, flg22-1410, flg22-5014, and flg22-5015. Due to the small number of antagonist samples (15), we did not want to eliminate these 4. To address this inconsistency, the models were tested on three modified versions of the dataset:
* **Test 1:** Peptides 1186, 1410, 5014, and 5015 were labeled as antagonistic.
     * 15 antagonistic, 25 immunogenic
* **Test 2:** Peptides 1186, 1410, 5014, and 5015 were labeled as immunogenic.
    * 11 antagonistic, 29 immunogenic
* **Test 3:** Peptides 1186, 1410, 5014, and 5015 were removed.
    * 11 antagonistic, 25 immunogenic

The .csv files for each of the three Test Sets can be found in the notebooks folder. 

#### Antagonist vs. Immunogenic Classification
Finally, the methods tested in Perception.ipynb were applied to classify Antagonist vs. Immunogenic peptides. Different feature ranking method demonstrated that FLS2-flg22 PAE was the most important, followed by FLS2-flg22 ipTM, then BAK1-associated scores, and least important were global pTM and ipTM. To further evaulate which features would be necessary/useful for classification, three Feature Seets were tested:
* **All 6:** FLS2-flg22 PAE, FLS2-flg22 ipTM, BAK1-flg22 PAE, BAK1-flg22 ipTM, pTM, ipTM
* **Top 4 (interface):** FLS2-flg22 PAE, FLS2-flg22 ipTM, BAK1-flg22 PAE, BAK1-flg22 ipTM
* **Top 2 (FLS2):** FLS2-flg22 PAE, FLS2-flg22 ipTM

Again, Logistic Regression, Decision Tree, KNN, SVM, Random Forest, and Gradient Boosting ML models were tested for each Test Set and Feature Set. Based primarily on ROC-AUC, Balanced Accuracy, and F1 Score, the best models are listed below. In cases where multiple models/features sets performed similarly, the simplest model with the least features was chosen as the best. (see Antagonism.ipynb for all code, metrics, and plots).
* **Test 1:** SVM with Top 2 Features
    * ROC-AUC: 0.95 ± 0.08
    * Balanced Accuracy: 0.89 ± 0.10
    * F1 Score: 0.92 ± 0.08
* **Test 2:** Random Forest with Top 2 Features
    * ROC-AUC: 0.93 ± 0.08
    * Balanced Accuracy: 0.90 ± 0.12
    * F1 Score: 0.93 ± 0.06
* **Test 3:** Gradient Boosting with Top 2 Features
    * ROC-AUC: 0.95 ± 0.06
    * Balanced Accuracy: 0.91 ± 0.09
    * F1 Score: 0.94 ± 0.05

These results demonstrate successful classification of Antagonist vs. Immunogenic peptides, regardless of how ambiguous peptides were handled. Additionally, they show that only a minimal number of carefully chosen features is necessary. Finally, relatively simple ML models (compared to complex deep learning) were successful for classification. 
