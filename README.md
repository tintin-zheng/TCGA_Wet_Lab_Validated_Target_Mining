# TCGA Wet-Lab Validated Target Mining Pipeline

An LLM-powered automated pipeline that systematically mines **wet-lab experimentally validated** molecular targets across all **33 TCGA cancer types** from high-impact biomedical literature.

## Overview

PubMed contains >37 million biomedical articles. Target-disease associations are scattered across tens of thousands of papers, and most bioinformatics predictions lack experimental validation. This pipeline:

1. Searches top-tier journals for each cancer type
2. Uses a large language model (DeepSeek) to read every abstract and determine whether it contains wet-lab validation
3. Extracts structured target-disease associations (gene symbol, expression change, functional role, experimental evidence, etc.)
4. Outputs a deduplicated CSV ready for downstream analysis

## Pipeline Architecture

```
Step 0 (pre-survey) -> Step 1 (search) -> Step 2 (LLM extract) -> Step 3 (integrate)
     │                     │                    │                     │
     ▼                     ▼                    ▼                     ▼
  Count PubMed      33 cancers ×           LLM judges             Filter wet-lab
  papers per        200 papers each        each abstract         → deduplicate
  cancer type       = 6,600 max           + extracts             → aggregate
                                          structured targets     → output CSV
```

| Step | Script | What It Does |
|------|--------|--------------|
| 0 | `step_0.py` | Pre-survey: count PubMed hits per cancer, estimate cost |
| 1 | `step1_search.py` | PubMed search + batch abstract fetching (37 Q1 journals) |
| 2 | `step2_extract.py` | DeepSeek LLM classifies wet-lab validation + extracts targets |
| 3 | `step3_integrate.py` | Filter, deduplicate, majority-vote aggregation, export CSV |

## Setup

### Prerequisites

```bash
pip install biopython openai pandas tqdm
```

### Configuration

```bash
cp config.example.py config.py
# Edit config.py with your API keys:
#   - NCBI_EMAIL: your email for PubMed API
#   - NCBI_API_KEY: optional, improves rate limits
#   - DEEPSEEK_API_KEY: from platform.deepseek.com
```

### Environment Variables (Optional)

| Variable | Purpose | Default |
|----------|---------|---------|
| `PIPELINE_CANCERS` | Run specific cancer types, e.g. `ACC,BRCA,LIHC` | All 33 |
| `PIPELINE_TAG` | Suffix for output files (isolates runs) | None |
| `PIPELINE_MAX_CANCERS` | Limit to first N cancer types | All |
| `PIPELINE_PAPERS_PER_CANCER` | Cap papers per cancer in Step 2 | All |
| `EXTRACT_MAX_WORKERS` | Thread count for LLM extraction | 8 |
| `EXTRACT_MAX_RETRIES` | Max API retries | 3 |

## Usage

### Full Pipeline

```bash
# Step 0: Pre-survey (optional)
python step_0.py

# Step 1: Search PubMed
python step1_search.py
# Output: data/papers_all.json  (one JSON per cancer + combined)

# Step 2: LLM Target Extraction
python step2_extract.py
# Output: data/extractions_all.json

# Step 3: Integrate & Export
python step3_integrate.py
# Output: output/final_targets.csv
```

### Mini Test Run (single cancer)

```bash
PIPELINE_CANCERS=ACC PIPELINE_TAG=accmini python step1_search.py
PIPELINE_CANCERS=ACC PIPELINE_TAG=accmini python step2_extract.py
PIPELINE_CANCERS=ACC PIPELINE_TAG=accmini python step3_integrate.py
```

### Resume After Interruption

All steps support checkpoint/resume — just re-run the same command. Already-processed cancer types (Step 1) or PMIDs (Step 2) will be skipped automatically.

```bash
# Prevent laptop sleep during long Step 2 runs
caffeinate -i python step2_extract.py
```

## Output Format

The final CSV (`output/final_targets.csv`) contains one row per target-disease association:

| Column | Description |
|--------|-------------|
| `id` | Primary key: `{TCGA_CODE}_{sequence_number}` |
| `tcga_code` | TCGA cancer type code (e.g., ACC, BRCA) |
| `disease_en` / `disease_cn` | Disease name |
| `target` | HGNC gene symbol, miRNA, lncRNA, or pathway name |
| `target_type` | gene / protein / miRNA / lncRNA / pathway |
| `expression_change` | Upregulated / Downregulated / Unchanged / Null |
| `functional_role` | Oncogene / Tumor suppressor / Protective / Risk / Biomarker / Null (with majority vote count) |
| `evidence_summary` | One-sentence experimental evidence per supporting paper |
| `validation_methods` | Experimental methods (Western blot, CRISPR, xenograft, etc.) |
| `experimental_detail` | Detailed experimental finding from each paper |
| `model_type` | cell line / animal model / clinical sample / mixed |
| `pmid` / `doi` | PubMed ID and DOI (semicolon-joined if multiple papers) |
| `n_papers` | Number of supporting papers for this target-disease association |

## Key Design Decisions

- **Complete evidence chain**: Wet-lab validation requires intervention (CRISPR/KO/siRNA/drug) + molecular detection (WB/qPCR/IHC) + functional phenotype — all explicitly stated in the abstract. Pure bioinformatics predictions are excluded.
- **37 Q1 journals** (Nature, Cell, Cancer Discovery, JCO, etc.) + extended journals for 3 rare cancer types (KIRP, KICH, UCS).
- **Majority voting**: When multiple papers report the same target for the same cancer, functional_role is resolved by majority vote with vote counts (e.g., `Oncogene (3/4)`).
- **Defensive JSON parsing**: 3-layer fallback (direct → regex extraction → strip markdown markers) to handle irregular LLM outputs.

## Notes

- `config.py` contains real API keys and is gitignored. Use `config.example.py` as a template.
- The `data/` and `output/` directories are gitignored — generated at runtime.
- NCBI Entrez API requires your email; add an API key for higher rate limits.
- DeepSeek extraction for all 33 cancers × 200 papers takes ~2-3 hours with 8 threads.
