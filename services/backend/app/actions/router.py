import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.actions.draft_generator import DraftRequestGenerator, DraftRequestOut
from app.core.database import get_db_session
from app.core.security import get_current_principal
from app.facts.models import FactAssertion
from app.facts.service import FactService
from app.identity.models import Principal

router = APIRouter(tags=["Case Actions & Drafts"])


@router.get(
    "/v1/cases/{case_id}/draft",
    response_model=DraftRequestOut,
)
async def get_case_draft_request(
    case_id: uuid.UUID,
    locale: str = Query("en", pattern="^(en|bn)$"),
    remedy: str = Query("full_refund"),
    principal: Principal = Depends(get_current_principal),
    db: AsyncSession = Depends(get_db_session),
):
    """T26: Generates a respectful, legally grounded, unsubmitted dispute request draft."""
    case = await FactService.get_authorized_case(case_id, principal, db)

    # Fetch active facts
    stmt = select(FactAssertion).where(
        FactAssertion.case_id == case.id,
        FactAssertion.is_active.is_(True),
    )
    res = await db.execute(stmt)
    assertions = res.scalars().all()

    facts_dict = {}
    for a in assertions:
        if a.field_type == "money" and isinstance(a.typed_value, dict):
            facts_dict[a.field_name] = a.typed_value.get("minor_units")
        elif a.field_type == "date" and isinstance(a.typed_value, dict):
            facts_dict[a.field_name] = a.typed_value.get("date")
        else:
            facts_dict[a.field_name] = a.typed_value

    effective_remedy = remedy
    if case.desired_outcomes and len(case.desired_outcomes) > 0:
        effective_remedy = case.desired_outcomes[0]

    return DraftRequestGenerator.generate_draft(
        case_title=case.title,
        merchant_name=case.merchant_name,
        facts=facts_dict,
        locale=locale,
        remedy=effective_remedy,
    )
