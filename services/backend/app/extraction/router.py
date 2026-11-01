import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.core.security import get_current_principal
from app.extraction.adapter import CaseExtractor
from app.extraction.schemas import FactProposalSet
from app.facts.schemas import FactAssertionCreate
from app.facts.service import FactService
from app.identity.models import Principal

router = APIRouter(tags=["Case Text Extraction"])


@router.post(
    "/v1/cases/{case_id}/extract",
    response_model=FactProposalSet,
    status_code=status.HTTP_200_OK,
)
async def extract_case_narrative(
    case_id: uuid.UUID,
    auto_persist: bool = Query(
        False,
        description="Whether to automatically persist extracted proposals as draft assertions",
    ),
    principal: Principal = Depends(get_current_principal),
    db: AsyncSession = Depends(get_db_session),
):
    """T08: Extracts structured fact proposals and verbatim text spans from the case story narrative."""
    c = await FactService.get_authorized_case(case_id, principal, db)

    if getattr(c, "consent_status", "active") == "withdrawn":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": {
                    "code": "CONSENT_WITHDRAWN",
                    "message": "External processing consent has been withdrawn by user (T37)",
                }
            },
        )

    narrative = c.story_narrative or ""
    proposal_set = CaseExtractor.propose(narrative)

    if auto_persist and proposal_set.proposals:
        for prop in proposal_set.proposals:
            # Check if matching span exists
            span_start = None
            span_end = None
            if prop.span_ids:
                s_id = prop.span_ids[0]
                matching_spans = [s for s in proposal_set.spans if s.span_id == s_id]
                if matching_spans:
                    span_start = matching_spans[0].start_offset
                    span_end = matching_spans[0].end_offset

            create_in = FactAssertionCreate(
                field_name=prop.field_name,
                field_type=prop.field_type,
                raw_value=prop.original_text
                if (prop.field_type == "money" and prop.original_text)
                else prop.raw_value,
                original_text=prop.original_text,
                origin="document_extraction",
                span_start=span_start,
                span_end=span_end,
            )
            await FactService.create_assertion(c.id, create_in, principal, db)

    return proposal_set
