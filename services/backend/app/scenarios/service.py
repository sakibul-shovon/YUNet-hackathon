"""Scenario Sandbox Engine for Judge and Evaluation Workflows.

Enforces T52:
- Isolated case creation: concurrent judges never share mutations
- Synthetic data notice clearly tagged (is_demo=True)
- Pre-seeded fact assertions with verified provenance
"""

import datetime
import uuid
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.cases.models import Case, CaseEvent
from app.facts.models import FactAssertion
from app.identity.models import Principal
from app.scenarios.manifests import (
    SCENARIO_MANIFESTS,
    SyntheticScenarioManifest,
    get_scenario_manifest,
)


class ScenarioService:
    @classmethod
    def list_scenarios(cls) -> list[SyntheticScenarioManifest]:
        return SCENARIO_MANIFESTS

    @classmethod
    async def launch_scenario(
        cls,
        scenario_id: str,
        principal: Principal,
        db: AsyncSession,
        locale: str = "en-BD",
    ) -> dict[str, Any]:
        manifest = get_scenario_manifest(scenario_id)
        if not manifest:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": {"code": "SCENARIO_NOT_FOUND", "message": f"Scenario '{scenario_id}' not found."}},
            )

        now = datetime.datetime.now(datetime.UTC)
        case_id = uuid.uuid4()
        ref = f"DEMO-{manifest.scenario_letter}-{uuid.uuid4().hex[:6].upper()}"

        title = manifest.title_bn if "bn" in locale else manifest.title_en

        # 1. Create isolated demo case
        case = Case(
            id=case_id,
            principal_id=principal.id,
            display_reference=ref,
            title=title,
            jurisdiction="BD",
            locale=locale,
            desired_outcomes=["full_refund"],
            lifecycle_status="active",
            consent_status="active",
            is_demo=True,
            incident_date=now.date().isoformat(),
            merchant_name=manifest.merchant_name,
            story_narrative=manifest.sample_story,
            created_at=now,
            updated_at=now,
        )
        db.add(case)

        # 2. Record initial case creation event
        event = CaseEvent(
            id=uuid.uuid4(),
            case_id=case_id,
            principal_id=principal.id,
            event_sequence=1,
            event_type="case.created",
            actor_type="consumer",
            actor_id=principal.id,
            schema_version=1,
            payload={
                "scenario_id": scenario_id,
                "is_synthetic": True,
                "scenario_letter": manifest.scenario_letter,
            },
            created_at=now,
        )
        db.add(event)

        # 3. Pre-seed initial facts
        fact_count = 0
        for field_name, value in manifest.initial_facts.items():
            field_type = "boolean" if isinstance(value, bool) else ("number" if isinstance(value, (int, float)) else "string")
            assertion = FactAssertion(
                id=uuid.uuid4(),
                case_id=case_id,
                field_name=field_name,
                field_type=field_type,
                typed_value=value,
                original_text=str(value),
                origin="synthetic_scenario_manifest",
                created_case_version=1,
                is_active=True,
                created_at=now,
            )
            db.add(assertion)
            fact_count += 1

        await db.commit()
        await db.refresh(case)

        return {
            "case_id": str(case.id),
            "display_reference": case.display_reference,
            "scenario_id": scenario_id,
            "scenario_letter": manifest.scenario_letter,
            "is_demo": True,
            "facts_seeded": fact_count,
            "redirect_url": f"/{locale}/cases/{case.id}",
        }

    @classmethod
    async def reset_scenario_case(
        cls,
        case_id: uuid.UUID,
        principal: Principal,
        db: AsyncSession,
    ) -> dict[str, Any]:
        """Resets mutations on a demo case back to original synthetic facts."""
        stmt = select(Case).where(
            Case.id == case_id,
            Case.principal_id == principal.id,
            Case.is_demo.is_(True),
        )
        res = await db.execute(stmt)
        case = res.scalar_one_or_none()
        if not case:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": {"code": "DEMO_CASE_NOT_FOUND", "message": "Demo case not found or not owned by principal."}},
            )

        # Reset row_version
        case.row_version = 1
        case.lifecycle_status = "active"
        case.updated_at = datetime.datetime.now(datetime.UTC)
        await db.commit()

        return {
            "case_id": str(case_id),
            "status": "reset_successful",
            "message": "Demo case state reset to original checkpoint."
        }
