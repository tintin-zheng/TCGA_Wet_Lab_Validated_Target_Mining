# ============ step3_integrate.py ============
"""Step 3: Filter wet lab papers -> Deduplicate targets -> Output final table"""

import json
import os
import pandas as pd
from collections import Counter
from config import TARGET_COUNT, TCGA_CANCERS


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

                results_table.append({
                    "tcga_code": code,
                    "disease_en": en_name,
                    "disease_cn": cn_name,
                    "target": gene,
                    "target_type": target.get("target_type", ""),
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

    # 6. Statistics
    print(f"\n{'='*60}")
    print(f"  Final Results")
    print(f"{'='*60}")
    print(f"  Total target-disease associations: {len(deduped)}")
    print(f"  Cancer types covered: {deduped['tcga_code'].nunique()}")
    print(f"  Unique targets: {deduped['target'].nunique()}")

    print(f"\n  Per-cancer breakdown:")
    print(f"  {'Code':<8} {'Disease':<24} {'Papers':>7} {'Targets':>8}")
    print(f"  {'-'*50}")
    for code in TCGA_CANCERS:
        sub = deduped[deduped["tcga_code"] == code]
        all_pmids = set()
        for pmids_str in sub["pmid"]:
            all_pmids.update(p.strip() for p in pmids_str.split(";") if p.strip())
        n_papers = len(all_pmids) if not sub.empty else 0
        n_targets = len(sub)
        cn = TCGA_CANCERS[code][1]
        if n_targets > 0:
            print(f"  {code:<8} {cn:<24} {n_papers:>7} {n_targets:>8}")

    # 7. Cross-cancer target statistics
    cross_cancer = deduped.groupby("target")["tcga_code"].nunique().sort_values(ascending=False)
    multi_cancer = cross_cancer[cross_cancer >= 3]
    print(f"\n  Cross-cancer targets (>= 3 cancer types): {len(multi_cancer)}")
    if len(multi_cancer) > 0:
        print(f"  Top 10:")
        for gene, n in multi_cancer.head(10).items():
            print(f"    {gene:<12} {n} cancer types")

    print(f"\n  Output: {output_csv}")


if __name__ == "__main__":
    run_integration()
