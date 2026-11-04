"""Private evidence relationships for the agent workspace and Evidence Lens."""
import uuid

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.core.security import get_current_principal
from app.evidence.models import EvidenceItem
from app.facts.models import FactAssertion, FactSourceLink
from app.facts.schemas import FactAssertionOut
from app.facts.service import FactService
from app.identity.models import Principal

router = APIRouter()


@router.post('/v1/cases/{case_id}/sample-payment')
async def add_second_sample_payment(case_id: uuid.UUID,
                                    principal: Principal = Depends(get_current_principal),
                                    db: AsyncSession = Depends(get_db_session)):
    case = await FactService.get_authorized_case(case_id, principal, db)
    if not case.is_demo:
        raise HTTPException(404, 'Sample workspace not found')
    from app.scenarios.sample_evidence import add_sample_payment
    evidence = await add_sample_payment(case, principal, db, second=True)
    return {'evidence_id': str(evidence.id), 'is_demo': True, 'filename': evidence.original_filename}


@router.get('/v1/cases/{case_id}/facts/{fact_id}/provenance')
async def fact_provenance(case_id: uuid.UUID, fact_id: uuid.UUID, response: Response,
                          principal: Principal = Depends(get_current_principal),
                          db: AsyncSession = Depends(get_db_session)):
    case = await FactService.get_authorized_case(case_id, principal, db)
    response.headers['Cache-Control'] = 'private, no-store'
    fact = await db.scalar(select(FactAssertion).where(
        FactAssertion.id == fact_id, FactAssertion.case_id == case.id,
        FactAssertion.is_active.is_(True),
    ))
    if not fact:
        raise HTTPException(404, 'Fact not found')
    links = list((await db.scalars(select(FactSourceLink).where(
        FactSourceLink.assertion_id == fact.id
    ))).all())
    result = []
    for link in links:
        meta = link.locator_meta or {}
        evidence_id = meta.get('evidence_id')
        evidence = None
        if evidence_id:
            try:
                evidence = await db.scalar(select(EvidenceItem).where(
                    EvidenceItem.id == uuid.UUID(evidence_id), EvidenceItem.case_id == case.id,
                    EvidenceItem.principal_id == principal.id, EvidenceItem.status == 'accepted',
                ))
            except (ValueError, TypeError):
                continue
            if not evidence:
                continue
        result.append({
            'id': str(link.id), 'source_type': link.source_type,
            'span_start': link.span_start, 'span_end': link.span_end,
            'quote': meta.get('selected_text'), 'page_number': meta.get('page_number'),
            'normalized_box': meta.get('normalized_box'),
            'evidence': {'id': str(evidence.id), 'filename': evidence.original_filename,
                         'mime_type': evidence.detected_mime_type or evidence.declared_mime_type}
                        if evidence else None,
        })
    return {'fact': FactAssertionOut.model_validate(fact), 'links': result,
            'narrative': case.story_narrative or '', 'case_version': case.row_version}
