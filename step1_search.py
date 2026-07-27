# ============ step1_search.py ============
"""Step 1: PubMed search across all TCGA cancer types, excluding reviews/guidelines/clinical trials, fetching abstracts"""

from Bio import Entrez
import json
import time
import os
from config import (
    NCBI_EMAIL, NCBI_API_KEY, JOURNAL_ISSNS,
    TCGA_CANCERS, EXTRA_JOURNALS, SEARCH_COUNT,
    SEARCH_COUNT_OVERRIDES
)

Entrez.email = NCBI_EMAIL
if NCBI_API_KEY:
    Entrez.api_key = NCBI_API_KEY


def parse_selected_cancers():
    """Select cancer types via env vars; return all if not set."""
    codes_str = os.getenv("PIPELINE_CANCERS", "").strip()
    max_cancers = int(os.getenv("PIPELINE_MAX_CANCERS", "0"))

    items = list(TCGA_CANCERS.items())
    if codes_str:
        wanted = [c.strip().upper() for c in codes_str.split(",") if c.strip()]
        items = [(k, v) for k, v in items if k in wanted]

    if max_cancers > 0:
        items = items[:max_cancers]

    return items


def build_query(disease_names, journal_issns):
    """Build PubMed query with disease aliases support"""
    journal_filter = " OR ".join([f'"{issn}"[ISSN]' for issn in journal_issns])

    disease_filter = " OR ".join(
        [f'"{name}"[Title/Abstract]' for name in disease_names]
    )
    mesh_term = disease_names[0]

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
        f'("{mesh_term}"[MeSH Terms] OR {disease_filter}) '
        f'AND ({journal_filter}) '
        f'AND {keyword_filter} '
        f'{exclude_filter}'
    )
    return query


def search_pmids(query, max_results=200):
    """Search PubMed and return PMID list"""
    handle = Entrez.esearch(
        db="pubmed", term=query,
        retmax=max_results, sort="relevance"
    )
    results = Entrez.read(handle)
    handle.close()
    return results["IdList"]


def search_pmids_with_split(query, target_count, pubmed_total):
    """Search PubMed with year-range splitting when total > 9,999.

    NCBI esearch caps at 9,999 PMIDs regardless of retmax.
    When the available pool exceeds 9,999, this function splits
    the query by date ranges to retrieve all PMIDs.
    """
    if pubmed_total <= 9999:
        return search_pmids(query, max_results=target_count)

    # Need date-range splitting
    n_chunks = max(2, int(pubmed_total / 8000) + 1)  # 8000 per chunk for safety margin
    current_year = 2026
    start_year = 1950
    span = current_year - start_year
    chunk_span = max(1, span // n_chunks)

    all_pmids = []
    seen = set()
    print(f"  PubMed total {pubmed_total:,} > 9,999 — splitting into {n_chunks} year-range chunks")

    for i in range(n_chunks):
        y_start = start_year + i * chunk_span
        y_end = min(current_year, y_start + chunk_span - 1) if i < n_chunks - 1 else current_year
        date_filter = f'{y_start}/01/01:{y_end}/12/31[PDAT]'
        chunk_query = f'({query}) AND ("{date_filter}")'

        handle = Entrez.esearch(
            db="pubmed", term=chunk_query,
            retmax=9999, sort="relevance"
        )
        results = Entrez.read(handle)
        handle.close()
        chunk_pmids = results["IdList"]
        chunk_total = int(results.get("Count", 0))

        new_count = sum(1 for pid in chunk_pmids if pid not in seen)
        all_pmids.extend([pid for pid in chunk_pmids if pid not in seen])
        seen.update(chunk_pmids)
        time.sleep(0.4)  # respect NCBI rate limit

        # If a chunk returned 9,999 and the count also says 9,999+, split it further
        if len(chunk_pmids) >= 9999 and chunk_total > len(chunk_pmids):
            # Recursively split this chunk with finer year granularity
            sub_span = max(3, chunk_span // 2)
            for sub_start in range(y_start, y_end + 1, sub_span):
                sub_end = min(y_end, sub_start + sub_span - 1)
                sub_date = f'{sub_start}/01/01:{sub_end}/12/31[PDAT]'
                sub_query = f'({query}) AND ("{sub_date}")'
                handle2 = Entrez.esearch(
                    db="pubmed", term=sub_query,
                    retmax=9999, sort="relevance"
                )
                sub_results = Entrez.read(handle2)
                handle2.close()
                sub_pmids = sub_results["IdList"]
                all_pmids.extend([pid for pid in sub_pmids if pid not in seen])
                seen.update(sub_pmids)
                time.sleep(0.3)

    # Trim to target_count (preserving relevance order across chunks)
    if len(all_pmids) > target_count:
        all_pmids = all_pmids[:target_count]

    return all_pmids


def fetch_abstracts(pmids, max_retries=3):
    """Batch fetch paper abstracts and metadata with retry on network errors"""
    if not pmids:
        return []

    for attempt in range(1, max_retries + 1):
        try:
            handle = Entrez.efetch(
                db="pubmed", id=",".join(pmids),
                rettype="abstract", retmode="xml"
            )
            records = Entrez.read(handle)
            handle.close()

            papers = []
            for article in records.get("PubmedArticle", []):
                try:
                    medline = article["MedlineCitation"]
                    art = medline["Article"]

                    title = str(art.get("ArticleTitle", ""))

                    abstract_parts = art.get("Abstract", {}).get("AbstractText", [])
                    if isinstance(abstract_parts, list):
                        abstract = " ".join(str(p) for p in abstract_parts)
                    else:
                        abstract = str(abstract_parts)

                    pmid = str(medline.get("PMID", ""))

                    year = ""
                    try:
                        pub_date = art["Journal"]["JournalIssue"]["PubDate"]
                        year = str(pub_date.get("Year", pub_date.get("MedlineDate", "")))
                    except:
                        pass

                    journal = ""
                    try:
                        journal = str(art["Journal"]["Title"])
                    except:
                        pass

                    doi = ""
                    try:
                        for eloc in art.get("ELocationID", []):
                            if str(eloc.attributes.get("EIdType")) == "doi":
                                doi = str(eloc)
                                break
                    except:
                        pass

                    papers.append({
                        "pmid": pmid,
                        "title": title,
                        "abstract": abstract,
                        "year": year,
                        "journal": journal,
                        "doi": doi,
                    })
                except:
                    continue
            return papers

        except Exception as e:
            if attempt == max_retries:
                print(f"  NCBI fetch error (final attempt {attempt}/{max_retries}): {e}")
                return []
            backoff = min(2 ** attempt, 16)
            print(f"  NCBI fetch error (attempt {attempt}/{max_retries}), retrying in {backoff}s: {e}")
            time.sleep(backoff)


def run_search():
    os.makedirs("data", exist_ok=True)
    tag = os.getenv("PIPELINE_TAG", "").strip()
    suffix = f"_{tag}" if tag else ""
    env_search_count = os.getenv("PIPELINE_SEARCH_COUNT", "").strip()

    cancer_items = parse_selected_cancers()
    if not cancer_items:
        raise ValueError("No cancer types selected. Check PIPELINE_CANCERS/PIPELINE_MAX_CANCERS.")

    all_results = {}
    total_papers = 0

    print(f"{'='*60}")
    print(f"  TCGA Search Started: {len(cancer_items)} cancer types")
    print(f"  Max results per cancer: {SEARCH_COUNT} (default, see SEARCH_COUNT_OVERRIDES) | tag: {tag or 'default'}")
    print(f"{'='*60}")

    for code, (disease_names, cn_name) in cancer_items:
        primary_en = disease_names[0]
        issns = list(dict.fromkeys(JOURNAL_ISSNS + EXTRA_JOURNALS.get(code, [])))

        # Resolve per-cancer search count
        if env_search_count:
            search_count = int(env_search_count)
        else:
            search_count = SEARCH_COUNT_OVERRIDES.get(code, SEARCH_COUNT)

        output_file = f"data/papers_{code}{suffix}.json"

        # Checkpoint: skip only if we already have enough papers
        if os.path.exists(output_file):
            try:
                with open(output_file, "r", encoding="utf-8") as f:
                    existing = json.load(f)
                n_existing = len(existing.get("papers", []))
                if n_existing >= search_count:
                    all_results[code] = existing
                    total_papers += n_existing
                    print(f"\n  {code}: {primary_en} ({cn_name}) — already done ({n_existing} ≥ {search_count}), skipped")
                    continue
                else:
                    # Quick count check: is n_existing already at PubMed ceiling?
                    query_check = build_query(disease_names, issns)
                    count_handle = Entrez.esearch(db="pubmed", term=query_check, retmax=0)
                    count_result = Entrez.read(count_handle)
                    count_handle.close()
                    actual_count = int(count_result.get("Count", 0))
                    if n_existing >= actual_count * 0.98:
                        all_results[code] = existing
                        total_papers += n_existing
                        print(f"\n  {code}: {primary_en} ({cn_name}) — at PubMed ceiling ({n_existing} ≈ {actual_count} available), skipped")
                        continue
                    else:
                        print(f"\n  {code}: {primary_en} ({cn_name}) — updating ({n_existing} → {search_count}, {actual_count:,} available)")
            except (json.JSONDecodeError, KeyError):
                print(f"\n  {code}: checkpoint file corrupted, re-running...")

        print(f"\n{'='*60}")
        print(f"  {code}: {primary_en} ({cn_name})")
        print(f"  Aliases: {len(disease_names)} | Journals: {len(issns)} | Target: {search_count} papers")
        print(f"{'='*60}")

        query = build_query(disease_names, issns)
        print("  Searching...")

        # Quick count to determine if we need year-range splitting (>9,999 limit)
        count_handle = Entrez.esearch(db="pubmed", term=query, retmax=0)
        count_result = Entrez.read(count_handle)
        count_handle.close()
        pubmed_total = int(count_result.get("Count", 0))

        if pubmed_total > 9999:
            pmids = search_pmids_with_split(query, search_count, pubmed_total)
        else:
            pmids = search_pmids(query, max_results=search_count)
        print(f"  PMIDs found: {len(pmids)}")

        papers_all = []
        batch_size = 50
        for i in range(0, len(pmids), batch_size):
            batch = pmids[i:i + batch_size]
            papers = fetch_abstracts(batch)
            papers_all.extend(papers)
            print(f"  Fetched abstracts: {i + len(batch)}/{len(pmids)}")
            time.sleep(0.5)

        papers_with_abstract = [p for p in papers_all if p["abstract"].strip()]
        print(f"  With abstract: {len(papers_with_abstract)}/{len(papers_all)}")

        result = {
            "code": code,
            "disease_en": primary_en,
            "disease_aliases": disease_names,
            "disease_cn": cn_name,
            "papers": papers_with_abstract,
        }
        all_results[code] = result
        total_papers += len(papers_with_abstract)

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

    all_papers_path = f"data/papers_all{suffix}.json"
    with open(all_papers_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)

    print(f"\n{'='*60}")
    print("  Search Complete")
    print(f"{'='*60}")
    print(f"  Cancer types: {len(all_results)}")
    print(f"  Total papers (with abstract): {total_papers}")
    print(f"  Output: {all_papers_path}")


if __name__ == "__main__":
    run_search()
