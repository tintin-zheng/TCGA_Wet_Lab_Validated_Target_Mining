# ============ step3_integrate.py ============
"""Step 3: Filter wet lab papers -> Deduplicate targets -> Output final table"""

import json
import os
from datetime import datetime

import pandas as pd
from collections import Counter
from config import TARGET_COUNT, TCGA_CANCERS, DEEPSEEK_MODEL
from gene_mapper import GeneMapper


def majority_vote(values):
    """Majority vote, returns 'most_common_value (n/total)' format"""
    valid = [v for v in values if v and v != "Null"]
    if not valid:
        return "Null"
    counter = Counter(valid)
    top_val, top_count = counter.most_common(1)[0]
    return f"{top_val} ({top_count}/{len(valid)})"


def run_integration():
    tag = os.getenv("PIPELINE_TAG", "").strip()
    suffix = f"_{tag}" if tag else ""
    cancers_str = os.getenv("PIPELINE_CANCERS", "").strip()

    all_extractions_path = f"data/extractions_all{suffix}.json"
    if not os.path.exists(all_extractions_path):
        all_extractions_path = "data/extractions_all.json"

    with open(all_extractions_path, "r", encoding="utf-8") as f:
        all_extractions = json.load(f)

    if cancers_str:
        wanted = {c.strip().upper() for c in cancers_str.split(",") if c.strip()}
        all_extractions = {k: v for k, v in all_extractions.items() if k in wanted}

    if not all_extractions:
        raise ValueError("No cancer types selected for integration. Check PIPELINE_CANCERS.")

    os.makedirs("output", exist_ok=True)
    results_table = []
    per_cancer_stats = {}  # {code: {screened, wet_lab, review, insufficient, other}}

    # Gene mapping (skip with SKIP_GENE_MAPPING=true for quick runs)
    if os.getenv("SKIP_GENE_MAPPING", "").strip().lower() == "true":
        mapper = None
        print("[step3] SKIP_GENE_MAPPING=true — gene mapping disabled.")
    else:
        mapper = GeneMapper()

    for code, extractions in all_extractions.items():
        cn_name = TCGA_CANCERS[code][1]
        en_names = TCGA_CANCERS[code][0]
        en_name = en_names[0] if isinstance(en_names, list) else en_names

        print(f"\n{'='*60}")
        print(f"  {code}: {cn_name}")
        print(f"{'='*60}")

        # Four-category breakdown
        n_total = len(extractions)
        n_wet = sum(1 for r in extractions if r.get("has_wet_lab_validation"))
        n_review = sum(1 for r in extractions if r.get("is_review"))
        n_insufficient = sum(1 for r in extractions if r.get("insufficient_info"))
        n_other = n_total - n_wet - n_review - n_insufficient
        per_cancer_stats[code] = {
            "disease": cn_name,
            "screened": n_total,
            "wet_lab": n_wet,
            "review": n_review,
            "insufficient": n_insufficient,
            "other": n_other,
        }
        print(f"  Total: {n_total} | Wet lab: {n_wet} | Review/Bioinfo: {n_review} | Insufficient: {n_insufficient} | Other: {n_other}")

        # 1. Filter wet lab papers
        wet_lab_papers = [r for r in extractions if r.get("has_wet_lab_validation")]

        # 2. Cap paper count
        if len(wet_lab_papers) > TARGET_COUNT:
            wet_lab_papers = wet_lab_papers[:TARGET_COUNT]
            print(f"  Capped to top {TARGET_COUNT} papers")

        # 3. Expand to target-disease associations
        for paper in wet_lab_papers:
            methods = paper.get("validation_methods", [])
            methods_str = ", ".join(methods) if isinstance(methods, list) else str(methods)
            evidence = paper.get("evidence_summary", "") or ""

            for target in paper.get("validated_targets", []):
                gene = target.get("target_name", "").strip()
                if not gene:
                    continue
                target_type = target.get("target_type", "")

                # Standardize gene symbol via HGNC
                if mapper:
                    official, ncbi_id, ensembl_id = mapper.lookup(gene, target_type)
                else:
                    official, ncbi_id, ensembl_id = "", "", ""

                results_table.append({
                    "tcga_code": code,
                    "disease_en": en_name,
                    "disease_cn": cn_name,
                    "target": gene,
                    "target_type": target_type,
                    "official_symbol": official,
                    "ncbi_gene_id": ncbi_id,
                    "ensembl_id": ensembl_id,
                    "expression_change": target.get("expression_change", "Null"),
                    "functional_role": target.get("functional_role", "Null"),
                    "evidence_summary": evidence,
                    "validation_methods": methods_str,
                    "experimental_detail": target.get("experimental_detail", ""),
                    "model_type": target.get("model_type", ""),
                    "specific_model_name": target.get("specific_model_name", "") or "",
                    "pmid": paper.get("pmid", ""),
                    "doi": paper.get("doi", ""),
                    "year": paper.get("year", ""),
                    "journal": paper.get("journal", ""),
                    "title": paper.get("title", ""),
                })

    if not results_table:
        print("\nNo targets extracted!")
        return

    df = pd.DataFrame(results_table)

    # 4. Deduplicate & merge (same cancer + same target -> aggregate across papers)
    deduped = df.groupby(["tcga_code", "target"]).agg({
        "disease_en": "first",
        "disease_cn": "first",
        "target_type": "first",
        "official_symbol": "first",
        "ncbi_gene_id": "first",
        "ensembl_id": "first",
        "expression_change": lambda x: "; ".join(sorted(set(v for v in x if v and v != "Null"))) or "Null",
        "functional_role": lambda x: majority_vote(list(x)),
        "evidence_summary": lambda x: " | ".join(x.dropna()),
        "validation_methods": lambda x: "; ".join(set(x.dropna())),
        "experimental_detail": lambda x: " | ".join(x.dropna()),
        "model_type": lambda x: "; ".join(set(x.dropna())),
        "specific_model_name": lambda x: "; ".join(set(x.dropna())),
        "pmid": lambda x: "; ".join(x),
        "doi": lambda x: "; ".join(x),
        "year": lambda x: f"{min(y for y in x if y)}-{max(y for y in x if y)}" if any(x) else "",
        "journal": lambda x: "; ".join(set(x.dropna())),
        "title": lambda x: " | ".join(x),
    }).reset_index()

    # Paper count
    deduped["n_papers"] = deduped["pmid"].apply(lambda x: len(x.split("; ")))
    # Sort: non-Null functional_role first -> cancer type -> paper count desc
    deduped["_role_rank"] = deduped["functional_role"].apply(lambda x: 0 if x != "Null" else 1)
    deduped = deduped.sort_values(["_role_rank", "tcga_code", "n_papers"], ascending=[True, True, False])
    deduped = deduped.drop(columns=["_role_rank"])

    # Add primary key column (cancer_type_sequence)
    deduped["id"] = deduped.groupby("tcga_code").cumcount() + 1
    deduped["id"] = deduped.apply(lambda row: f"{row['tcga_code']}_{row['id']:03d}", axis=1)
    # Move id to first column
    cols = ["id"] + [c for c in deduped.columns if c != "id"]
    deduped = deduped[cols]

    # 5. Output
    output_csv = f"output/final_targets{suffix}.csv"
    deduped.to_csv(output_csv, index=False, encoding="utf-8-sig")

    # 6. Build per-cancer breakdown (all 33 cancers, including those with 0 targets)
    breakdown_rows = []
    for code in TCGA_CANCERS:
        stats = per_cancer_stats.get(code, {})
        sub = deduped[deduped["tcga_code"] == code]
        # Count unique supporting PMIDs from final deduped table
        all_pmids = set()
        for pmids_str in sub["pmid"]:
            all_pmids.update(p.strip() for p in pmids_str.split(";") if p.strip())
        n_support_papers = len(all_pmids) if not sub.empty else 0
        breakdown_rows.append({
            "code": code,
            "disease": TCGA_CANCERS[code][1],
            "screened": stats.get("screened", 0),
            "wet_lab": stats.get("wet_lab", 0),
            "wet_rate": f"{stats.get('wet_lab', 0) / max(stats.get('screened', 1), 1) * 100:.1f}%",
            "review": stats.get("review", 0),
            "insufficient": stats.get("insufficient", 0),
            "other": stats.get("other", 0),
            "final_targets": len(sub),
            "support_papers": n_support_papers,
        })

    # 7. Cross-cancer target statistics
    cross_cancer = deduped.groupby("target")["tcga_code"].nunique().sort_values(ascending=False)
    multi_cancer = cross_cancer[cross_cancer >= 3]

    # 8. Terminal output
    print(f"\n{'='*60}")
    print(f"  Final Results")
    print(f"{'='*60}")
    print(f"  Total target-disease associations: {len(deduped)}")
    print(f"  Cancer types covered: {deduped['tcga_code'].nunique()}")
    print(f"  Unique targets: {deduped['target'].nunique()}")
    if mapper:
        stats = mapper.get_stats()
        print(f"  Gene standardization: {stats['hits']}/{stats['total']} mapped ({stats['rate']:.1f}%)")
    print(f"\n  Per-cancer breakdown:")
    print(f"  {'Code':<8} {'Disease':<24} {'Screened':>8} {'Wet':>5} {'Rate':>7} {'Targets':>8} {'Supp.Papers':>12}")
    print(f"  {'-'*78}")
    for row in breakdown_rows:
        if row["wet_lab"] > 0:
            print(f"  {row['code']:<8} {row['disease']:<24} {row['screened']:>8} {row['wet_lab']:>5} {row['wet_rate']:>7} {row['final_targets']:>8} {row['support_papers']:>12}")

    print(f"\n  Cross-cancer targets (>= 3 cancer types): {len(multi_cancer)}")
    if len(multi_cancer) > 0:
        print(f"  Top 10:")
        for gene, n in multi_cancer.head(10).items():
            print(f"    {gene:<12} {n} cancer types")

    print(f"\n  Output: {output_csv}")

    # 9. Write summary markdown
    write_summary_markdown(
        suffix=suffix,
        deduped=deduped,
        breakdown_rows=breakdown_rows,
        multi_cancer=multi_cancer,
        mapper=mapper,
    )


def write_summary_markdown(suffix, deduped, breakdown_rows, multi_cancer, mapper=None):
    """Generate a human-readable pipeline summary in Markdown."""
    summary_path = f"output/pipeline_summary{suffix}.md"
    tag = suffix.lstrip("_") if suffix else "default"
    total_wet = sum(r["wet_lab"] for r in breakdown_rows)
    total_screened = sum(r["screened"] for r in breakdown_rows)
    total_review = sum(r["review"] for r in breakdown_rows)
    total_insufficient = sum(r["insufficient"] for r in breakdown_rows)
    total_other = sum(r["other"] for r in breakdown_rows)

    lines = []
    lines.append("# TCGA Wet-Lab Validated Target Mining — Pipeline Summary")
    lines.append("")
    lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}  ")
    lines.append(f"**Model:** {DEEPSEEK_MODEL}  ")
    lines.append(f"**Run tag:** `{tag}`  ")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Overview")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("|--------|-------|")
    lines.append(f"| Cancer types | {len(TCGA_CANCERS)} |")
    lines.append(f"| Papers screened | {total_screened:,} |")
    lines.append(f"| Wet-lab validated | {total_wet:,} ({total_wet/max(total_screened,1)*100:.1f}%) |")
    lines.append(f"| Review / bioinformatics | {total_review:,} |")
    lines.append(f"| Insufficient info | {total_insufficient:,} |")
    lines.append(f"| Other (no wet lab) | {total_other:,} |")
    lines.append(f"| Final target-disease associations | {len(deduped):,} |")
    lines.append(f"| Unique targets | {deduped['target'].nunique():,} |")
    lines.append(f"| Cross-cancer targets (≥3 cancers) | {len(multi_cancer):,} |")
    if mapper:
        stats = mapper.get_stats()
        lines.append(f"| Gene targets standardized | {stats['hits']:,} ({stats['rate']:.1f}%) |")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Per-Cancer Breakdown")
    lines.append("")
    lines.append("| Code | Disease | Screened | Wet Lab | Rate | Review | Insuff. | Other | Final Targets | Supp. Papers |")
    lines.append("|------|---------|----------|---------|------|--------|---------|-------|---------------|--------------|")
    for row in breakdown_rows:
        lines.append(
            f"| {row['code']} | {row['disease']} | {row['screened']} | {row['wet_lab']} | "
            f"{row['wet_rate']} | {row['review']} | {row['insufficient']} | {row['other']} | "
            f"{row['final_targets']} | {row['support_papers']} |"
        )
    lines.append("")
    lines.append("*Screened = total papers processed by LLM; Wet Lab = papers with wet-lab validation; Final Targets = unique target-disease pairs after dedup; Supp. Papers = unique PMIDs supporting final targets.*")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Cross-Cancer Targets (≥3 cancer types)")
    lines.append("")
    if len(multi_cancer) > 0:
        lines.append(f"{len(multi_cancer)} targets appear in 3 or more cancer types.")
        lines.append("")
        lines.append("| # | Target | Cancer Types |")
        lines.append("|---|--------|-------------|")
        for rank, (gene, count) in enumerate(multi_cancer.head(20).items(), 1):
            cancers = ", ".join(sorted(deduped[deduped["target"] == gene]["tcga_code"].unique()))
            lines.append(f"| {rank} | {gene} | {count} ({cancers}) |")
    else:
        lines.append("No cross-cancer targets found (≥3 cancer types threshold).")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Configuration")
    lines.append("")
    lines.append(f"- **Model:** {DEEPSEEK_MODEL}")
    lines.append(f"- **Targets per cancer cap:** {TARGET_COUNT}")
    lines.append(f"- **Output CSV:** `output/final_targets{suffix}.csv`")
    lines.append(f"- **Extraction source:** `data/extractions_all{suffix}.json`")
    lines.append("")

    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"  Summary: {summary_path}")


if __name__ == "__main__":
    run_integration()
