# TCGA Wet-Lab Validated Target Mining — Pipeline Summary

**Generated:** 2026-08-02 16:53  
**Model:** deepseek-v4-pro  
**Run tag:** `default`  

---

## Overview

| Metric | Value |
|--------|-------|
| Cancer types | 33 |
| Papers screened | 67,046 |
| Wet-lab validated | 41,263 (61.5%) |
| Review / bioinformatics | 501 |
| Insufficient info | 473 |
| Other (no wet lab) | 24,809 |
| Final target-disease associations | 31,134 |
| Unique targets | 14,238 |
| Cross-cancer targets (≥3 cancers) | 3,053 |
| Gene targets standardized | 51,768 (94.3%) |

---

## Per-Cancer Breakdown

| Code | Disease | Screened | Wet Lab | Rate | Review | Insuff. | Other | Final Targets | Supp. Papers |
|------|---------|----------|---------|------|--------|---------|-------|---------------|--------------|
| ACC | Adrenocortical Carcinoma | 205 | 83 | 40.5% | 1 | 1 | 120 | 135 | 75 |
| BLCA | Bladder Cancer | 1392 | 715 | 51.4% | 5 | 15 | 657 | 639 | 631 |
| BRCA | Breast Cancer | 12680 | 7669 | 60.5% | 97 | 86 | 4828 | 4144 | 7106 |
| CESC | Cervical Cancer | 902 | 478 | 53.0% | 10 | 8 | 406 | 511 | 442 |
| CHOL | Cholangiocarcinoma | 593 | 360 | 60.7% | 6 | 7 | 220 | 454 | 312 |
| COAD | Colon Cancer | 7737 | 4585 | 59.3% | 54 | 43 | 3055 | 3141 | 4197 |
| DLBC | DLBC Lymphoma | 928 | 489 | 52.7% | 7 | 7 | 425 | 490 | 470 |
| ESCA | Esophageal Cancer | 547 | 250 | 45.7% | 2 | 5 | 290 | 298 | 222 |
| GBM | Glioblastoma | 3335 | 2319 | 69.5% | 31 | 28 | 957 | 1853 | 2113 |
| HNSC | Head & Neck Cancer | 1325 | 771 | 58.2% | 10 | 8 | 536 | 747 | 715 |
| KICH | Kidney Chromophobe | 112 | 22 | 19.6% | 1 | 0 | 89 | 31 | 20 |
| KIRC | Kidney Clear Cell Carcinoma | 531 | 300 | 56.5% | 6 | 10 | 215 | 368 | 285 |
| KIRP | Kidney Papillary Cell Carcinoma | 201 | 37 | 18.4% | 2 | 1 | 161 | 58 | 36 |
| LAML | Acute Myeloid Leukemia | 4056 | 2568 | 63.3% | 29 | 25 | 1434 | 1763 | 2426 |
| LGG | Low-Grade Glioma | 328 | 97 | 29.6% | 7 | 4 | 220 | 143 | 91 |
| LIHC | Hepatocellular Carcinoma | 4136 | 2995 | 72.4% | 23 | 33 | 1085 | 2572 | 2774 |
| LUAD | Lung Adenocarcinoma | 1258 | 849 | 67.5% | 6 | 11 | 392 | 904 | 779 |
| LUSC | Lung Squamous Cell Carcinoma | 187 | 93 | 49.7% | 3 | 1 | 90 | 141 | 88 |
| MESO | Mesothelioma | 414 | 261 | 63.0% | 4 | 2 | 147 | 283 | 226 |
| OV | Ovarian Cancer | 3324 | 1930 | 58.1% | 21 | 17 | 1356 | 1505 | 1720 |
| PAAD | Pancreatic Cancer | 3061 | 2163 | 70.7% | 26 | 29 | 843 | 1758 | 1998 |
| PCPG | Pheochromocytoma & Paraganglioma | 415 | 186 | 44.8% | 7 | 6 | 216 | 186 | 172 |
| PRAD | Prostate Cancer | 5217 | 3522 | 67.5% | 37 | 36 | 1622 | 2370 | 3255 |
| READ | Rectal Cancer | 278 | 62 | 22.3% | 3 | 1 | 212 | 86 | 50 |
| SARC | Sarcoma | 4197 | 2732 | 65.1% | 20 | 24 | 1421 | 1815 | 2346 |
| SKCM | Cutaneous Melanoma | 4733 | 3204 | 67.7% | 43 | 29 | 1457 | 2088 | 2797 |
| STAD | Gastric Cancer | 2050 | 1161 | 56.6% | 10 | 21 | 858 | 1223 | 1072 |
| TGCT | Testicular Cancer | 185 | 61 | 33.0% | 4 | 1 | 119 | 81 | 53 |
| THCA | Thyroid Cancer | 1259 | 668 | 53.1% | 11 | 4 | 576 | 617 | 618 |
| THYM | Thymoma | 244 | 164 | 67.2% | 1 | 2 | 77 | 183 | 144 |
| UCEC | Endometrial Cancer | 719 | 275 | 38.2% | 5 | 3 | 436 | 343 | 250 |
| UCS | Uterine Carcinosarcoma | 114 | 24 | 21.1% | 0 | 0 | 90 | 29 | 21 |
| UVM | Uveal Melanoma | 383 | 170 | 44.4% | 9 | 5 | 199 | 175 | 108 |

*Screened = total papers processed by LLM; Wet Lab = papers with wet-lab validation; Final Targets = unique target-disease pairs after dedup; Supp. Papers = unique PMIDs supporting final targets.*

---

## Cross-Cancer Targets (≥3 cancer types)

3053 targets appear in 3 or more cancer types.

| # | Target | Cancer Types |
|---|--------|-------------|
| 1 | TP53 | 30 (ACC, BLCA, BRCA, CESC, CHOL, COAD, DLBC, ESCA, GBM, HNSC, KICH, KIRC, LAML, LGG, LIHC, LUAD, LUSC, MESO, OV, PAAD, PCPG, PRAD, READ, SARC, SKCM, STAD, TGCT, THCA, THYM, UCEC) |
| 2 | VEGFA | 28 (ACC, BLCA, BRCA, CESC, CHOL, COAD, DLBC, ESCA, GBM, HNSC, KIRC, KIRP, LAML, LGG, LIHC, LUAD, LUSC, MESO, OV, PAAD, PCPG, PRAD, SARC, SKCM, STAD, THCA, UCEC, UCS) |
| 3 | MYC | 27 (BLCA, BRCA, CESC, CHOL, COAD, DLBC, ESCA, GBM, HNSC, KIRC, KIRP, LAML, LGG, LIHC, LUAD, MESO, OV, PAAD, PRAD, SARC, SKCM, STAD, TGCT, THCA, THYM, UCEC, UVM) |
| 4 | AKT1 | 26 (BLCA, BRCA, CESC, CHOL, COAD, DLBC, ESCA, GBM, HNSC, KIRC, KIRP, LAML, LIHC, LUAD, MESO, OV, PAAD, PRAD, READ, SARC, SKCM, STAD, THCA, THYM, UCEC, UCS) |
| 5 | MET | 26 (ACC, BRCA, COAD, DLBC, ESCA, GBM, HNSC, KIRC, KIRP, LAML, LGG, LIHC, LUAD, LUSC, MESO, OV, PAAD, PCPG, PRAD, SARC, SKCM, STAD, THCA, THYM, UCEC, UVM) |
| 6 | EGFR | 26 (BLCA, BRCA, CESC, CHOL, COAD, ESCA, GBM, HNSC, KIRC, LAML, LGG, LIHC, LUAD, LUSC, MESO, OV, PAAD, PRAD, READ, SARC, SKCM, STAD, THCA, THYM, UCEC, UVM) |
| 7 | MTOR | 26 (ACC, BRCA, CESC, CHOL, COAD, DLBC, ESCA, GBM, HNSC, KIRC, LAML, LGG, LIHC, LUAD, LUSC, MESO, OV, PAAD, PRAD, SARC, SKCM, STAD, THCA, THYM, UCEC, UVM) |
| 8 | BCL2 | 25 (BLCA, BRCA, CESC, CHOL, COAD, DLBC, ESCA, GBM, HNSC, LAML, LGG, LIHC, LUAD, LUSC, OV, PAAD, PRAD, SARC, SKCM, STAD, TGCT, THCA, THYM, UCEC, UVM) |
| 9 | PTEN | 25 (BLCA, BRCA, CESC, CHOL, COAD, DLBC, GBM, HNSC, KIRC, KIRP, LAML, LGG, LIHC, LUSC, MESO, OV, PAAD, PRAD, SARC, SKCM, STAD, TGCT, THCA, THYM, UCEC) |
| 10 | CDKN1A | 24 (BLCA, BRCA, CESC, CHOL, COAD, DLBC, ESCA, GBM, HNSC, LAML, LGG, LIHC, LUAD, MESO, OV, PAAD, PCPG, PRAD, SARC, SKCM, STAD, TGCT, THCA, UCEC) |
| 11 | BIRC5 | 24 (BLCA, BRCA, COAD, DLBC, ESCA, GBM, HNSC, KIRC, KIRP, LAML, LGG, LIHC, LUAD, MESO, OV, PAAD, PRAD, READ, SARC, SKCM, STAD, THCA, UCEC, UCS) |
| 12 | ERBB2 | 24 (BLCA, BRCA, CESC, CHOL, COAD, ESCA, GBM, HNSC, KIRC, LAML, LIHC, LUAD, MESO, OV, PAAD, PRAD, SARC, SKCM, STAD, THCA, THYM, UCEC, UCS, UVM) |
| 13 | STAT3 | 24 (BLCA, BRCA, CESC, CHOL, COAD, DLBC, ESCA, GBM, HNSC, KIRC, LAML, LGG, LIHC, LUAD, MESO, OV, PAAD, PRAD, READ, SARC, SKCM, STAD, THCA, UCEC) |
| 14 | JUN | 23 (BLCA, BRCA, CESC, COAD, DLBC, ESCA, GBM, HNSC, LAML, LGG, LIHC, LUAD, MESO, OV, PAAD, PCPG, PRAD, SARC, SKCM, STAD, THCA, THYM, UVM) |
| 15 | HSP90AA1 | 23 (ACC, BLCA, BRCA, CESC, COAD, DLBC, ESCA, GBM, HNSC, KIRC, KIRP, LAML, LIHC, LUAD, MESO, OV, PAAD, PRAD, SARC, SKCM, STAD, THCA, UVM) |
| 16 | PARP1 | 23 (BLCA, BRCA, CESC, CHOL, COAD, DLBC, GBM, HNSC, LAML, LIHC, LUAD, MESO, OV, PAAD, PCPG, PRAD, READ, SARC, SKCM, STAD, THCA, UCS, UVM) |
| 17 | YAP1 | 23 (ACC, BLCA, BRCA, CESC, CHOL, COAD, ESCA, GBM, HNSC, KIRC, LIHC, LUAD, LUSC, MESO, OV, PAAD, PRAD, SARC, SKCM, STAD, THCA, UCEC, UVM) |
| 18 | CCND1 | 23 (BRCA, CHOL, COAD, DLBC, ESCA, GBM, HNSC, KIRC, KIRP, LAML, LGG, LIHC, LUAD, MESO, OV, PAAD, PRAD, SARC, SKCM, STAD, THCA, THYM, UCEC) |
| 19 | CTNNB1 | 23 (ACC, BLCA, BRCA, CESC, CHOL, COAD, DLBC, ESCA, GBM, HNSC, KIRC, LAML, LIHC, LUAD, MESO, OV, PAAD, PRAD, SARC, SKCM, STAD, THCA, UCEC) |
| 20 | IGF1R | 23 (ACC, BRCA, CESC, CHOL, COAD, GBM, HNSC, KIRC, LAML, LIHC, LUAD, MESO, OV, PAAD, PRAD, READ, SARC, SKCM, STAD, THCA, THYM, UCEC, UVM) |

---

## Gene Standardization

Target names from LLM extraction are mapped to HGNC-approved official symbols, NCBI Gene IDs, and Ensembl IDs using the [HGNC complete set](https://www.genenames.org/).

### Gene / Protein Targets

| Metric | Value |
|--------|-------|
| Attempted | 54,900 |
| Successfully mapped | 51,768 (94.3%) |
| Not found in HGNC | 3,132 |
| Alias / prev-symbol corrected | 1,931 (e.g. HSP90 → HSP90AA1, PI3K; PIK3CA → PIK3CA, AKT; AKT1; Akt → AKT1, RAC1; Rac1 → RAC1, ARHGDIB; RhoGDI2 → ARHGDIB) |

### Non-Gene Targets (correctly skipped)

These target types have no NCBI Gene ID and are not mapped:

| Type | Count |
|------|-------|
| pathway | 6,854 |
| mirna | 1,871 |
| lncrna | 605 |
| protein complex | 66 |
| unknown | 57 |
| circrna | 42 |
| gene family | 25 |
| protein family | 17 |
| gene fusion | 12 |
| fusion gene | 7 |
| fusion protein | 6 |
| antigen | 3 |
| protein isoform | 3 |
| tsrna | 3 |
| fusion gene/protein | 3 |
| trna-derived fragment | 2 |
| trna | 2 |
| viral oncogene | 2 |
| snorna | 2 |
| erna | 2 |
| fusion | 2 |
| retrotransposon | 1 |
| complex | 1 |
| promoter | 1 |
| ncrna | 1 |
| protein interaction | 1 |
| protein (fusion) | 1 |
| scarna | 1 |
| other | 1 |
| pirna | 1 |
| protein-protein interaction | 1 |
| chimeric rna | 1 |
| viral protein | 1 |
| locus | 1 |
| biomarker panel | 1 |

---

## Configuration

- **Model:** deepseek-v4-pro
- **Targets per cancer cap:** none (all wet-lab papers used)
- **Output CSV:** `output/final_targets.csv`
- **Extraction source:** `data/extractions_all.json`
