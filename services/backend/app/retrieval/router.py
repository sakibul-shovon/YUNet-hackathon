from fastapi import APIRouter, HTTPException, Query, status

from app.retrieval.citation_validator import CitationValidator
from app.retrieval.hybrid_retriever import HybridRetriever
from app.retrieval.provision_service import ProvisionService
from app.retrieval.schemas import (
    CitationValidationRequest,
    CitationValidationResponse,
    HybridSearchRequest,
    ProvisionLookupResult,
    ProvisionOut,
    ProvisionTreeItem,
)

router = APIRouter(prefix="/v1/retrieval", tags=["Knowledge & Retrieval"])
_hybrid_retriever: HybridRetriever | None = None


def get_retriever() -> HybridRetriever:
    global _hybrid_retriever
    if _hybrid_retriever is None:
        _hybrid_retriever = HybridRetriever()
    return _hybrid_retriever


@router.post(
    "/search",
    status_code=status.HTTP_200_OK,
)
async def hybrid_search_provisions(req: HybridSearchRequest):
    """T25: Executes parallel dense E5 and BM25 search with allowed-ID filtering and RRF."""
    retriever = get_retriever()
    allowed_set = set(req.allowed_ids) if req.allowed_ids else None
    return retriever.retrieve(
        query=req.query,
        allowed_ids=allowed_set,
        date_context=req.date_context,
        top_k=req.top_k,
        dense_enabled=req.dense_enabled,
        lexical_enabled=req.lexical_enabled,
    )


@router.post(
    "/citations/validate",
    response_model=CitationValidationResponse,
    status_code=status.HTTP_200_OK,
)
async def validate_statutory_citations(req: CitationValidationRequest):
    """T28: Validates statutory citations against existence, scope, and temporal interval."""
    allowed_scope = set(req.allowed_source_ids) if req.allowed_source_ids else None
    res = CitationValidator.validate_citations(
        citation_handles=req.citation_handles,
        date_context=req.date_context,
        allowed_source_ids=allowed_scope,
    )
    return CitationValidationResponse(
        is_valid=res.is_valid,
        valid_citations=res.valid_citations,
        invalid_citations=res.invalid_citations,
    )


@router.get(
    "/provisions/lookup",
    response_model=ProvisionLookupResult,
    status_code=status.HTTP_200_OK,
)
async def lookup_provision_by_exact_section(
    q: str = Query(
        ...,
        description="Exact section reference in Bengali or Latin (e.g. 'sec:45', 'ধারা ৪৫(২)', 'sec:60')",
    ),
):
    """T24: Exact Bengali/Latin section lookup.

    Preserves parent context, subsection exceptions, and qualifications.
    Returns match_found=False without inventing missing provisions.
    """
    res = ProvisionService.lookup_exact_provision(q)
    return res


@router.get(
    "/provisions/{citation_handle:path}",
    response_model=ProvisionOut,
    status_code=status.HTTP_200_OK,
)
async def get_provision_by_citation_handle(citation_handle: str):
    """T24: Retrieves verified statutory provision by stable citation handle."""
    res = ProvisionService.lookup_exact_provision(citation_handle)
    if not res.match_found or not res.provision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Provision citation '{citation_handle}' not found in governed corpus.",
        )
    return res.provision


@router.get(
    "/sources/{source_id}/provisions",
    response_model=list[ProvisionTreeItem],
    status_code=status.HTTP_200_OK,
)
async def get_source_provisions_tree(source_id: str):
    """Returns the hierarchical provision tree for an official source."""
    return ProvisionService.get_provisions_tree(source_id)
