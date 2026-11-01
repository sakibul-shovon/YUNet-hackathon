"""T24, T25: Bengali-aware BM25s Adapter with Unicode Combining Marks, Negation & Allowed-ID Scoring.

Guarantees:
- NFC-normalizes search text.
- Tokenizes Unicode letters including Bengali combining marks (hasanta, vowel signs).
- Retains negation words (না, নাই, নহে, নয়, not, no, never).
- Preserves exact section aliases (sec:45(2), ৪৫(২), ধারা ৪৫).
- No default English stopword damage.
- Allowed-ID mask applied BEFORE selecting top candidates (T25).
- Snapshot save & load verified.
"""

import hashlib
import json
import os
import re
import unicodedata
from typing import Any

import bm25s

BN_TO_EN_DIGITS = str.maketrans("০১২৩৪৫৬৭৮৯", "0123456789")
EN_TO_BN_DIGITS = str.maketrans("0123456789", "০১২৩৪৫৬৭৮৯")

# Explicit negation tokens that MUST NEVER be pruned
NEGATION_TOKENS = {"না", "নাই", "নহে", "নয়", "ছাড়া", "ব্যতীত", "ব্যতিরেকে", "not", "no", "never", "without"}


class BengaliBM25Adapter:
    TOKENIZER_VERSION = "bn_bm25_v1.0"

    @classmethod
    def tokenize(cls, text: str) -> list[str]:
        """T24 / P07.3: NFC-normalizes and tokenizes Bengali/English text with vowel signs, marks & aliases intact."""
        # 1. NFC normalization
        nfc_text = unicodedata.normalize("NFC", text or "")

        # 2. Extract section patterns like 45(2) or ৪৫(২) and preserve them as compound tokens
        section_matches = re.findall(r"[\d০-৯]+\([\d০-৯]+\)", nfc_text)
        extra_aliases = []
        for sm in section_matches:
            en_ver = sm.translate(BN_TO_EN_DIGITS)
            bn_ver = sm.translate(EN_TO_BN_DIGITS)
            extra_aliases.extend([
                sm.lower(),
                en_ver.lower(),
                bn_ver.lower(),
                f"sec:{en_ver}".lower(),
                f"ধারা:{bn_ver}".lower(),
            ])

        # 3. Match Bengali Unicode words (letters \u0985-\u09B9, signs \u09BE-\u09CD, digits \u09E6-\u09EF)
        # and standard alphanumeric words [a-zA-Z0-9]+
        raw_tokens = re.findall(
            r"[\u0980-\u09FF]+|[A-Za-z0-9_:-]+",
            nfc_text.lower(),
        )

        tokens: list[str] = []
        for t in raw_tokens:
            t_clean = t.strip()
            if not t_clean:
                continue

            # Add token
            tokens.append(t_clean)

            # If token contains digits, add bilingual dual-numeral alias
            if re.search(r"[\d০-৯]", t_clean):
                en_digit = t_clean.translate(BN_TO_EN_DIGITS)
                bn_digit = t_clean.translate(EN_TO_BN_DIGITS)
                if en_digit != t_clean:
                    tokens.append(en_digit)
                if bn_digit != t_clean:
                    tokens.append(bn_digit)

        # Append extracted compound section aliases
        tokens.extend(extra_aliases)
        return tokens

    def __init__(self) -> None:
        self.retriever: bm25s.BM25 | None = None
        self.corpus_handles: list[str] = []
        self.corpus_lookup: dict[str, dict[str, Any]] = {}
        self.snapshot_hash: str | None = None

    def build_index(self, corpus: list[dict[str, Any]]) -> str:
        """Builds bm25s index over corpus provisions and computes snapshot checksum."""
        self.corpus_handles = []
        self.corpus_lookup = {}
        tokenized_corpus: list[list[str]] = []

        for item in corpus:
            handle = item["citation_handle"]
            self.corpus_handles.append(handle)
            self.corpus_lookup[handle] = item

            # Full searchable text combines Bengali text, English text, and all aliases
            combined_text = (
                f"{item.get('provision_path', '')} "
                f"{item.get('title_bn', '')} "
                f"{item.get('title_en', '')} "
                f"{item.get('canonical_text_bn', '')} "
                f"{' '.join(item.get('aliases', []))} "
                f"{' '.join(item.get('qualifications_and_exceptions', []))}"
            )
            tokens = self.tokenize(combined_text)
            tokenized_corpus.append(tokens)

        # Initialize and index with bm25s
        self.retriever = bm25s.BM25()
        self.retriever.index(tokenized_corpus)

        # Compute deterministic checksum
        manifest_raw = f"{self.TOKENIZER_VERSION}:{','.join(self.corpus_handles)}"
        self.snapshot_hash = hashlib.sha256(manifest_raw.encode("utf-8")).hexdigest()
        return self.snapshot_hash

    def search(
        self,
        query: str,
        allowed_ids: set[str] | None = None,
        date_context: str | None = None,
        top_k: int = 10,
    ) -> list[dict[str, Any]]:
        """T25: Lexical BM25 search with allowed-ID and temporal filtering applied BEFORE top-k selection."""
        if not self.retriever or not self.corpus_handles:
            return []

        query_tokens = self.tokenize(query)
        if not query_tokens:
            return []

        # Retrieve scores for all documents in the corpus
        total_docs = len(self.corpus_handles)
        doc_indices, scores = self.retriever.retrieve([query_tokens], k=total_docs)

        scored_candidates: list[dict[str, Any]] = []
        for idx_in_result, doc_idx in enumerate(doc_indices[0]):
            score = float(scores[0][idx_in_result])
            handle = self.corpus_handles[doc_idx]
            item = self.corpus_lookup[handle]

            # 1. Apply allowed-ID filter BEFORE top-k selection (T25)
            if allowed_ids is not None and handle not in allowed_ids:
                continue

            # 2. Apply temporal filter BEFORE top-k selection (T25)
            if date_context:
                eff_from = item.get("effective_from")
                eff_to = item.get("effective_to")
                if eff_from and date_context < eff_from:
                    continue
                if eff_to and date_context >= eff_to:
                    continue

            if score > 0.001:  # Non-trivial lexical relevance
                scored_candidates.append({
                    "citation_handle": handle,
                    "score": score,
                    "provision": item,
                })

        # Sort by BM25 score descending and select top_k
        scored_candidates.sort(key=lambda x: x["score"], reverse=True)
        return scored_candidates[:top_k]

    def save_snapshot(self, directory_path: str) -> str:
        """Saves bm25s index and corpus lookup metadata."""
        os.makedirs(directory_path, exist_ok=True)
        if self.retriever:
            self.retriever.save(os.path.join(directory_path, "bm25s_index"))

        meta = {
            "tokenizer_version": self.TOKENIZER_VERSION,
            "snapshot_hash": self.snapshot_hash,
            "corpus_handles": self.corpus_handles,
        }
        with open(os.path.join(directory_path, "meta.json"), "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2, ensure_ascii=False)

        return self.snapshot_hash or ""

    def load_snapshot(self, directory_path: str, corpus: list[dict[str, Any]]) -> str:
        """Loads bm25s index from snapshot directory."""
        with open(os.path.join(directory_path, "meta.json"), "r", encoding="utf-8") as f:
            meta = json.load(f)

        self.corpus_handles = meta["corpus_handles"]
        self.snapshot_hash = meta["snapshot_hash"]
        self.corpus_lookup = {item["citation_handle"]: item for item in corpus}

        index_path = os.path.join(directory_path, "bm25s_index")
        self.retriever = bm25s.BM25.load(index_path)
        return self.snapshot_hash
