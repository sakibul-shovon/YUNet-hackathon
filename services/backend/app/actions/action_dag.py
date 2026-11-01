import uuid

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.facts.models import FactAssertion
from app.facts.service import FactService
from app.identity.models import Principal
from app.policy.engine import ProceduralAssessmentEngine, RouteStatus


class ActionNode(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    action_id: str
    title_en: str
    title_bn: str
    description_en: str
    description_bn: str
    action_type: str  # 'merchant_contact', 'official_portal', 'hotline', 'evidence_prep', 'provider_dispute'
    status: str  # 'ready', 'blocked', 'optional', 'completed'
    blocking_reasons: list[str] = Field(default_factory=list)
    prerequisite_actions: list[str] = Field(default_factory=list)
    destination_id: str | None = None
    is_primary: bool = False
    is_mandatory: bool = True


class ActionDAGOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    case_id: uuid.UUID
    primary_action_id: str
    nodes: list[ActionNode]
    stage_hierarchy_explanation_en: str
    stage_hierarchy_explanation_bn: str


class ActionDAGService:
    """P09.1: Remedy/stage-aware action DAG generator enforcing:

    - Dependency resolution: blocked actions explain why they are blocked.
    - Non-forced optional seller messages: seller notice is NOT universally mandatory for official DNCRP complaints.
    - Mandatory Stage 1 provider grievance before Central Bank escalation (T20).
    """

    @classmethod
    async def build_action_dag(
        cls,
        case_id: uuid.UUID,
        principal: Principal,
        db: AsyncSession,
    ) -> ActionDAGOut:
        case = await FactService.get_authorized_case(case_id, principal, db)

        # 1. Fetch facts
        stmt = select(FactAssertion).where(
            FactAssertion.case_id == case.id,
            FactAssertion.is_active.is_(True),
        )
        res = await db.execute(stmt)
        assertions = res.scalars().all()
        facts = ProceduralAssessmentEngine.extract_facts_from_db_records(assertions, case)

        # 2. Get baseline assessment
        assessment = await ProceduralAssessmentEngine.assess_case(case, db)

        # Inspect route types
        has_safety = any(r.issue_type == "product_safety_hazard" and r.status == RouteStatus.SUPPORTED for r in assessment.routes)
        has_finance = any(r.issue_type == "mfs_unauthorized_charge" for r in assessment.routes)
        finance_route = next((r for r in assessment.routes if r.issue_type == "mfs_unauthorized_charge"), None)

        nodes: list[ActionNode] = []

        # Case 1: Urgent Safety
        if has_safety:
            nodes.append(ActionNode(
                action_id="call_dncrp_hotline_16121",
                title_en="Call National Consumer Rights Hotline 16121",
                title_bn="ভোক্তা অধিকার সংরক্ষণ অধিদপ্তর হটলাইন ১৬১২১-এ কল করুন",
                description_en="Urgent safety hazard detected. Immediately report hazardous product to DNCRP emergency hotline.",
                description_bn="জরুরি নিরাপত্তা ঝুঁকি শনাক্ত হয়েছে। অবিলম্বে ১৬১২১ নম্বরে ফোন করে বিপজ্জনক পণ্যের তথ্য জানান।",
                action_type="hotline",
                status="ready",
                is_primary=True,
                is_mandatory=True,
                destination_id="dncrp_hotline_16121",
            ))
            nodes.append(ActionNode(
                action_id="preserve_hazardous_sample",
                title_en="Preserve Physical Evidence & Hazardous Product Sample",
                title_bn="শারীরিক প্রমাণ ও বিপজ্জনক পণ্যের নমুনা সংরক্ষণ করুন",
                description_en="Do not discard the item. Safely store packaging, batch numbers, and receipts in sealed container.",
                description_bn="পণ্যটি ফেলে দেবেন না। মোড়ক, ব্যাচ নম্বর ও ক্যাশমেমো সাবধানে সংরক্ষণ করুন।",
                action_type="evidence_prep",
                status="ready",
                is_primary=False,
                is_mandatory=True,
            ))
            return ActionDAGOut(
                case_id=case.id,
                primary_action_id="call_dncrp_hotline_16121",
                nodes=nodes,
                stage_hierarchy_explanation_en="Urgent safety hazard takes absolute precedence over all ordinary commercial dispute steps.",
                stage_hierarchy_explanation_bn="জরুরি স্বাস্থ্য বা শারীরিক ঝুঁকির ক্ষেত্রে তাৎক্ষণিক হটলাইন যোগাযোগ সর্বাগ্রে প্রযোজ্য।",
            )

        # Case 2: Financial MFS/Bank Dispute (T20 Stage Hierarchy)
        if has_finance and finance_route:
            is_ticket_filed = facts.get("provider_ticket_filed") is True

            # Stage 1: Provider Grievance (Mandatory)
            nodes.append(ActionNode(
                action_id="prepare_provider_formal_letter",
                title_en="Submit Formal Dispute Letter to MFS/Bank Provider (Stage 1)",
                title_bn="এমএফএস/ব্যাংক প্রোভাইডারে আনুষ্ঠানিক অভিযোগ দাখিল করুন (ধাপ ১)",
                description_en="Mandatory Stage 1 under Bangladesh Bank guidelines. Submit formal notice and obtain ticket number.",
                description_bn="বাংলাদেশ ব্যাংক নির্দেশিকা অনুযায়ী ধাপ ১ বাধ্যতামূলক। প্রোভাইডারে অভিযোগ দাখিল করে টিকিট নম্বর নিন।",
                action_type="provider_dispute",
                status="completed" if is_ticket_filed else "ready",
                is_primary=not is_ticket_filed,
                is_mandatory=True,
                destination_id="mfs_provider_channel",
            ))

            # Stage 2: Central Bank CIPC Escalation (Blocked if Stage 1 ticket not filed)
            stage2_blocked = not is_ticket_filed
            blocking_reasons = []
            if stage2_blocked:
                blocking_reasons.append(
                    "Bangladesh Bank CIPC regulations require you to first file a formal grievance with the provider "
                    "and receive a tracking ticket number before Central Bank escalation (T20)."
                )

            nodes.append(ActionNode(
                action_id="prepare_bb_cipc_escalation",
                title_en="Escalate to Bangladesh Bank CIPC Portal (Stage 2)",
                title_bn="বাংলাদেশ ব্যাংক সিআইপিসি পোর্টালে অভিযোগ দাখিল করুন (ধাপ ২)",
                description_en="Official regulatory grievance portal for unresolved financial transactions.",
                description_bn="অমীমাংসিত আর্থিক বিরোধের ক্ষেত্রে বাংলাদেশ ব্যাংকের কেন্দ্রীয় অভিযোগ ব্যবস্থাপনা পোর্টাল।",
                action_type="official_portal",
                status="blocked" if stage2_blocked else "ready",
                blocking_reasons=blocking_reasons,
                prerequisite_actions=["prepare_provider_formal_letter"],
                is_primary=is_ticket_filed,
                is_mandatory=True,
                destination_id="bb_cipc_portal",
            ))

            return ActionDAGOut(
                case_id=case.id,
                primary_action_id="prepare_bb_cipc_escalation" if is_ticket_filed else "prepare_provider_formal_letter",
                nodes=nodes,
                stage_hierarchy_explanation_en="Financial disputes strictly enforce two-stage escalation: Provider Grievance (Stage 1) -> BB CIPC (Stage 2).",
                stage_hierarchy_explanation_bn="আর্থিক বিরোধের ক্ষেত্রে দুই ধাপের শৃঙ্খলা প্রযোজ্য: প্রোভাইডার গ্রিভেন্স (ধাপ ১) -> বাংলাদেশ ব্যাংক সিআইপিসি (ধাপ ২)।",
            )

        # Case 3: E-Commerce / Consumer Goods (DNCRP CCMS & Optional Merchant Notice)
        # P09.1 Invariant: Seller notice is OPTIONAL, not universally forced!
        nodes.append(ActionNode(
            action_id="prepare_merchant_notice",
            title_en="Send Pre-Filing Dispute Notice to Merchant",
            title_bn="বিক্রেতাকে প্রাক-অভিযোগ বিরোধ নোটিশ পাঠান",
            description_en="Optional private resolution request. Gives merchant final opportunity to fulfill or refund before official complaint.",
            description_bn="ঐচ্ছিক ব্যক্তিগত নিষ্পত্তির সুযোগ। অফিশিয়াল অভিযোগ দায়েরের পূর্বে বিক্রেতাকে সমাধানের সুযোগ দেয়।",
            action_type="merchant_contact",
            status="optional",
            is_primary=False,
            is_mandatory=False,  # NOT universally forced!
        ))

        # DNCRP CCMS Complaint is ready immediately; not blocked by seller notice
        nodes.append(ActionNode(
            action_id="prepare_dncrp_complaint",
            title_en="File Official Complaint on DNCRP CCMS Portal",
            title_bn="ভোক্তা অধিকার সংরক্ষণ অধিদপ্তর সিসিএমএস পোর্টালে অভিযোগ দাখিল করুন",
            description_en="Official statutory complaint under Consumer Rights Protection Act, 2009 (Sections 45 & 76).",
            description_bn="ভোক্তা অধিকার সংরক্ষণ আইন, ২০০৯ (ধারা ৪৫ ও ৭৬) এর অধীনে সরকারি সিসিএমএস পোর্টালে সরাসরি অভিযোগ।",
            action_type="official_portal",
            status="ready",
            is_primary=True,
            is_mandatory=True,
            destination_id="dncrp_ccms_portal",
        ))

        return ActionDAGOut(
            case_id=case.id,
            primary_action_id="prepare_dncrp_complaint",
            nodes=nodes,
            stage_hierarchy_explanation_en="Consumer complaints under CRPA 2009 can be filed directly on DNCRP CCMS; private seller notice is optional.",
            stage_hierarchy_explanation_bn="ভোক্তা অধিকার আইনে সরাসরি সিসিএমএস পোর্টালে অভিযোগ দাখিল করা যায়; বিক্রেতাকে নোটিশ পাঠানো ঐচ্ছিক।",
        )

