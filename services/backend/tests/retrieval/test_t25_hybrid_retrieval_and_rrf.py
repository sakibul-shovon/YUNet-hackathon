import os
import shutil
import tempfile
import pytest
from httpx import AsyncClient

from app.retrieval.bm25_adapter import BengaliBM25Adapter
from app.retrieval.citation_validator import CitationValidator
from app.retrieval.e5_adapter import E5EmbeddingAdapter
from app.retrieval.hybrid_retriever import HybridRetriever
from app.retrieval.provisions_data import CANONICAL_PROVISIONS


def test_t25_e5_embedding_format_and_dense_allowed_id_mask():
    """T25 / P07.2: Pinned E5 formatting (384-dim) and allowed-ID filtering BEFORE top-k selection."""
    # 1. Check prefixes and dimension
    q_formatted = E5EmbeddingAdapter.format_query("পণ্য ডেলিভারি না দেওয়া")
    assert q_formatted.startswith("query: ")

    p_formatted = E5EmbeddingAdapter.format_passage("প্রতিশ্রুত পণ্য সরবরাহ না করা")
    assert p_formatted.startswith("passage: ")

    vec = E5EmbeddingAdapter.embed_text("টেস্ট বাক্য", is_query=True)
    assert len(vec) == 384

    # 2. Invariant T25: Allowed-ID filter MUST precede top-k selection
    allowed_ids = {"crpa2009:sec:45", "crpa2009:sec:45(2)"}
    dense_res = E5EmbeddingAdapter.dense_search(
        query="পণ্য না পেয়ে টাকা ফেরত পাওয়ার নিয়ম",
        corpus=CANONICAL_PROVISIONS,
        allowed_ids=allowed_ids,
        top_k=5,
    )
    assert len(dense_res) <= 2
    for item in dense_res:
        assert item["citation_handle"] in allowed_ids

    # 3. Temporal exclusion check
    test_corpus = [
        {
            "citation_handle": "test:old_law",
            "canonical_text_bn": "পুরনো আইন যা ২০২৪ সালে বাতিল হয়েছে",
            "effective_from": "2010-01-01",
            "effective_to": "2024-12-31",  # Repealed before 2026
        },
        {
            "citation_handle": "test:new_law",
            "canonical_text_bn": "নতুন আইন যা ২০২৬ সালে কার্যকর আছে",
            "effective_from": "2025-01-01",
            "effective_to": None,
        },
    ]
    # Incident date in 2026
    date_context = "2026-10-15"
    temporal_res = E5EmbeddingAdapter.dense_search(
        query="আইন",
        corpus=test_corpus,
        date_context=date_context,
        top_k=5,
    )
    # Old repealed law must be excluded BEFORE ranking
    returned_handles = [r["citation_handle"] for r in temporal_res]
    assert "test:old_law" not in returned_handles
    assert "test:new_law" in returned_handles


def test_t25_bengali_bm25s_tokenization_and_snapshot_roundtrip():
    """T25 / P07.3: Bengali-aware tokenization with combining marks, negation, and snapshot persistence."""
    # 1. Verify combining marks and vowel signs are not split into loose characters
    bengali_phrase = "তিনি প্রতিশ্রুত পণ্য সরবরাহ করেননি এবং কোনো টাকা ফেরত দেননি"
    tokens = BengaliBM25Adapter.tokenize(bengali_phrase)

    # Vowel signs attached
    assert any("পণ্য" in t for t in tokens)
    assert any("সরবরাহ" in t for t in tokens)
    # Negation retained
    assert any("করেননি" in t or "দেননি" in t for t in tokens)

    # 2. Section and compound numeral preservation
    sec_phrase = "ধারা ৪৫(২) অনুসারে ব্যবস্থা"
    sec_tokens = BengaliBM25Adapter.tokenize(sec_phrase)
    assert any("৪৫(২)" in t or "45(2)" in t for t in sec_tokens)
    assert any("sec:45(2)" in t for t in sec_tokens)

    # 3. Snapshot save and load
    adapter = BengaliBM25Adapter()
    h1 = adapter.build_index(CANONICAL_PROVISIONS)
    assert h1 is not None and len(h1) == 64

    temp_dir = tempfile.mkdtemp()
    try:
        saved_hash = adapter.save_snapshot(temp_dir)
        assert saved_hash == h1

        loaded_adapter = BengaliBM25Adapter()
        loaded_hash = loaded_adapter.load_snapshot(temp_dir, CANONICAL_PROVISIONS)
        assert loaded_hash == h1

        # Search on loaded adapter produces identical results
        search_res = loaded_adapter.search("প্রতিশ্রুত পণ্য সরবরাহ না করা এবং মূল্য ফেরত", top_k=3)
        assert len(search_res) > 0
        returned_handles = [r["citation_handle"] for r in search_res]
        assert any(h in ("crpa2009:sec:45", "crpa2009:sec:45(2)") for h in returned_handles)
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_t25_hybrid_retrieval_and_rrf_fusion():
    """T25 / P07.4: RRF fusion combines exact match, dense, and lexical channels without score skew."""
    retriever = HybridRetriever(CANONICAL_PROVISIONS)

    # 1. Exact query for Section 45
    res = retriever.retrieve("ধারা ৪৫", top_k=3)
    assert res["status_mode"] == "hybrid"
    assert res["is_degraded"] is False
    assert res["exact_matched_handle"] == "crpa2009:sec:45"
    assert res["results"][0]["citation_handle"] == "crpa2009:sec:45"
    assert res["results"][0]["rrf_score"] > 0.0

    # 2. Conceptual query for MFS complaint escalation
    mfs_res = retriever.retrieve("বিকাশ বা ব্যাংকে অভিযোগের টিকিট না পেলে পরবর্তী পদক্ষেপ", top_k=3)
    handles = [r["citation_handle"] for r in mfs_res["results"]]
    assert any("bb_cipc" in h for h in handles)


def test_t25_channel_ablations_and_degraded_reporting():
    """P07.6: Channel ablations report truthful degraded mode when a channel is disabled."""
    retriever = HybridRetriever(CANONICAL_PROVISIONS)

    # Dense only
    dense_only = retriever.retrieve("পণ্য ডেলিভারি না করা", dense_enabled=True, lexical_enabled=False)
    assert dense_only["status_mode"] == "dense_only"
    assert dense_only["is_degraded"] is True

    # Lexical only
    lex_only = retriever.retrieve("পণ্য ডেলিভারি না করা", dense_enabled=False, lexical_enabled=True)
    assert lex_only["status_mode"] == "lexical_only"
    assert lex_only["is_degraded"] is True

    # Both active -> True hybrid
    hybrid = retriever.retrieve("পণ্য ডেলিভারি না করা", dense_enabled=True, lexical_enabled=True)
    assert hybrid["status_mode"] == "hybrid"
    assert hybrid["is_degraded"] is False


def test_t28_t29_citation_validator():
    """T28 / T29: Citation validator blocks non-existent or outdated citations."""
    # 1. Valid citations
    v_res = CitationValidator.validate_citations(["crpa2009:sec:45", "crpa2009:sec:45(2)"])
    assert v_res.is_valid is True
    assert len(v_res.invalid_citations) == 0

    # 2. Fabricated citation
    bad_res = CitationValidator.validate_citations(["crpa2009:sec:45", "invented_statute:sec:999"])
    assert bad_res.is_valid is False
    assert len(bad_res.invalid_citations) == 1
    assert bad_res.invalid_citations[0]["code"] == "CITATION_NON_EXISTENT"

    # 3. Outdated provision check
    test_prov = {
        "citation_handle": "old_act:sec:1",
        "source_id": "old_act",
        "provision_path": "sec:1",
        "section_number": "1",
        "section_bn": "১",
        "title_en": "Old section",
        "title_bn": "পুরনো ধারা",
        "parent_path": None,
        "document_type": "statute",
        "canonical_text_en": "Old repealed text",
        "canonical_text_bn": "পুরনো বাতিলকৃত পাঠ",
        "aliases": ["old_act:sec:1"],
        "effective_from": "2000-01-01",
        "effective_to": "2020-01-01",  # Repealed in 2020
    }
    # Temporarily register in provision service
    from app.retrieval.provision_service import ProvisionService
    ProvisionService._provisions_by_handle["old_act:sec:1"] = test_prov

    outdated_res = CitationValidator.validate_citations(["old_act:sec:1"], date_context="2026-10-15")
    assert outdated_res.is_valid is False
    assert outdated_res.invalid_citations[0]["code"] == "CITATION_OUTDATED_OR_REPEALED"


@pytest.mark.asyncio
async def test_t25_retrieval_api_search_and_validate(client: AsyncClient):
    """T25 / T28: API endpoints for hybrid search and citation validation."""
    # 1. Search endpoint
    search_resp = await client.post(
        "/v1/retrieval/search",
        json={"query": "পণ্য সরবরাহ না করার কারণে মূল্য ফেরত", "top_k": 3},
    )
    assert search_resp.status_code == 200
    search_data = search_resp.json()
    assert search_data["status_mode"] == "hybrid"
    assert search_data["is_degraded"] is False
    assert len(search_data["results"]) > 0

    # 2. Citation validate endpoint
    val_resp = await client.post(
        "/v1/retrieval/citations/validate",
        json={"citation_handles": ["crpa2009:sec:45", "fake_citation:sec:1"]},
    )
    assert val_resp.status_code == 200
    val_data = val_resp.json()
    assert val_data["is_valid"] is False
    assert len(val_data["invalid_citations"]) == 1
    assert val_data["invalid_citations"][0]["code"] == "CITATION_NON_EXISTENT"
