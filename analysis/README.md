# Pipeline Analysis

Standalone analysis notebook for the TCGA Wet-Lab Validated Target Mining pipeline output.
**Read-only** — no project code is modified.

## Usage

```bash
cd analysis
jupyter notebook pipeline_analysis.ipynb
# Or convert to HTML report:
jupyter nbconvert --to html --execute pipeline_analysis.ipynb
```

## Dependencies

```bash
pip install pandas matplotlib seaborn jupyter
```

## Data Sources

- `../output/final_targets.csv` — final deduplicated target-disease associations
- `../data/extractions_all.json` — full LLM extraction results (for paper-level stats)

## Output

- Inline charts and statistics in the notebook
- PNG figures saved to `analysis/figures/`
