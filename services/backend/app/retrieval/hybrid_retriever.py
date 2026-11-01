"""T24, T25: True Hybrid Retrieval Engine fusing Exact Lookup, Dense E5, and BM25s with Reciprocal Rank Fusion (RRF).

Guarantees:
- Exact section ID lookup runs first; if matched, given priority rank 0.
- Parallel dense cosine candidates and BM25 lexical candidates computed over allowed corpus R.
- Allowed-ID mask and temporal validity filters applied BEFORE top-k selection (T25).
- Channel fusion via standard RRF: RRF(d) = sum(1 / (60 + rank_i(d))).
- Deduplicated by unique citation_handle.
- Complete canonical provisions and untruncated qualifications preserved in output context.
- Degraded mode reported honestly if a channel is disabled.
"""

from typing import Any

from app.retrieval.bm25_adapter import BengaliBM25Adapter
from app.retrieval.e5_adapter import E5EmbeddingAdapter
from app.retrieval.provision_service import ProvisionService
from app.retrieval.provisions_data import CANONICAL_PROVISIONS


class HybridRetriever:
    def __init__(self, corpus: list[dict[str, Any]] | None = None) -> None:
        self.corpus = corpus or CANONICAL_PROVISIONS
        self.bm25_adapter = BengaliBM25Adapter()
        self.bm25_adapter.build_index(self.corpus)

    def retrieve(
        self,
        query: str,
        allowed_ids: set[str] | None = None,
        date_context: str | None = None,
        top_k: int = 5,
        dense_enabled: bool = True,
        lexical_enabled: bool = True,
    ) -> dict[str, Any]:
        """T25: Executes exact lookup, dense E5, and BM25 search, fusing ranks with RRF."""
        # 1. Exact section lookup (T24)
        exact_res = ProvisionService.lookup_exact_provision(query)
        exact_matched_handle = None
        exact_item = None
        if exact_res.match_found and exact_res.provision:
            exact_matched_handle = exact_res.provision.citation_handle
            # Find item in corpus
            for item in self.corpus:
                if item["citation_handle"] == exact_matched_handle:
                    exact_item = item
                    break

        # Check if exact match is allowed by ID and date filters
        if exact_matched_handle:
            if allowed_ids is not None and exact_matched_handle not in allowed_ids:
                exact_matched_handle = None
                exact_item = None
            elif date_context and exact_item:
                eff_from = exact_item.get("effective_from")
                eff_to = exact_item.get("effective_to")
                if (eff_from and date_context < eff_from) or (eff_to and date_context >= eff_to):
                    exact_matched_handle = None
                    exact_item = None

        # 2. Dense retrieval channel
        dense_results: list[dict[str, Any]] = []
        if dense_enabled:
            dense_results = E5EmbeddingAdapter.dense_search(
                query=query,
                corpus=self.corpus,
                allowed_ids=allowed_ids,
                date_context=date_context,
                top_k=20,
            )

        # 3. Lexical BM25 channel
        lexical_results: list[dict[str, Any]] = []
        if lexical_enabled:
            lexical_results = self.bm25_adapter.search(
                query=query,
                allowed_ids=allowed_ids,
                date_context=date_context,
                top_k=20,
            )

        # 4. Reciprocal Rank Fusion (RRF)
        # RRF(d) = sum(1 / (60 + rank(d)))
        K = 60.0
        rrf_scores: dict[str, float] = {}
        channel_ranks: dict[str, dict[str, Any]] = {}
        provisions_map: dict[str, dict[str, Any]] = {}

        # Exact match gets rank 0 boost if present
        if exact_matched_handle and exact_item:
            rrf_scores[exact_matched_handle] = 1.0 / (K + 0)
            channel_ranks[exact_matched_handle] = {
                "exact_match": True,
                "dense_rank": None,
                "lexical_rank": None,
            }
            provisions_map[exact_matched_handle] = exact_item

        # Dense ranks
        for rank, res in enumerate(dense_results, start=1):
            h = res["citation_handle"]
            rrf_scores[h] = rrf_scores.get(h, 0.0) + (1.0 / (K + rank))
            channel_ranks.setdefault(
                h, {"exact_match": False, "dense_rank": None, "lexical_rank": None}
            )
            channel_ranks[h]["dense_rank"] = rank
            provisions_map[h] = res["provision"]

        # Lexical ranks
        for rank, res in enumerate(lexical_results, start=1):
            h = res["citation_handle"]
            rrf_scores[h] = rrf_scores.get(h, 0.0) + (1.0 / (K + rank))
            channel_ranks.setdefault(
                h, {"exact_match": False, "dense_rank": None, "lexical_rank": None}
            )
            channel_ranks[h]["lexical_rank"] = rank
            provisions_map[h] = res["provision"]

        # 5. Sort by fused RRF score
        sorted_handles = sorted(rrf_scores.keys(), key=lambda h: rrf_scores[h], reverse=True)

        ranked_items = []
        for h in sorted_handles[:top_k]:
            prov = provisions_map[h]
            ranked_items.append(
                {
                    "citation_handle": h,
                    "provision_path": prov.get("provision_path"),
                    "title_en": prov.get("title_en"),
                    "title_bn": prov.get("title_bn"),
                    "rrf_score": round(rrf_scores[h], 5),
                    "ranks": channel_ranks[h],
                    "canonical_text_bn": prov.get("canonical_text_bn"),
                    "qualifications": prov.get("qualifications_and_exceptions", []),
                }
            )

        is_degraded = not dense_enabled or not lexical_enabled
        status_mode = (
            "hybrid"
            if (dense_enabled and lexical_enabled)
            else ("dense_only" if dense_enabled else "lexical_only")
        )

        return {
            "query": query,
            "status_mode": status_mode,
            "is_degraded": is_degraded,
            "exact_matched_handle": exact_matched_handle,
            "total_candidates": len(ranked_items),
            "results": ranked_items,
        }
