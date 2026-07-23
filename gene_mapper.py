# ============ gene_mapper.py ============
"""Gene symbol standardization via HGNC complete set.

On first use, downloads the HGNC complete set JSON (~30 MB) from Google
Cloud Storage and caches it to data/hgnc_complete_set.json. Builds in-memory
lookup dicts mapping colloquial gene names → official_symbol / ncbi_gene_id /
ensembl_id.

Set SKIP_GENE_MAPPING=true to skip mapping entirely (useful for quick test runs).
"""

import json
import os
import time
import urllib.request
import sys

HGNC_URL = "https://storage.googleapis.com/public-download-files/hgnc/json/json/hgnc_complete_set.json"
HGNC_CACHE = "data/hgnc_complete_set.json"

# Target types that are mappable to NCBI Gene IDs
MAPPABLE_TYPES = {"gene", "gene/protein", "protein"}


class GeneMapper:
    """Lazy-loading gene symbol → official/NCBI/Ensembl mapper."""

    def __init__(self):
        self._loaded = False
        self._symbols = {}   # UPPERCASE_SYMBOL → {official_symbol, ncbi_gene_id, ensembl_id}
        self._aliases = {}   # UPPERCASE_ALIAS  → official_symbol
        self._prev = {}      # UPPERCASE_PREV   → official_symbol
        self._hits = 0       # gene targets successfully mapped
        self._misses = 0     # gene targets not found in HGNC
        self._skipped = {}   # non-gene targets skipped by type (e.g. {"miRNA": 9, "pathway": 8})

    def _ensure_loaded(self):
        if self._loaded:
            return
        self._loaded = True
        self._load_hgnc()

    def _load_hgnc(self):
        if not os.path.exists(HGNC_CACHE):
            self._download_hgnc()

        if not os.path.exists(HGNC_CACHE):
            print("[gene_mapper] HGNC cache not available — gene mapping disabled.")
            return

        print("[gene_mapper] Loading HGNC complete set...", end=" ", flush=True)
        try:
            with open(HGNC_CACHE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            print(f"error: {e} — gene mapping disabled.")
            return

        docs = data.get("response", {}).get("docs", [])
        if not docs:
            print("empty — gene mapping disabled.")
            return

        n_genes = 0
        n_aliases = 0
        n_prev = 0
        for entry in docs:
            symbol = (entry.get("symbol") or "").strip()
            if not symbol:
                continue

            info = {
                "official_symbol": symbol,
                "ncbi_gene_id": entry.get("entrez_id", "") or "",
                "ensembl_id": entry.get("ensembl_gene_id", "") or "",
            }
            n_genes += 1
            self._symbols[symbol.upper()] = info

            # Map alias symbols → official
            aliases = entry.get("alias_symbol") or []
            if isinstance(aliases, list):
                for a in aliases:
                    a = a.strip()
                    if a and a.upper() not in self._aliases:
                        self._aliases[a.upper()] = symbol
                        n_aliases += 1

            # Map previous symbols → official (NB: some entries have "N/A" string)
            prev_raw = entry.get("prev_symbol") or []
            if isinstance(prev_raw, list):
                for prev in prev_raw:
                    prev = prev.strip()
                    if prev and prev.upper() not in self._prev:
                        self._prev[prev.upper()] = symbol
                        n_prev += 1

        print(f"{n_genes} genes, {n_aliases} aliases, {n_prev} prev symbols loaded.")

    def _download_hgnc(self):
        os.makedirs("data", exist_ok=True)
        tmp_path = HGNC_CACHE + ".tmp"
        print(f"[gene_mapper] Downloading HGNC complete set (~30 MB)...")
        print(f"  {HGNC_URL}")

        for attempt in range(1, 4):
            try:
                # Remove partial files from previous attempts
                for p in (HGNC_CACHE, tmp_path):
                    if os.path.exists(p):
                        os.remove(p)

                req = urllib.request.Request(HGNC_URL)
                with urllib.request.urlopen(req, timeout=60) as resp:
                    total = int(resp.headers.get("Content-Length", 0))
                    downloaded = 0
                    with open(tmp_path, "wb") as f:
                        while True:
                            chunk = resp.read(1024 * 1024)  # 1 MB chunks
                            if not chunk:
                                break
                            f.write(chunk)
                            downloaded += len(chunk)
                            if total:
                                pct = downloaded / total * 100
                                print(f"\r  Downloading... {downloaded / (1024*1024):.1f} / {total / (1024*1024):.1f} MB ({pct:.0f}%)", end="", flush=True)

                # Verify and rename
                if total > 0 and downloaded < total:
                    raise IOError(f"incomplete download: {downloaded}/{total} bytes")

                os.rename(tmp_path, HGNC_CACHE)
                print(f"\n  Downloaded {downloaded / (1024*1024):.1f} MB → {HGNC_CACHE}")
                return

            except Exception as e:
                print(f"\n  Attempt {attempt}/3 failed: {e}")
                for p in (HGNC_CACHE, tmp_path):
                    if os.path.exists(p):
                        os.remove(p)
                if attempt < 3:
                    wait = 2 ** attempt
                    print(f"  Retrying in {wait}s...")
                    time.sleep(wait)

        print("  All download attempts failed — gene mapping disabled.")

    def lookup(self, target_name, target_type):
        """Return (official_symbol, ncbi_gene_id, ensembl_id) tuple.

        Only maps gene/protein type targets. Returns empty strings for
        pathways, miRNAs, lncRNAs, and other non-gene targets.
        """
        if not target_name:
            return "", "", ""

        # Only attempt mapping for gene-like targets
        if target_type and target_type.lower() not in MAPPABLE_TYPES:
            t = target_type.lower()
            self._skipped[t] = self._skipped.get(t, 0) + 1
            return "", "", ""

        self._ensure_loaded()
        if not self._symbols:
            self._misses += 1
            return target_name, "", ""

        # Handle multi-gene names (slash-separated or fusions)
        gene = target_name.strip()
        separators = self._detect_separator(gene)
        if separators:
            components = self._split_gene(gene)
            mapped = [self._resolve_one(c) for c in components]
            official = ";".join(m[0] for m in mapped)
            ncbi = ";".join(m[1] for m in mapped if m[1])
            ensembl = ";".join(m[2] for m in mapped if m[2])
            return official, ncbi, ensembl

        return self._resolve_one(gene)

    def _resolve_one(self, name):
        """Map a single gene name to (official_symbol, ncbi_gene_id, ensembl_id)."""
        key = name.strip().upper()
        if not key:
            self._misses += 1
            return name, "", ""

        # 1. Exact symbol match
        if key in self._symbols:
            self._hits += 1
            info = self._symbols[key]
            return info["official_symbol"], info["ncbi_gene_id"], info["ensembl_id"]

        # 2. Alias match
        if key in self._aliases:
            self._hits += 1
            official = self._aliases[key]
            info = self._symbols.get(official.upper())
            if info:
                return info["official_symbol"], info["ncbi_gene_id"], info["ensembl_id"]

        # 3. Previous symbol match
        if key in self._prev:
            self._hits += 1
            official = self._prev[key]
            info = self._symbols.get(official.upper())
            if info:
                return info["official_symbol"], info["ncbi_gene_id"], info["ensembl_id"]

        # 4. Not found — keep original name, leave IDs empty
        self._misses += 1
        return name, "", ""

    def get_stats(self):
        """Return detailed mapping statistics.

        - hits: gene targets successfully mapped to HGNC
        - misses: gene targets NOT found in HGNC (potential issues)
        - gene_total: hits + misses (gene-like targets only)
        - skipped: non-gene targets by type (expected — they have no gene IDs)
        - rate: hit rate for gene-like targets only (excludes skipped)
        """
        gene_total = self._hits + self._misses
        return {
            "hits": self._hits,
            "misses": self._misses,
            "gene_total": gene_total,
            "skipped": dict(self._skipped),
            "skipped_total": sum(self._skipped.values()),
            "rate": self._hits / max(gene_total, 1) * 100,
        }

    @staticmethod
    def _detect_separator(name):
        """Return True if the name looks like a multi-gene string."""
        # Fusion genes: EWSR1::FLI1, CD74-NRG1 fusion, BCR-ABL
        # Slashed: CDK4/6, ERK1/2, AKT1/AKT2
        return "/" in name or "::" in name or "-fusion" in name.lower()

    @staticmethod
    def _split_gene(name):
        """Split a multi-gene name into individual gene symbols."""
        import re
        name_lower = name.lower()
        if "-fusion" in name_lower:
            # CD74-NRG1 fusion → extract gene parts
            name_lower = name_lower.replace(" fusion", "")
            parts = re.split(r"\s*-\s*", name_lower)
            return [p.strip() for p in parts if p.strip() and p.strip() != "fusion"]
        if "::" in name:
            return [p.strip() for p in name.split("::")]
        if "/" in name:
            return [p.strip() for p in name.split("/")]
        return [name]
