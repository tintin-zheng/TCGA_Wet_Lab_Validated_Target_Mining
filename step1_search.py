# ============ step1_search.py ============
"""Step 1: PubMed search across all TCGA cancer types, excluding reviews/guidelines/clinical trials, fetching abstracts"""

from Bio import Entrez
import json
import time
import os
from config import (
    NCBI_EMAIL, NCBI_API_KEY, JOURNAL_ISSNS,
    TCGA_CANCERS, EXTRA_JOURNALS, SEARCH_COUNT
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
    search_count = int(os.getenv("PIPELINE_SEARCH_COUNT", str(SEARCH_COUNT)))

    cancer_items = parse_selected_cancers()
    if not cancer_items:
        raise ValueError("No cancer types selected. Check PIPELINE_CANCERS/PIPELINE_MAX_CANCERS.")

    all_results = {}
    total_papers = 0

    print(f"{'='*60}")
    print(f"  TCGA Search Started: {len(cancer_items)} cancer types")
    print(f"  Max results per cancer: {search_count} | tag: {tag or 'default'}")
    print(f"{'='*60}")

    for code, (disease_names, cn_name) in cancer_items:
        primary_en = disease_names[0]
        issns = list(dict.fromkeys(JOURNAL_ISSNS + EXTRA_JOURNALS.get(code, [])))

        output_file = f"data/papers_{code}{suffix}.json"

        # Checkpoint: skip if already done
        if os.path.exists(output_file):
            try:
                with open(output_file, "r", encoding="utf-8") as f:
                    existing = json.load(f)
                all_results[code] = existing
                n = len(existing.get("papers", []))
                total_papers += n
                print(f"\n  {code}: {primary_en} ({cn_name}) — already done ({n} papers), skipped")
                continue
            except (json.JSONDecodeError, KeyError):
                print(f"\n  {code}: checkpoint file corrupted, re-running...")

        print(f"\n{'='*60}")
        print(f"  {code}: {primary_en} ({cn_name})")
        print(f"  Aliases: {len(disease_names)} | Journals: {len(issns)}")
        print(f"{'='*60}")

        query = build_query(disease_names, issns)
        print("  Searching...")

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
