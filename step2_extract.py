# ============ step2_extract.py ============
"""Step 2: DeepSeek per-paper extraction of wet-lab validated targets"""

import json
import os
import re
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from openai import OpenAI
from tqdm import tqdm
from config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL, TCGA_CANCERS

MAX_WORKERS = int(os.getenv("EXTRACT_MAX_WORKERS", "8"))
MAX_RETRIES = int(os.getenv("EXTRACT_MAX_RETRIES", "3"))
REQUEST_GAP = float(os.getenv("EXTRACT_REQUEST_GAP", "0.0"))
SAVE_EVERY = int(os.getenv("EXTRACT_SAVE_EVERY", "20"))

_thread_local = threading.local()


def get_client():
    """Provide a thread-local client to reduce shared-object risks under concurrency."""
    if not hasattr(_thread_local, "client"):
        _thread_local.client = OpenAI(
            api_key=DEEPSEEK_API_KEY,
            base_url=DEEPSEEK_BASE_URL,
        )
    return _thread_local.client

EXTRACTION_PROMPT = """You are a biomedical literature analysis expert. Read the following paper abstract and determine whether it contains wet lab validated targets, then extract relevant information.

This paper was retrieved by a PubMed search for: {tcga_code}
If the paper's PRIMARY study subject is a DIFFERENT cancer type than {tcga_code}, set corrected_tcga_code to the correct TCGA code from the list below. If the cancer type matches {tcga_code}, set corrected_tcga_code to null.

TCGA cancer type codes:
{tcga_list}

Paper Title: {title}
Abstract: {abstract}

Strictly output the following JSON format (do not output anything else):
{
  "has_wet_lab_validation": true/false,
  "is_review": true/false,
  "insufficient_info": true/false,
  "corrected_tcga_code": "CORRECT_TCGA_CODE or null",
  "evidence_summary": "one-sentence description of experimental evidence, or null if no wet lab or insufficient info",
  "validation_methods": ["method1", "method2"],
  "disease": "disease name",
  "validated_targets": [
    {
      "target_name": "Official HGNC gene/protein symbol or pathway name",
      "target_type": "gene/protein/miRNA/lncRNA/pathway",
      "expression_change": "Upregulated/Downregulated/Unchanged/Null",
      "functional_role": "Oncogene/Tumor suppressor/Protective/Risk/Biomarker/Null",
      "experimental_detail": "one-sentence description of experimental finding",
      "model_type": "cell line / animal model / clinical sample / mixed",
      "specific_model_name": "Specific names (e.g., A549, BALB/c nude mice, patient tissues) or null"
    }
  ]
}

Rules:

1. has_wet_lab_validation=true condition:
   Judgment principle: the authors performed a deliberate experimental manipulation on a biological system
   (cells, tissues, or animals) and then measured a molecular or functional outcome. The key question is:
   "Did the authors DO something to the biology and MEASURE the result in the lab?"

   Common intervention types include genetic manipulation (knockout, knockdown, siRNA, CRISPR, overexpression),
   drug/inhibitor treatment, and animal models (xenograft, PDX, transgenic mice). Detection methods include
   Western blot, qPCR, IHC, IF, flow cytometry, and functional assays (proliferation, migration, apoptosis, etc.).
   These are illustrative only — use your judgment. Any experimental perturbation + molecular measurement counts.

   IMPORTANT: Having wet-lab techniques ≠ wet-lab target validation. Papers that only observe/measure
   (mutation scanning, expression profiling, IHC without intervention, sequencing to find mutations) are
   NOT wet-lab validation — the authors merely described what was there, not what the target DOES.
   The key differentiator is intervention: the authors must have deliberately perturbed the biology,
   not just measured it.

   Bioinformatics + wet lab mixed papers: if the paper contains any wet lab validation part, it counts as true.

2. has_wet_lab_validation=false condition:
   - Review, meta-analysis, guideline -> is_review=true
   - Pure bioinformatics prediction: network pharmacology, molecular docking, TCGA mining alone, co-expression analysis alone
   - Single-cell sequencing / spatial transcriptomics (without functional validation)
   - Pure clinical trial report: only reports drug efficacy, no molecular target validation
   - Epidemiological study: only reports incidence/survival rate, no molecular experiments
   - Pure prognostic correlation IHC: IHC staining + survival analysis only, no functional experiments (no knockout/overexpression/drug intervention) -> NOT wet lab validation
   - Insufficient information -> insufficient_info=true

   CRITICAL: When has_wet_lab_validation=false, validated_targets MUST be an empty array [].
   The paper may mention genes/proteins, but without wet-lab functional validation they are NOT valid targets.
   evidence_summary, validation_methods, and all target fields must be null/empty.

3. insufficient_info rules:
   - insufficient_info = true when:
     * Abstract is too short (less than 3 sentences) and cannot determine experiment type
     * Abstract only mentions "we validated a target" but does not specify methods
     * Abstract mentions experimental results but no experimental method names
     * Abstract structure is incomplete (e.g., only background and conclusion, methods section omitted)
   - insufficient_info = false when:
     * Abstract clearly describes experimental methods (whether wet lab or not)
     * Abstract clearly indicates this is a review / bioinformatics / clinical trial
   - When insufficient_info = true:
     * has_wet_lab_validation must be false
     * is_review must be false
     * validated_targets must be empty array []
     * Do not guess or infer, only mark as insufficient info

4. evidence_summary examples:
   - "CRISPR-mediated CDK1 knockout in NCI-H295R cells validated pro-proliferative role; xenograft model confirmed in vivo tumor suppression"
   - "Gefitinib treatment in A549 cells, Western blot confirmed EGFR downstream pathway inhibition, MTT assay validated proliferation suppression"
   - null (when no wet lab or insufficient info)

5. Target extraction rules:
   - Use standard official HGNC gene symbols for target names (e.g., ERBB2 instead of HER2, TP53 instead of p53).
   - Pathway can also be a target: target_type = "pathway", target_name = pathway name (e.g., PI3K/AKT, Wnt/beta-catenin)
   - expression_change values:
     * Upregulated: explicitly stated as highly expressed or upregulated in disease/experiment
     * Downregulated: explicitly stated as lowly expressed or downregulated
     * Unchanged: no significant change
     * Null: expression level not mentioned or cannot be determined from abstract
   - functional_role values:
     * Oncogene: promotes cancer (knockdown suppresses tumor / overexpression promotes tumor)
     * Tumor suppressor: suppresses cancer (overexpression suppresses tumor / knockdown promotes tumor)
     * Protective: protective factor (high expression associated with favorable prognosis with functional validation)
     * Risk: risk factor (mutation/polymorphism increases risk, direction unclear)
     * Biomarker: diagnostic/prognostic marker only (molecular detection present but functional role unclear)
     * Null: insufficient information to determine functional role
   - When no validated targets, return empty array []
   - Do not fabricate information, only extract what is explicitly stated in the abstract.

6. Language requirement:
   All output content must be in pure English, no Chinese mixed in.
   evidence_summary, experimental_detail, validation_methods and all other text fields must be in English.
   Gene symbols use standard English nomenclature (e.g., TP53, EGFR, miR-21).
   Pathway names in English (e.g., PI3K/AKT, Wnt/beta-catenin).

7. Defensive JSON rules:
   - Do not omit any field, must output complete JSON structure.
   - Do not fabricate information, fill missing data as follows:
     * has_wet_lab_validation: no wet lab evidence found -> false
     * is_review: cannot determine if review -> false
     * insufficient_info: cannot determine experiment type -> true
     * evidence_summary: no wet lab or insufficient info -> null
     * validation_methods: no methods mentioned -> [] (empty array)
     * disease: cannot determine disease -> null
     * validated_targets: no wet lab validation -> [] (empty array)
   - Single target field missing value rules:
     * target_name: if specific target cannot be determined, do not output that target object at all
     * target_type: cannot determine -> "unknown"
     * expression_change: cannot determine -> "Null"
     * functional_role: cannot determine -> "Null"
     * experimental_detail: cannot extract -> "Not specified in abstract"
     * model_type: cannot determine -> "unknown"
     * specific_model_name: cannot extract -> null"""

# Build TCGA cancer code reference list for disease correction in prompt
_tcga_entries = []
for _code, (_names, _cn) in sorted(TCGA_CANCERS.items()):
    _primary = _names[0] if isinstance(_names, list) else _names
    _tcga_entries.append(f"{_code}: {_primary} ({_cn})")
TCGA_LIST = "\n".join(_tcga_entries)


def safe_json_parse(text):
    """Multi-layer JSON parsing to handle irregular LLM outputs"""
    # Layer 1: direct parse
    try:
        return json.loads(text)
    except:
        pass

    # Layer 2: regex extract JSON block
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except:
            pass

    # Layer 3: strip markdown code block markers
    text_clean = text.strip().strip('```json').strip('```').strip()
    try:
        return json.loads(text_clean)
    except:
        pass

    # Parse failed, return default structure
    return {
        "has_wet_lab_validation": False,
        "is_review": False,
        "insufficient_info": True,
        "corrected_tcga_code": None,
        "evidence_summary": None,
        "validation_methods": [],
        "disease": None,
        "validated_targets": [],
        "error": "parse_failed",
    }


def extract_targets(title, abstract, tcga_code):
    """Call DeepSeek API to extract target information"""
    # Use direct placeholder replacement so JSON braces in prompt are treated literally.
    prompt = (EXTRACTION_PROMPT
              .replace("{tcga_code}", tcga_code)
              .replace("{tcga_list}", TCGA_LIST)
              .replace("{title}", title)
              .replace("{abstract}", abstract))
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            if REQUEST_GAP > 0:
                time.sleep(REQUEST_GAP)
            client = get_client()
            response = client.chat.completions.create(
                model=DEEPSEEK_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
            )
            content = response.choices[0].message.content
            return safe_json_parse(content)
        except Exception as e:
            if attempt == MAX_RETRIES:
                print(f"  API error (final): {e}")
                return None
            backoff = min(2 ** attempt, 8)
            print(f"  API error (retry {attempt}/{MAX_RETRIES}): {e}")
            time.sleep(backoff)


def process_paper(paper, tcga_code):
    """Single paper processing function for ThreadPoolExecutor concurrency."""
    result = extract_targets(paper["title"], paper["abstract"], tcga_code)
    if result is None:
        result = {
            "has_wet_lab_validation": False,
            "is_review": False,
            "insufficient_info": True,
            "corrected_tcga_code": None,
            "evidence_summary": None,
            "validation_methods": [],
            "disease": None,
            "validated_targets": [],
            "error": "api_error",
        }

    result["pmid"] = paper["pmid"]
    result["title"] = paper["title"]
    result["year"] = paper["year"]
    result["journal"] = paper["journal"]
    result["doi"] = paper.get("doi", "")
    return result


def run_extraction():
    tag = os.getenv("PIPELINE_TAG", "").strip()
    suffix = f"_{tag}" if tag else ""
    papers_cap = int(os.getenv("PIPELINE_PAPERS_PER_CANCER", "0"))
    cancers_str = os.getenv("PIPELINE_CANCERS", "").strip()

    extraction_dir = f"data/extractions{suffix}"
    os.makedirs(extraction_dir, exist_ok=True)

    papers_all_path = f"data/papers_all{suffix}.json"
    if not os.path.exists(papers_all_path):
        papers_all_path = "data/papers_all.json"

    with open(papers_all_path, "r", encoding="utf-8") as f:
        all_papers = json.load(f)

    if cancers_str:
        wanted = {c.strip().upper() for c in cancers_str.split(",") if c.strip()}
        all_papers = {k: v for k, v in all_papers.items() if k in wanted}

    if not all_papers:
        raise ValueError("No cancer types selected for extraction. Check PIPELINE_CANCERS.")

    total_papers = sum(len(v["papers"]) for v in all_papers.values())
    print(f"Total: {len(all_papers)} cancer types, {total_papers} papers to process")
    print(f"Workers: {MAX_WORKERS}, max retries: {MAX_RETRIES}")
    print(f"Estimated time (rough): ~{total_papers * 1.5 / max(MAX_WORKERS, 1) / 60:.0f} minutes")
    print()

    all_extractions = {}

    for code, disease_data in all_papers.items():
        cn_name = disease_data["disease_cn"]
        papers = disease_data["papers"]
        if papers_cap > 0:
            papers = papers[:papers_cap]

        output_file = f"{extraction_dir}/{code}.json"

        # Checkpoint / resume
        if os.path.exists(output_file):
            try:
                with open(output_file, "r", encoding="utf-8") as f:
                    existing = json.load(f)
                done_pmids = {p["pmid"] for p in existing}
                papers_todo = [p for p in papers if p["pmid"] not in done_pmids]
                results = existing
                print(f"  {code}: {len(existing)}/{len(papers)} done, {len(papers_todo)} to go")
            except (json.JSONDecodeError, KeyError):
                print(f"  {code}: checkpoint file corrupted, restarting from scratch")
                results = []
                papers_todo = papers
        else:
            results = []
            papers_todo = papers

        print(f"\n{'='*60}")
        print(f"  {code}: {cn_name} ({len(papers_todo)} papers to process)")
        print(f"{'='*60}")

        if papers_todo:
            with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                future_to_paper = {executor.submit(process_paper, p, code): p for p in papers_todo}
                futures = list(future_to_paper.keys())
                for idx, future in enumerate(tqdm(as_completed(futures), total=len(futures), desc=code), start=1):
                    try:
                        result = future.result()
                    except Exception as e:
                        paper = future_to_paper[future]
                        result = {
                            "has_wet_lab_validation": False,
                            "is_review": False,
                            "insufficient_info": True,
                            "corrected_tcga_code": None,
                            "evidence_summary": None,
                            "validation_methods": [],
                            "disease": None,
                            "validated_targets": [],
                            "error": f"worker_exception: {e}",
                            "pmid": paper.get("pmid", ""),
                            "title": paper.get("title", ""),
                            "year": paper.get("year", ""),
                            "journal": paper.get("journal", ""),
                            "doi": paper.get("doi", ""),
                        }
                    results.append(result)

                    # Batch save to avoid losing progress on long runs
                    if idx % SAVE_EVERY == 0:
                        with open(output_file, "w", encoding="utf-8") as f:
                            json.dump(results, f, ensure_ascii=False, indent=2)

        all_extractions[code] = results

        # Save per-cancer results
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        # Print stats
        n_wet = sum(1 for r in results if r.get("has_wet_lab_validation"))
        n_review = sum(1 for r in results if r.get("is_review"))
        n_insufficient = sum(1 for r in results if r.get("insufficient_info"))
        n_other = len(results) - n_wet - n_review - n_insufficient
        n_targets = sum(
            len(r.get("validated_targets", []))
            for r in results if r.get("has_wet_lab_validation")
        )
        print(f"\n  -> Wet lab: {n_wet}/{len(results)}")
        print(f"  -> Review/Bioinfo: {n_review}")
        print(f"  -> Insufficient info: {n_insufficient}")
        print(f"  -> Other (no wet lab): {n_other}")
        print(f"  -> Targets extracted: {n_targets}")

    # Save all results
    all_extractions_path = f"data/extractions_all{suffix}.json"
    with open(all_extractions_path, "w", encoding="utf-8") as f:
        json.dump(all_extractions, f, ensure_ascii=False, indent=2)

    # Overall stats
    print(f"\n{'='*60}")
    print("  All extractions complete!")
    print(f"{'='*60}")

    total_wet = 0
    total_review = 0
    total_insufficient = 0
    total_targets = 0
    for code, results in all_extractions.items():
        total_wet += sum(1 for r in results if r.get("has_wet_lab_validation"))
        total_review += sum(1 for r in results if r.get("is_review"))
        total_insufficient += sum(1 for r in results if r.get("insufficient_info"))
        total_targets += sum(
            len(r.get("validated_targets", []))
            for r in results if r.get("has_wet_lab_validation")
        )

    print(f"  Total papers: {total_papers}")
    print(f"  Wet lab validated: {total_wet}")
    print(f"  Review/Bioinfo: {total_review}")
    print(f"  Insufficient info: {total_insufficient}")
    print(f"  Total targets extracted: {total_targets}")
    print(f"  Output: {all_extractions_path}")


if __name__ == "__main__":
    run_extraction()
