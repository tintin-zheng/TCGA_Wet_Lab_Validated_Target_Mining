# ============ step0_count.py ============
"""Pre-experiment: count how many papers match each cancer type in PubMed"""

from Bio import Entrez
import time
from config import NCBI_EMAIL, NCBI_API_KEY, JOURNAL_ISSNS, TCGA_CANCERS, EXTRA_JOURNALS

Entrez.email = NCBI_EMAIL
if NCBI_API_KEY:
    Entrez.api_key = NCBI_API_KEY


def build_query(disease_names, extra_issns=None):
    """Build PubMed query, optionally appending extended journals"""
    all_issns = JOURNAL_ISSNS.copy()
    if extra_issns:
        all_issns.extend(extra_issns)
    journal_filter = " OR ".join([f'"{issn}"[ISSN]' for issn in all_issns])

    disease_parts = []
    for name in disease_names:
        disease_parts.append(f'("{name}"[MeSH Terms] OR "{name}"[Title/Abstract])')
    disease_filter = " OR ".join(disease_parts)

    keyword_filter = (
        '(target[Title/Abstract] OR biomarker[Title/Abstract] '
        'OR gene[Title/Abstract] OR pathway[Title/Abstract] '
        'OR mechanism[Title/Abstract] OR molecular[Title/Abstract])'
    )

    exclude_filter = (
        'NOT (Review[Publication Type] OR Meta-Analysis[Publication Type] '
        'OR Guideline[Publication Type] OR Editorial[Publication Type] '
        'OR Letter[Publication Type] OR Comment[Publication Type] '
        'OR Case Reports[Publication Type])'
    )

    query = (
        f'({disease_filter}) '
        f'AND ({journal_filter}) '
        f'AND {keyword_filter} '
        f'{exclude_filter}'
    )
    return query


def count_results(query):
    handle = Entrez.esearch(db="pubmed", term=query, retmax=0)
    results = Entrez.read(handle)
    handle.close()
    return int(results["Count"])


def run_count():
    print("=" * 75)
    print(f"{'Cancer':<8} {'Disease Name':<24} {'Journals':>8} {'Ext':>4} {'Papers':>8}")
    print("=" * 75)

    all_counts = {}
    total = 0

    for code, (disease_names, cn_name) in TCGA_CANCERS.items():
        extra = EXTRA_JOURNALS.get(code)
        query = build_query(disease_names, extra_issns=extra)
        count = count_results(query)
        all_counts[code] = count
        total += count
        n_journals = len(JOURNAL_ISSNS) + (len(extra) if extra else 0)
        extra_tag = f"+{len(extra)}" if extra else ""
        print(f"{code:<8} {cn_name:<24} {n_journals:>8} {extra_tag:>4} {count:>8}")
        time.sleep(0.5)

    print("=" * 75)
    print(f"{'Total':<8} {'':<24} {'':>8} {'':>4} {total:>8}")
    print("=" * 75)

    # Distribution
    print(f"\nDistribution:")
    print(f"  < 100 papers:     {sum(1 for v in all_counts.values() if v < 100)} cancer types")
    print(f"  100-300 papers:   {sum(1 for v in all_counts.values() if 100 <= v < 300)} cancer types")
    print(f"  300-1000 papers:  {sum(1 for v in all_counts.values() if 300 <= v < 1000)} cancer types")
    print(f"  > 1000 papers:    {sum(1 for v in all_counts.values() if v >= 1000)} cancer types")

    # Cost estimate
    capped_total = sum(min(v, 200) for v in all_counts.values())
    print(f"\nCost estimate (max 200 papers per cancer):")
    print(f"  Capped total: {capped_total} papers")
    print(f"  Estimated time: ~{capped_total * 1.5 / 60:.0f} min")
    print(f"  Estimated cost: ~¥{capped_total * 0.005:.0f}")

    # Comparison: extended journal effect
    print(f"\nExtended journal effect:")
    for code in EXTRA_JOURNALS:
        cn = TCGA_CANCERS[code][1]
        # Re-run count without extended journals
        query_base = build_query(TCGA_CANCERS[code][0])
        base_count = count_results(query_base)
        print(f"  {code} ({cn}): {base_count} -> {all_counts[code]} (+{all_counts[code]-base_count})")
        time.sleep(0.5)

    return all_counts


if __name__ == "__main__":
    run_count()
