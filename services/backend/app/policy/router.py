import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.core.security import get_current_principal
from app.facts.schemas import FactAssertionCreate, FactAssertionOut
from app.facts.service import FactService
from app.identity.models import Principal
from app.policy.domain_catalogue import (
    DomainCatalogueResponse,
    DomainCatalogueService,
)
from app.policy.engine import (
    ProceduralAssessmentEngine,
    ProceduralAssessmentOut,
    WhatIfSimulationRequest,
    WhatIfSimulationResult,
)

router = APIRouter(tags=["Case Procedural Assessment"])


class NBQAnswerRequest(BaseModel):
    question_key: str
    fact_field: str
    value: Any
    field_type: str = "boolean"


class NBQSkipRequest(BaseModel):
    question_key: str
    fact_field: str


class WhatIfApplyRequest(BaseModel):
    overrides: dict[str, Any] = Field(..., min_length=1)


# In-memory skipped questions tracking per case for this runtime session
_CASE_SKIPPED_QUESTIONS: dict[uuid.UUID, set[str]] = {}


@router.get(
    "/v1/cases/{case_id}/assessment",
    response_model=ProceduralAssessmentOut,
)
async def get_case_assessment(
    case_id: uuid.UUID,
    principal: Principal = Depends(get_current_principal),
    db: AsyncSession = Depends(get_db_session),
):
    """T19/T20/T30/T32: Computes deterministic procedural assessment, condition traces, NBQ, and next actions."""
    case = await FactService.get_authorized_case(case_id, principal, db)
    skips = _CASE_SKIPPED_QUESTIONS.get(case.id, set())
    return await ProceduralAssessmentEngine.assess_case(case, db, skipped_questions=skips)


@router.post(
    "/v1/cases/{case_id}/assess",
    response_model=ProceduralAssessmentOut,
)
async def trigger_case_assessment(
    case_id: uuid.UUID,
    principal: Principal = Depends(get_current_principal),
    db: AsyncSession = Depends(get_db_session),
):
    """Recomputes procedural assessment against the latest active facts."""
    case = await FactService.get_authorized_case(case_id, principal, db)
    skips = _CASE_SKIPPED_QUESTIONS.get(case.id, set())
    return await ProceduralAssessmentEngine.assess_case(case, db, skipped_questions=skips)


@router.post(
    "/v1/cases/{case_id}/what-if",
    response_model=WhatIfSimulationResult,
)
async def simulate_what_if_scenario(
    case_id: uuid.UUID,
    payload: WhatIfSimulationRequest,
    principal: Principal = Depends(get_current_principal),
    db: AsyncSession = Depends(get_db_session),
):
    """T31: Ephemeral What-If simulation with ZERO database side effects."""
    case = await FactService.get_authorized_case(case_id, principal, db)
    try:
        return await ProceduralAssessmentEngine.simulate_what_if(case, payload.overrides, db)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post(
    "/v1/cases/{case_id}/what-if/apply",
    response_model=list[FactAssertionOut],
)
async def apply_what_if_overrides(
    case_id: uuid.UUID,
    payload: WhatIfApplyRequest,
    principal: Principal = Depends(get_current_principal),
    db: AsyncSession = Depends(get_db_session),
):
    """Explicit workflow to commit simulated facts into the actual case as reviewed assertions."""
    case = await FactService.get_authorized_case(case_id, principal, db)

    # Check for forbidden credential fields (T32)
    for k in payload.overrides:
        if any(c in k.lower() for c in ProceduralAssessmentEngine.FORBIDDEN_CREDENTIAL_TERMS):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Prohibited credential field '{k}' cannot be collected or stored (T32).",
            )

    applied_assertions: list[FactAssertionOut] = []
    for field_name, value in payload.overrides.items():
        # Determine field type
        if isinstance(value, bool):
            ft = "boolean"
        elif isinstance(value, (int, float)):
            ft = "money" if "amount" in field_name or "price" in field_name else "string"
        elif isinstance(value, str) and len(value) == 10 and value[4] == "-" and value[7] == "-":
            ft = "date"
        else:
            ft = "string"

        assertion = await FactService.create_assertion(
            case.id,
            FactAssertionCreate(
                field_name=field_name,
                field_type=ft,
                raw_value=value,
                origin="what_if_adopted",
            ),
            principal,
            db,
        )
        applied_assertions.append(assertion)

    return applied_assertions


@router.post(
    "/v1/cases/{case_id}/nbq/answer",
    response_model=ProceduralAssessmentOut,
)
async def answer_next_best_question(
    case_id: uuid.UUID,
    payload: NBQAnswerRequest,
    principal: Principal = Depends(get_current_principal),
    db: AsyncSession = Depends(get_db_session),
):
    """T32: Answers the Next Best Question, creating an active fact assertion and returning updated assessment."""
    case = await FactService.get_authorized_case(case_id, principal, db)

    # T32 Invariant: Strictly forbid OTP / PIN collection
    if any(c in payload.fact_field.lower() for c in ProceduralAssessmentEngine.FORBIDDEN_CREDENTIAL_TERMS):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Collection of OTP, PIN, password, or security credentials is strictly prohibited (T32).",
        )

    await FactService.create_assertion(
        case.id,
        FactAssertionCreate(
            field_name=payload.fact_field,
            field_type=payload.field_type,
            raw_value=payload.value,
            origin="user_statement",
        ),
        principal,
        db,
    )

    # Remove from skipped if previously skipped
    if case.id in _CASE_SKIPPED_QUESTIONS:
        _CASE_SKIPPED_QUESTIONS[case.id].discard(payload.fact_field)
        _CASE_SKIPPED_QUESTIONS[case.id].discard(payload.question_key)

    skips = _CASE_SKIPPED_QUESTIONS.get(case.id, set())
    return await ProceduralAssessmentEngine.assess_case(case, db, skipped_questions=skips)


@router.post(
    "/v1/cases/{case_id}/nbq/skip",
    response_model=ProceduralAssessmentOut,
)
async def skip_next_best_question(
    case_id: uuid.UUID,
    payload: NBQSkipRequest,
    principal: Principal = Depends(get_current_principal),
    db: AsyncSession = Depends(get_db_session),
):
    """T32 Invariant: Skipping a question preserves UNKNOWN status (never coerced to false)

    and ensures the question is not repetitively prompted.
    """
    case = await FactService.get_authorized_case(case_id, principal, db)

    if case.id not in _CASE_SKIPPED_QUESTIONS:
        _CASE_SKIPPED_QUESTIONS[case.id] = set()

    _CASE_SKIPPED_QUESTIONS[case.id].add(payload.fact_field)
    _CASE_SKIPPED_QUESTIONS[case.id].add(payload.question_key)

    skips = _CASE_SKIPPED_QUESTIONS[case.id]
    return await ProceduralAssessmentEngine.assess_case(case, db, skipped_questions=skips)


# --- P12.4 Domain Catalogue & Jurisdiction Disclosure Endpoints ---


@router.get(
    "/v1/domains/catalogue",
    response_model=DomainCatalogueResponse,
)
async def get_domain_catalogue(
    jurisdiction: str = "BD",
):
    """P12.4: Transparency catalogue disclosing exact verified support depth for each domain."""
    return DomainCatalogueService.get_catalogue(jurisdiction=jurisdiction)


@router.get(
    "/v1/domains/{domain_id}/support",
)
async def check_domain_support(
    domain_id: str,
    jurisdiction: str = "BD",
):
    """P12.4: Checks domain support and enforces unsupported-jurisdiction fallback."""
    return DomainCatalogueService.check_domain_support(domain_id=domain_id, jurisdiction=jurisdiction)
