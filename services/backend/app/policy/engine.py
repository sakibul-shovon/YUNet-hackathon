import datetime
import uuid
from typing import Any, ClassVar

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.cases.models import Case
from app.knowledge.source_registry import get_source_by_id
from app.policy.ast import PolicyRule
from app.policy.evaluator import PolicyEvaluator, RouteStatus


class AssessmentRouteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    route_id: str
    rule_id: str
    issue_type: str
    status: RouteStatus
    reasons: list[str]
    allowed_actions: list[str]
    source_dependencies: list[str]
    statutory_citations: list[str] = Field(default_factory=list)
    supported_remedies: list[str] = Field(default_factory=list)
    unsupported_remedies: list[str] = Field(default_factory=list)
    unsupported_remedy_warnings: list[str] = Field(default_factory=list)
    condition_trace: list[dict[str, Any]]


class NextBestQuestion(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    question_key: str
    fact_field: str
    prompt_en: str
    prompt_bn: str
    question_type: str  # 'boolean', 'select', 'date', 'money'
    options: list[dict[str, str]] | None = None
    priority: str  # 'safety', 'route_disambiguation', 'materiality', 'readiness'
    relevance_rationale: str


class ProceduralAssessmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    case_id: uuid.UUID
    overall_status: str
    primary_action: str
    primary_action_title_en: str
    primary_action_title_bn: str
    secondary_actions: list[dict[str, str]]
    routes: list[AssessmentRouteOut]
    next_best_question: NextBestQuestion | None = None
    source_cards: list[dict[str, Any]]
    limitation_warning_en: str | None = None
    limitation_warning_bn: str | None = None
    days_remaining_in_limitation: int | None = None
    is_deadline_uncertain: bool = False


class WhatIfSimulationRequest(BaseModel):
    overrides: dict[str, Any]


class RouteDiffItem(BaseModel):
    route_id: str
    issue_type: str
    baseline_status: RouteStatus
    simulated_status: RouteStatus
    changed: bool


class WhatIfSimulationResult(BaseModel):
    case_id: uuid.UUID
    overrides: dict[str, Any]
    baseline_routes: list[AssessmentRouteOut]
    simulated_routes: list[AssessmentRouteOut]
    route_diff: list[RouteDiffItem]
    is_material_change: bool
    summary_en: str
    summary_bn: str


class ProceduralAssessmentEngine:
    """Deterministic policy assessment engine enforcing:

    - T17/T18: Kleene 3-valued policy evaluation, source health gates
    - T19: Merchant non-delivery vs Provider service failure separation
    - T20: Mandatory Stage 1 provider grievance before Central Bank CIPC escalation
    - T30: Limitation deadline calculation and explicit uncertain date caution
    - T31: In-memory What-If simulation with zero DB persistence
    - T32: Safety hazard NBQ prioritization, strict OTP/PIN prohibition, skip semantics
    """

    # Static Question Catalogue for Next Best Questions (NBQ)
    QUESTION_CATALOGUE: ClassVar[dict[str, NextBestQuestion]] = {
        "product_presents_immediate_hazard": NextBestQuestion(
            question_key="nbq_product_hazard",
            fact_field="product_presents_immediate_hazard",
            prompt_en="Does this product pose an immediate physical danger, chemical toxicity, or fire hazard?",
            prompt_bn="পণ্যটি কি তাৎক্ষণিক শারীরিক বিপদ, রাসায়নিক বিষক্রিয়া বা অগ্নিকাণ্ডের ঝুঁকি তৈরি করছে?",
            question_type="boolean",
            priority="safety",
            relevance_rationale="Emergency product hazards trigger immediate 16121 hotline escalation.",
        ),
        "goods_delivered": NextBestQuestion(
            question_key="nbq_goods_delivered",
            fact_field="goods_delivered",
            prompt_en="Did you receive the ordered goods or products from the merchant?",
            prompt_bn="আপনি কি বিক্রেতার কাছ থেকে অর্ডারকৃত পণ্যটি হাতে পেয়েছেন?",
            question_type="boolean",
            priority="route_disambiguation",
            relevance_rationale="Distinguishes between non-delivery failure (Section 45) and defective goods (Section 41/44).",
        ),
        "promised_delivery_date_passed": NextBestQuestion(
            question_key="nbq_delivery_date_passed",
            fact_field="promised_delivery_date_passed",
            prompt_en="Has the committed or promised delivery date already elapsed?",
            prompt_bn="বিক্রেতার দেওয়া প্রতিশ্রুত ডেলিভারির তারিখ কি পার হয়ে গেছে?",
            question_type="boolean",
            priority="materiality",
            relevance_rationale="A delivery dispute is procedurally valid only once the promised deadline has expired.",
        ),
        "transaction_unauthorized": NextBestQuestion(
            question_key="nbq_transaction_unauthorized",
            fact_field="transaction_unauthorized",
            prompt_en="Was this transaction executed without your permission or authentication?",
            prompt_bn="লেনদেনটি কি আপনার অনুমতি বা অথেন্টিকেশন ব্যতিরেকে সম্পন্ন হয়েছিল?",
            question_type="boolean",
            priority="materiality",
            relevance_rationale="Determines whether financial provider dispute procedures apply.",
        ),
        "provider_ticket_filed": NextBestQuestion(
            question_key="nbq_provider_ticket_filed",
            fact_field="provider_ticket_filed",
            prompt_en="Have you already filed a formal complaint with your MFS/bank provider and received a ticket number?",
            prompt_bn="আপনি কি বিকাশ/নগদ/ব্যাংকের হেল্পলাইনে অভিযোগ দায়ের করে কোনো ট্র্যাকিং টিকিট নম্বর পেয়েছেন?",
            question_type="boolean",
            priority="readiness",
            relevance_rationale="Bangladesh Bank CIPC regulations strictly mandate provider-level grievance before central bank escalation (T20).",
        ),
        "seller_notified_within_warranty": NextBestQuestion(
            question_key="nbq_seller_notified_warranty",
            fact_field="seller_notified_within_warranty",
            prompt_en="Did you notify the merchant about the defect within the applicable warranty or return window?",
            prompt_bn="আপনি কি ওয়ারেন্টি বা রিটার্ন মেয়াদের ভেতরে বিক্রেতাকে ত্রুটি সম্পর্কে জানিয়েছিলেন?",
            question_type="boolean",
            priority="materiality",
            relevance_rationale="Warranty and notification timing affects replacement and repair remedies.",
        ),
    }

    # Forbidden credential terms (T32)
    FORBIDDEN_CREDENTIAL_TERMS: ClassVar[set[str]] = {
        "otp", "pin", "password", "cvv", "secret", "cvv2", "mfs_pin", "card_cvv",
    }

    @classmethod
    def load_starter_rules(cls) -> list[PolicyRule]:
        """Loads canonical starter rules."""
        from pathlib import Path

        import yaml


        repo_root = Path(__file__).resolve().parents[4]
        packs_dir = repo_root / "knowledge" / "packs" / "bd"

        rules: list[PolicyRule] = []
        if packs_dir.exists():
            for yf in sorted(packs_dir.rglob("*.yaml")):
                with open(yf, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                rules.append(PolicyRule.model_validate(data))
        return rules

    @classmethod
    def extract_facts_from_db_records(
        cls,
        assertions: list[Any],
        case: Case,
    ) -> dict[str, Any]:
        """Unwraps fact assertion models into a flat dictionary."""
        facts_dict: dict[str, Any] = {}
        for a in assertions:
            if a.field_type == "money" and isinstance(a.typed_value, dict):
                facts_dict[a.field_name] = a.typed_value.get("minor_units")
            elif a.field_type == "date" and isinstance(a.typed_value, dict):
                facts_dict[a.field_name] = a.typed_value.get("date")
            else:
                facts_dict[a.field_name] = a.typed_value

        # Infer merchant/channel if missing
        if "purchase_channel" not in facts_dict and case.merchant_name:
            facts_dict["purchase_channel"] = "ecommerce"

        # Transfer incident_date from case if present
        if "incident_date" not in facts_dict and case.incident_date:
            facts_dict["incident_date"] = case.incident_date

        return facts_dict

    @classmethod
    def evaluate_all_rules(
        cls,
        rules: list[PolicyRule],
        facts_dict: dict[str, Any],
        desired_outcomes: list[str] | None = None,
        source_health: dict[str, str] | None = None,
        case: Case | None = None,
    ) -> tuple[list[AssessmentRouteOut], set[str]]:
        """Evaluates rules against facts with T19/T20/T30 checks."""
        routes_out: list[AssessmentRouteOut] = []
        needed_facts: set[str] = set()
        user_outcomes = set(desired_outcomes or [])

        for rule in rules:
            # T19 Guard: If it's an MFS/bank rule, only evaluate if alleged provider fault or unauthorized transaction is present
            if rule.issue_type == "mfs_unauthorized_charge":
                is_unauthorized = facts_dict.get("transaction_unauthorized") is True
                provider_conduct = facts_dict.get("alleged_provider_service_failure") is True
                if not (is_unauthorized or provider_conduct):
                    continue

            eval_res = PolicyEvaluator.evaluate(
                rule,
                facts_dict,
                source_health=source_health,
                allow_test_only=False,
            )

            # Check trace for unknown condition nodes
            trace_dicts = []
            has_any_true_condition = False
            route_unknown_facts: list[str] = []

            for tr in eval_res.trace:
                trace_dicts.append({
                    "node_type": tr.node_type,
                    "fact": tr.fact,
                    "inspected_value": tr.inspected_value,
                    "outcome": tr.outcome.value,
                    "details": tr.details,
                })
                if tr.outcome.value == "TRUE":
                    has_any_true_condition = True
                elif tr.outcome.value == "UNKNOWN" and tr.fact:
                    route_unknown_facts.append(tr.fact)

            is_safety_candidate = False
            if rule.issue_type == "product_safety_hazard":
                story = ((case.story_narrative if case else "") or "").lower()
                title = ((case.title if case else "") or "").lower()
                hazard_keywords = {"hazard", "danger", "explod", "fire", "burn", "shock", "electric", "toxic", "poison", "harm", "injury", "safety"}
                if any(k in story or k in title for k in hazard_keywords) or facts_dict.get("alleged_safety_hazard"):
                    is_safety_candidate = True

            # Only consider unknown facts as candidates if the route is an active hypothesis or safety candidate
            if (has_any_true_condition or is_safety_candidate) and eval_res.status == RouteStatus.NEEDS_FACTS:
                for uf in route_unknown_facts:
                    needed_facts.add(uf)

            # Unsupported remedy check
            unsupported_warnings: list[str] = []
            for uo in user_outcomes:
                if uo in rule.unsupported_remedies:
                    unsupported_warnings.append(
                        f"Remedy '{uo}' is not statutorily available for {rule.issue_type}. "
                        f"Supported remedies are: {', '.join(rule.supported_remedies)}."
                    )

            routes_out.append(AssessmentRouteOut(
                route_id=f"route_{rule.rule_id}",
                rule_id=rule.rule_id,
                issue_type=rule.issue_type,
                status=eval_res.status,
                reasons=eval_res.reasons,
                allowed_actions=eval_res.allowed_actions,
                source_dependencies=rule.source_dependencies,
                statutory_citations=rule.statutory_citations,
                supported_remedies=rule.supported_remedies,
                unsupported_remedies=rule.unsupported_remedies,
                unsupported_remedy_warnings=unsupported_warnings,
                condition_trace=trace_dicts,
            ))

        return routes_out, needed_facts

    @classmethod
    def calculate_statutory_limitation(
        cls,
        facts_dict: dict[str, Any],
        case_incident_date: str | None,
        statutory_limitation_days: int = 30,
    ) -> tuple[str | None, str | None, int | None, bool]:
        """T30 Invariant: Exact cutoff is withheld when trigger/date counting is uncertain.

        Returns (warning_en, warning_bn, days_remaining, is_uncertain).
        """
        raw_date = facts_dict.get("incident_date") or case_incident_date
        if not raw_date:
            warning_en = (
                "Incident or cause-of-action date is unverified; exact 30-day statutory limitation cutoff "
                "(CRPA 2009 Sec 60) cannot be definitively computed. Prompt filing advised."
            )
            warning_bn = (
                "ঘটনার তারিখ নিশ্চিত না হওয়ায় ভোক্তা অধিকার আইনের ৩০ দিনের সময়সীমা নিশ্চিতভাবে গণনা করা সম্ভব হয়নি। "
                "অনতিবিলম্বে পদক্ষেপ নেওয়ার পরামর্শ দেওয়া হচ্ছে।"
            )
            return warning_en, warning_bn, None, True

        # Try parsing ISO date
        try:
            # Handle YYYY-MM-DD or ISO timestamp
            dt_str = str(raw_date)[:10]
            parsed_date = datetime.date.fromisoformat(dt_str)
            today = datetime.date.today()
            elapsed_days = (today - parsed_date).days

            if elapsed_days < 0:
                # Future date anomaly
                return (
                    "Incident date is in the future. Please correct the incident date.",
                    "ঘটনার তারিখ ভবিষ্যতে দেখানো হয়েছে। অনুগ্রহ করে সঠিক তারিখ প্রদান করুন।",
                    None,
                    True,
                )

            days_remaining = max(0, statutory_limitation_days - elapsed_days)
            if elapsed_days > statutory_limitation_days:
                warning_en = (
                    f"Statutory 30-day limitation window under Section 60 has elapsed ({elapsed_days} days since incident). "
                    "A formal condonation of delay explanation will be required by DNCRP."
                )
                warning_bn = (
                    f"ভোক্তা অধিকার আইনের ৬০ ধারা অনুযায়ী ৩০ দিনের সময়সীমা পার হয়ে গেছে (ঘটনাটি {elapsed_days} দিন আগের)। "
                    "অভিযোগ দাখিলের সময় বিলম্বের যৌক্তিক কারণ ব্যাখ্যা করতে হবে।"
                )
                return warning_en, warning_bn, 0, False
            else:
                return None, None, days_remaining, False

        except (ValueError, TypeError):
            warning_en = (
                "Incident date format is uncertain; exact statutory cutoff cannot be safely verified. Prompt action advised."
            )
            warning_bn = (
                "ঘটনার তারিখের ফরম্যাট স্পষ্ট নয়; আইনি ডেডলাইন সঠিকভাবে গণনা করা যাচ্ছে না। অনতিবিলম্বে অভিযোগ দায়ের করুন।"
            )
            return warning_en, warning_bn, None, True

    @classmethod
    async def assess_case(
        cls,
        case: Case,
        db: AsyncSession,
        source_health: dict[str, str] | None = None,
        skipped_questions: set[str] | None = None,
    ) -> ProceduralAssessmentOut:
        # 1. Fetch active facts for the case
        stmt = await db.execute(select_facts(case.id))
        assertions = stmt.scalars().all()

        facts_dict = cls.extract_facts_from_db_records(assertions, case)

        # 2. Evaluate Policy Rules
        rules = cls.load_starter_rules()
        routes_out, needed_facts = cls.evaluate_all_rules(
            rules,
            facts_dict,
            desired_outcomes=case.desired_outcomes,
            source_health=source_health,
            case=case,
        )

        # 3. Determine Overall Status & Primary Action with strict priority:
        # Precedence: Urgent Safety -> Financial Provider Dispute (T20) -> E-commerce Merchant Dispute -> Clarification
        overall_status = "needs_clarification"
        primary_action = "prepare_merchant_notice"
        primary_title_en = "Prepare Formal Merchant Notice"
        primary_title_bn = "বিক্রেতার কাছে আনুষ্ঠানিক নোটিশ প্রস্তুত করুন"
        secondary_actions: list[dict[str, str]] = []

        # Check for safety hazard first (urgent priority)
        safety_routes = [r for r in routes_out if r.issue_type == "product_safety_hazard"]
        finance_routes = [r for r in routes_out if r.issue_type == "mfs_unauthorized_charge"]
        shopping_routes = [r for r in routes_out if r.issue_type in ("ecommerce_delivery_failure", "defective_goods")]
        supported_shopping = [r for r in shopping_routes if r.status == RouteStatus.SUPPORTED]

        if safety_routes and safety_routes[0].status == RouteStatus.SUPPORTED:
            overall_status = "safety_alert"
            primary_action = "call_dncrp_hotline_16121"
            primary_title_en = "Call National Consumer Rights Hotline 16121"
            primary_title_bn = "ভোক্তা অধিকার হটলাইন ১৬১২১-এ কল করুন"

        # Check for MFS / Finance route (T20 procedural hierarchy)
        elif finance_routes:
            f_route = finance_routes[0]
            if f_route.status == RouteStatus.SUPPORTED:
                # Provider ticket was filed
                overall_status = "ready_for_bb_escalation"
                primary_action = "prepare_bb_cipc_escalation"
                primary_title_en = "Escalate to Bangladesh Bank CIPC"
                primary_title_bn = "বাংলাদেশ ব্যাংক সিআইপিসিতে অভিযোগ দাখিল করুন"
            elif f_route.status == RouteStatus.NEEDS_FACTS:
                # T20: Mandatory Stage 1 provider grievance
                overall_status = "ready_for_provider_ticket"
                primary_action = "prepare_provider_formal_letter"
                primary_title_en = "Submit Formal Dispute to Provider (Stage 1)"
                primary_title_bn = "এমএফএস/ব্যাংক প্রোভাইডারে অভিযোগ দাখিল করুন (ধাপ ১)"

        # Check for E-commerce shopping route
        elif supported_shopping:
            s_route = supported_shopping[0]
            overall_status = "ready_for_merchant_notice"
            primary_action = "prepare_merchant_notice"
            primary_title_en = "Prepare Formal Merchant Notice"
            primary_title_bn = "বিক্রেতার কাছে আনুষ্ঠানিক নোটিশ প্রস্তুত করুন"
            secondary_actions.append({
                "action_id": "prepare_dncrp_complaint",
                "title_en": "Prepare DNCRP CCMS Portal Complaint",
                "title_bn": "ভোক্তা অধিকার সিসিএমএস অভিযোগ প্রস্তুত করুন",
            })
        elif shopping_routes:
            s_route = shopping_routes[0]
            if s_route.status == RouteStatus.NEEDS_FACTS:
                overall_status = "needs_clarification"

        # 4. Next Best Question Selection (T32: safety priority, no OTP/PIN, skip semantics)
        nbq: NextBestQuestion | None = None
        priority_order = ["safety", "route_disambiguation", "materiality", "readiness"]
        skips = skipped_questions or set()

        for p_level in priority_order:
            for f_key in needed_facts:
                if f_key in skips:
                    continue
                # T32: Enforce strict rejection of credential questions
                if any(cred in f_key.lower() for cred in cls.FORBIDDEN_CREDENTIAL_TERMS):
                    continue

                candidate = cls.QUESTION_CATALOGUE.get(f_key)
                if candidate and candidate.priority == p_level and candidate.question_key not in skips:
                    nbq = candidate
                    break
            if nbq:
                break

        # 5. T30 Limitation Calculation
        warn_en, warn_bn, days_rem, is_uncert = cls.calculate_statutory_limitation(
            facts_dict,
            case.incident_date,
            statutory_limitation_days=30,
        )

        # 6. Collect Source Cards
        referenced_sources = set()
        for r in routes_out:
            for src_id in r.source_dependencies:
                referenced_sources.add(src_id)

        source_cards: list[dict[str, Any]] = []
        for s_id in referenced_sources:
            entry = get_source_by_id(s_id)
            if entry:
                source_cards.append({
                    "id": entry.id,
                    "title_en": entry.title_en,
                    "title_bn": entry.title_bn,
                    "issuer": entry.issuer,
                    "official_url": entry.official_url,
                    "document_type": entry.document_type,
                    "procedural_scope": entry.procedural_scope,
                    "status": entry.status,
                    "is_authoritative_for_penalties": entry.is_authoritative_for_penalties,
                })

        return ProceduralAssessmentOut(
            case_id=case.id,
            overall_status=overall_status,
            primary_action=primary_action,
            primary_action_title_en=primary_title_en,
            primary_action_title_bn=primary_title_bn,
            secondary_actions=secondary_actions,
            routes=routes_out,
            next_best_question=nbq,
            source_cards=source_cards,
            limitation_warning_en=warn_en,
            limitation_warning_bn=warn_bn,
            days_remaining_in_limitation=days_rem,
            is_deadline_uncertain=is_uncert,
        )

    @classmethod
    async def simulate_what_if(
        cls,
        case: Case,
        overrides: dict[str, Any],
        db: AsyncSession,
        source_health: dict[str, str] | None = None,
    ) -> WhatIfSimulationResult:
        """T31 Invariant: Ephemeral simulation with ZERO persistent database side effects.

        Never commits, flushes, or modifies database rows or row versions.
        """
        # T32 Invariant Check: Overrides must NEVER contain OTP or PIN
        for k in overrides:
            if any(c in k.lower() for c in cls.FORBIDDEN_CREDENTIAL_TERMS):
                raise ValueError(f"Prohibited credential field '{k}' cannot be submitted (T32).")

        # 1. Baseline assessment
        baseline = await cls.assess_case(case, db, source_health=source_health)

        # 2. Extract facts and overlay ephemeral overrides
        stmt = await db.execute(select_facts(case.id))
        assertions = stmt.scalars().all()
        simulated_facts = cls.extract_facts_from_db_records(assertions, case)

        # Apply overrides
        simulated_facts.update(overrides)

        # 3. Evaluate rules on simulated facts
        rules = cls.load_starter_rules()
        simulated_routes, _ = cls.evaluate_all_rules(
            rules,
            simulated_facts,
            desired_outcomes=case.desired_outcomes,
            source_health=source_health,
            case=case,
        )

        # 4. Compute Route Diff
        baseline_map = {r.route_id: r.status for r in baseline.routes}
        route_diff: list[RouteDiffItem] = []
        is_material_change = False

        for sr in simulated_routes:
            b_status = baseline_map.get(sr.route_id, RouteStatus.NOT_SUPPORTED)
            changed = b_status != sr.status
            if changed:
                is_material_change = True
            route_diff.append(RouteDiffItem(
                route_id=sr.route_id,
                issue_type=sr.issue_type,
                baseline_status=b_status,
                simulated_status=sr.status,
                changed=changed,
            ))

        # Check for unreferenced/new routes
        sim_ids = {sr.route_id for sr in simulated_routes}
        for br in baseline.routes:
            if br.route_id not in sim_ids:
                is_material_change = True
                route_diff.append(RouteDiffItem(
                    route_id=br.route_id,
                    issue_type=br.issue_type,
                    baseline_status=br.status,
                    simulated_status=RouteStatus.NOT_SUPPORTED,
                    changed=True,
                ))

        if is_material_change:
            summary_en = f"Simulation produced a material route change across {sum(1 for d in route_diff if d.changed)} route(s)."
            summary_bn = f"সিমুলেশনে {sum(1 for d in route_diff if d.changed)}টি রুটে গুরুত্বপূর্ণ পরিবর্তন দেখা গেছে।"
        else:
            summary_en = "Simulation produced no material change in procedural eligibility or routing."
            summary_bn = "এই তথ্যের পরিবর্তনে মূল আইনি বা প্রক্রিয়াগত রুটে কোনো পরিবর্তন ঘটেনি।"

        return WhatIfSimulationResult(
            case_id=case.id,
            overrides=overrides,
            baseline_routes=baseline.routes,
            simulated_routes=simulated_routes,
            route_diff=route_diff,
            is_material_change=is_material_change,
            summary_en=summary_en,
            summary_bn=summary_bn,
        )


def select_facts(case_id: uuid.UUID):
    from sqlalchemy import select

    from app.facts.models import FactAssertion
    return select(FactAssertion).where(
        FactAssertion.case_id == case_id,
        FactAssertion.is_active.is_(True),
    )
