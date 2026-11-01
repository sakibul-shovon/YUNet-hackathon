import uuid
from typing import Any, ClassVar

from pydantic import BaseModel, ConfigDict
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


class ProceduralAssessmentEngine:
    """Deterministic policy assessment engine enforcing T19 (merchant vs provider distinction) and T20 (procedural hierarchy)."""

    # Static Question Catalogue for Next Best Questions (NBQ)
    QUESTION_CATALOGUE: ClassVar[dict[str, NextBestQuestion]] = {
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
        "provider_ticket_filed": NextBestQuestion(
            question_key="nbq_provider_ticket_filed",
            fact_field="provider_ticket_filed",
            prompt_en="Have you already filed a formal complaint with your MFS/bank provider and received a ticket number?",
            prompt_bn="আপনি কি বিকাশ/নগদ/ব্যাংকের হেল্পলাইনে অভিযোগ দায়ের করে কোনো ট্র্যাকিং টিকিট নম্বর পেয়েছেন?",
            question_type="boolean",
            priority="readiness",
            relevance_rationale="Bangladesh Bank CIPC regulations strictly mandate provider-level grievance before central bank escalation (T20).",
        ),
        "product_presents_immediate_hazard": NextBestQuestion(
            question_key="nbq_product_hazard",
            fact_field="product_presents_immediate_hazard",
            prompt_en="Does this product pose an immediate physical danger, chemical toxicity, or fire hazard?",
            prompt_bn="পণ্যটি কি তাৎক্ষণিক শারীরিক বিপদ, রাসায়নিক বিষক্রিয়া বা অগ্নিকাণ্ডের ঝুঁকি তৈরি করছে?",
            question_type="boolean",
            priority="safety",
            relevance_rationale="Emergency product hazards trigger immediate 16121 hotline escalation.",
        ),
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
            for yf in packs_dir.rglob("*.yaml"):
                with open(yf, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                rules.append(PolicyRule.model_validate(data))
        return rules

    @classmethod
    async def assess_case(
        cls,
        case: Case,
        db: AsyncSession,
    ) -> ProceduralAssessmentOut:
        # 1. Fetch active facts for the case
        stmt = (
            await db.execute(
                select_facts(case.id)
            )
        )
        assertions = stmt.scalars().all()

        facts_dict: dict[str, Any] = {}
        for a in assertions:
            # Unwrap typed values
            if a.field_type == "money" and isinstance(a.typed_value, dict):
                facts_dict[a.field_name] = a.typed_value.get("minor_units")
            elif a.field_type == "date" and isinstance(a.typed_value, dict):
                facts_dict[a.field_name] = a.typed_value.get("date")
            else:
                facts_dict[a.field_name] = a.typed_value

        # Infer merchant/channel if missing
        if "purchase_channel" not in facts_dict and case.merchant_name:
            facts_dict["purchase_channel"] = "ecommerce"

        # 2. Evaluate Policy Rules
        rules = cls.load_starter_rules()
        routes_out: list[AssessmentRouteOut] = []
        needed_facts: set[str] = set()

        for rule in rules:
            # T19 Guard: If it's an MFS/bank rule, only evaluate if alleged provider fault or unauthorized transaction is present
            if rule.issue_type == "mfs_unauthorized_charge":
                # T19: Payment instrument mention alone (e.g. paying via bKash for Daraz goods)
                # does NOT create a provider complaint. Only provider conduct does.
                is_unauthorized = facts_dict.get("transaction_unauthorized") is True
                provider_conduct = facts_dict.get("alleged_provider_service_failure") is True
                if not (is_unauthorized or provider_conduct):
                    continue

            eval_res = PolicyEvaluator.evaluate(rule, facts_dict)

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

            # Only consider unknown facts as candidates if the route is an active hypothesis (has at least one satisfied condition)
            if has_any_true_condition and eval_res.status == RouteStatus.NEEDS_FACTS:
                for uf in route_unknown_facts:
                    needed_facts.add(uf)

            routes_out.append(AssessmentRouteOut(
                route_id=f"route_{rule.rule_id}",
                rule_id=rule.rule_id,
                issue_type=rule.issue_type,
                status=eval_res.status,
                reasons=eval_res.reasons,
                allowed_actions=eval_res.allowed_actions,
                source_dependencies=rule.source_dependencies,
                condition_trace=trace_dicts,
            ))

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

        # 4. Next Best Question Selection (Section 12.6)
        nbq: NextBestQuestion | None = None
        # Rank by: safety -> route disambiguation -> materiality -> readiness
        priority_order = ["safety", "route_disambiguation", "materiality", "readiness"]
        for p_level in priority_order:
            for f_key in needed_facts:
                candidate = cls.QUESTION_CATALOGUE.get(f_key)
                if candidate and candidate.priority == p_level:
                    nbq = candidate
                    break
            if nbq:
                break

        # 5. Collect Source Cards
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
        )


def select_facts(case_id: uuid.UUID):
    from sqlalchemy import select

    from app.facts.models import FactAssertion
    return select(FactAssertion).where(
        FactAssertion.case_id == case_id,
        FactAssertion.is_active.is_(True),
    )
