import asyncio
import json
import uuid
from pathlib import Path

from app.cases.models import Case
from app.core.database import async_session_factory
from app.facts.models import FactAssertion
from app.identity.models import Principal
from sqlalchemy import select

ROOT_DIR = Path(__file__).resolve().parent.parent
SPEC_FILE = ROOT_DIR / "demo" / "specs" / "synthetic_demo_case_ecommerce.json"


async def seed_demo_case(session=None):
    if not SPEC_FILE.exists():
        print(f"Error: Demo spec file not found at {SPEC_FILE}")
        return

    with open(SPEC_FILE, "r", encoding="utf-8") as f:
        spec = json.load(f)

    demo_ref = "DEMO-DARAZ-001"

    async def _do_seed(sess):
        # 1. Seed or verify Scenario A (DEMO-DARAZ-001)
        stmt = select(Case).where(Case.display_reference == demo_ref)
        existing = (await sess.execute(stmt)).scalar_one_or_none()
        if existing:
            print(f"Demo case {demo_ref} already exists (ID: {existing.id}). Skipping re-creation.")
        else:
            # Create demo principal
            demo_principal = Principal(
                id=uuid.uuid4(),
                kind="anonymous",
                locale=spec.get("locale", "en-BD"),
            )
            sess.add(demo_principal)
            await sess.flush()

            # Create demo case
            demo_case = Case(
                id=uuid.UUID("1887c4ed-99d6-44f2-9fb4-0c15e9d3287e"),
                principal_id=demo_principal.id,
                display_reference=demo_ref,
                title=spec.get("case_title", "Synthetic Demo Case"),
                jurisdiction=spec.get("jurisdiction", "BD"),
                locale=spec.get("locale", "en-BD"),
                desired_outcomes=spec.get("desired_outcomes", ["full_refund"]),
                lifecycle_status="active",
                is_demo=True,
                merchant_name=spec.get("merchant_name"),
                incident_date=spec.get("incident_date"),
                story_narrative=spec.get("story_narrative"),
                row_version=1,
            )
            sess.add(demo_case)
            await sess.flush()

            # Add assertions
            for a in spec.get("assertions", []):
                field_type = a["field_type"]
                raw_val = a["raw_value"]
                if field_type == "money":
                    typed_val = {"currency": "BDT", "minor_units": 550000}
                elif field_type == "date":
                    typed_val = {"date": str(raw_val)}
                else:
                    typed_val = raw_val

                assertion = FactAssertion(
                    id=uuid.uuid4(),
                    case_id=demo_case.id,
                    field_name=a["field_name"],
                    field_type=field_type,
                    typed_value=typed_val,
                    original_text=a["original_text"],
                    origin=a.get("origin", "document_extraction"),
                    asserting_actor_id=demo_principal.id,
                    created_case_version=1,
                    is_active=True,
                )
                sess.add(assertion)

            await sess.flush()
            print(f"Successfully seeded synthetic demo case: {demo_ref} (Case ID: {demo_case.id})")

        # 2. Also seed deterministic fixtures for Scenario B and Scenario H
        from app.scenarios.service import ScenarioService
        for fid in [
            uuid.UUID("2887c4ed-99d6-44f2-9fb4-0c15e9d3287f"),
            uuid.UUID("3887c4ed-99d6-44f2-9fb4-0c15e9d3287a"),
        ]:
            c = await ScenarioService.ensure_deterministic_demo_case(fid, sess)
            if c:
                print(f"Seeded deterministic demo fixture: {c.display_reference} ({fid})")

    if session is not None:
        await _do_seed(session)
    else:
        async with async_session_factory() as sess:
            await _do_seed(sess)
            await sess.commit()


if __name__ == "__main__":
    asyncio.run(seed_demo_case())
