import datetime
import uuid
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.cases.models import Case
from app.facts.models import FactAssertion


class DocumentSentenceAST(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    sentence_id: str
    text: str
    statement_type: str  # 'reviewed_fact', 'user_allegation', 'statutory_basis', 'procedural_note'
    supporting_fact_id: uuid.UUID | None = None
    supporting_citation: str | None = None
    is_user_edited: bool = False


class DocumentSectionAST(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    section_id: str
    section_title_en: str
    section_title_bn: str
    sentences: list[DocumentSentenceAST]


class EditableDocumentAST(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    document_id: uuid.UUID
    case_id: uuid.UUID
    document_type: str  # 'pre_filing_merchant_notice', 'dncrp_ccms_complaint', 'bb_cipc_escalation'
    locale: str = "en"
    title: str
    counterpart_name: str
    desired_remedy: str
    sections: list[DocumentSectionAST]
    evidence_index: list[dict[str, Any]] = Field(default_factory=list)
    preparation_checklist: list[str] = Field(default_factory=list)
    unsubmitted_disclaimer_en: str = (
        "PREPARATION MATERIAL ONLY — NOT SUBMITTED BY CLAIMCRAFT BD. "
        "Review carefully and file personally via official portal or merchant contact."
    )
    unsubmitted_disclaimer_bn: str = (
        "শুধুমাত্র প্রস্তুতির খসড়া — ক্লেইমক্রাফট বিডি কর্তৃক দাখিলকৃত নয়। "
        "ব্যক্তিগতভাবে পর্যালোচনা করে স্বয়ং অফিশিয়াল পোর্টাল বা বিক্রেতার নিকট দাখিল করুন।"
    )
    lifecycle_state: str = "unsubmitted_draft"
    is_filed: bool = False
    is_sent: bool = False
    created_at: str


class DocumentEditRequest(BaseModel):
    document_type: str
    section_id: str
    sentence_id: str
    new_text: str


class DocumentASTService:
    """P09.2: Generates editable document AST with sentence-level source mapping

    and enforces T26/T29 fact vs allegation distinction.
    """

    @classmethod
    def generate_document_ast(
        cls,
        case: Case,
        facts: dict[str, Any],
        assertions: list[FactAssertion],
        evidence_items: list[Any] | None = None,
        document_type: str = "dncrp_ccms_complaint",
        locale: str = "en",
    ) -> EditableDocumentAST:
        is_bn = locale == "bn"
        merchant = case.merchant_name or ("Merchant" if not is_bn else "বিক্রেতা")
        remedy_choice = case.desired_outcomes[0] if case.desired_outcomes else "full_refund"
        sections: list[DocumentSectionAST] = []

        # Find supporting fact IDs
        fact_id_map = {a.field_name: a.id for a in assertions}

        # Domain-specific section dispatch
        if document_type == "btrc_complaint":
            sections = cls._generate_telecom_sections(case, facts, fact_id_map, is_bn)
        elif document_type == "idra_grievance":
            sections = cls._generate_insurance_sections(case, facts, fact_id_map, is_bn)
        elif document_type == "grs_submission":
            sections = cls._generate_grs_sections(case, facts, fact_id_map, is_bn)
        else:
            # Default / E-Commerce / CCMS sections
            sections = cls._generate_default_sections(case, facts, fact_id_map, is_bn)

        # Evidence Index
        ev_index = []
        if evidence_items:
            for item in evidence_items:
                ev_index.append(
                    {
                        "id": str(item.id),
                        "filename": item.original_filename,
                        "mime_type": item.declared_mime_type,
                        "status": item.status,
                    }
                )

        # Checklist
        checklist = [
            "Verify all amounts match money receipts exactly"
            if not is_bn
            else "ক্যাশমেমোর সাথে উল্লেখিত টাকার অঙ্ক হুবহু মিলিয়ে নিন",
            "Ensure screenshots contain visible date and transaction identifiers"
            if not is_bn
            else "স্ক্রিনশটে তারিখ ও ট্রানজেকশন আইডি স্পষ্টভাবে দৃশ্যমান কিনা যাচাই করুন",
            "Submit directly on the verified official portal using your personal NID/Account"
            if not is_bn
            else "সরকারি পোর্টাল বা হেল্পলাইনে নিজ দায়িত্বে ব্যক্তিগত তথ্য দিয়ে দাখিল করুন",
        ]

        return EditableDocumentAST(
            document_id=uuid.uuid4(),
            case_id=case.id,
            document_type=document_type,
            locale=locale,
            title=f"Dispute Complaint Document — {case.title}",
            counterpart_name=merchant,
            desired_remedy=remedy_choice,
            sections=sections,
            evidence_index=ev_index,
            preparation_checklist=checklist,
            created_at=datetime.date.today().isoformat(),
        )

    @classmethod
    def _generate_default_sections(
        cls,
        case: Case,
        facts: dict[str, Any],
        fact_id_map: dict[str, uuid.UUID],
        is_bn: bool,
    ) -> list[DocumentSectionAST]:
        sections: list[DocumentSectionAST] = []
        sentences_bg: list[DocumentSentenceAST] = []
        merchant = case.merchant_name or ("Merchant" if not is_bn else "বিক্রেতা")
        amt = facts.get("amount_paid")
        amt_str = (
            f"৳ {amt / 100:,.2f}"
            if isinstance(amt, int)
            else ("the purchase amount" if not is_bn else "পরিশোধিত মূল্য")
        )

        sentences_bg.append(
            DocumentSentenceAST(
                sentence_id="bg_1",
                text=(
                    f"On or around {facts.get('incident_date', 'recent date')}, I engaged in a consumer transaction with {merchant}."
                    if not is_bn
                    else f"গত {facts.get('incident_date', 'সাম্প্রতিক সময়ে')}, আমি {merchant}-এর সাথে একটি ভোক্তা লেনদেন সম্পন্ন করি।"
                ),
                statement_type="reviewed_fact" if "incident_date" in facts else "user_allegation",
                supporting_fact_id=fact_id_map.get("incident_date"),
            )
        )

        sentences_bg.append(
            DocumentSentenceAST(
                sentence_id="bg_2",
                text=(
                    f"Total consideration transferred was {amt_str} for the intended consumer goods."
                    if not is_bn
                    else f"উক্ত পণ্যের ক্রয় বাবদ সর্বমোট {amt_str} পরিশোধ করা হয়েছিল।"
                ),
                statement_type="reviewed_fact" if "amount_paid" in facts else "user_allegation",
                supporting_fact_id=fact_id_map.get("amount_paid"),
            )
        )

        sections.append(
            DocumentSectionAST(
                section_id="sec_background",
                section_title_en="1. Transaction Background & Consideration",
                section_title_bn="১. লেনদেনের পটভূমি ও পরিশোধিত মূল্য",
                sentences=sentences_bg,
            )
        )

        sentences_breach: list[DocumentSentenceAST] = []
        if facts.get("goods_delivered") is False:
            sentences_breach.append(
                DocumentSentenceAST(
                    sentence_id="br_1",
                    text=(
                        f"Despite commitment, {merchant} completely failed to deliver the ordered merchandise."
                        if not is_bn
                        else f"প্রতিশ্রুতি থাকা সত্ত্বেও, {merchant} ক্রয়কৃত পণ্যটি সরবরাহ করতে সম্পূর্ণ ব্যর্থ হয়েছে।"
                    ),
                    statement_type="reviewed_fact",
                    supporting_fact_id=fact_id_map.get("goods_delivered"),
                    supporting_citation="crpa2009:sec:45",
                )
            )
            sentences_breach.append(
                DocumentSentenceAST(
                    sentence_id="br_2",
                    text=(
                        "The promised delivery date elapsed without fulfillment or automatic refund."
                        if not is_bn
                        else "প্রতিশ্রুত ডেলিভারির মেয়াদ উত্তীর্ণ হওয়া সত্ত্বেও পণ্য বা মূল্য কোনোটিই ফেরত দেওয়া হয়নি।"
                    ),
                    statement_type="reviewed_fact",
                    supporting_fact_id=fact_id_map.get("promised_delivery_date_passed"),
                    supporting_citation="crpa2009:sec:45",
                )
            )
        elif facts.get("goods_received_defective") is True:
            sentences_breach.append(
                DocumentSentenceAST(
                    sentence_id="br_1",
                    text=(
                        f"Upon receipt, the delivered goods from {merchant} were found defective and non-functional."
                        if not is_bn
                        else "পণ্যটি হাতে পাওয়ার পর দেখা যায় এটি ত্রুটিপূর্ণ ও ব্যবহার অনুপযোগী।"
                    ),
                    statement_type="reviewed_fact",
                    supporting_fact_id=fact_id_map.get("goods_received_defective"),
                    supporting_citation="crpa2009:sec:41",
                )
            )
        elif facts.get("transaction_unauthorized") is True:
            sentences_breach.append(
                DocumentSentenceAST(
                    sentence_id="br_1",
                    text=(
                        "An unauthorized debit occurred on my financial wallet without valid customer authorization."
                        if not is_bn
                        else "আমার ওয়ালেট থেকে অননুমোদিতভাবে টাকা কেটে নেওয়া হয়েছে।"
                    ),
                    statement_type="reviewed_fact",
                    supporting_fact_id=fact_id_map.get("transaction_unauthorized"),
                    supporting_citation="bb_cipc:stage:1",
                )
            )
        else:
            sentences_breach.append(
                DocumentSentenceAST(
                    sentence_id="br_1",
                    text=(
                        f"The commercial terms agreed with {merchant} were unilaterally breached."
                        if not is_bn
                        else f"{merchant}-এর সাথে সম্মত চুক্তি শর্তাবলী লঙ্ঘিত হয়েছে।"
                    ),
                    statement_type="user_allegation",
                )
            )

        sections.append(
            DocumentSectionAST(
                section_id="sec_breach",
                section_title_en="2. Factual Chronology of Grievance",
                section_title_bn="২. অভিযোগের ঘটনাপঞ্জি ও ব্যত্যয়",
                sentences=sentences_breach,
            )
        )

        sentences_remedy: list[DocumentSentenceAST] = []
        remedy_choice = case.desired_outcomes[0] if case.desired_outcomes else "full_refund"

        if remedy_choice == "full_refund":
            remedy_text_en = f"Immediate full reimbursement of {amt_str} under Consumer Rights Protection Act, 2009."
            remedy_text_bn = f"ভোক্তা অধিকার সংরক্ষণ আইন, ২০০৯ অনুযায়ী সমুদয় {amt_str} অবিলম্বে ফেরত প্রদান।"
        elif remedy_choice == "replacement":
            remedy_text_en = (
                "Immediate replacement of defective item with a brand new conforming unit."
            )
            remedy_text_bn = "ত্রুটিপূর্ণ পণ্যের পরিবর্তে ত্রুটিমুক্ত নতুন পণ্য অবিলম্বে প্রতিস্থাপন।"
        else:
            remedy_text_en = (
                "Lawful resolution and statutory compensation as provided by governing regulations."
            )
            remedy_text_bn = "প্রযোজ্য বিধিমালা অনুযায়ী আইনানুগ প্রতিকার ও ক্ষতিপূরণ প্রদান।"

        sentences_remedy.append(
            DocumentSentenceAST(
                sentence_id="rem_1",
                text=remedy_text_en if not is_bn else remedy_text_bn,
                statement_type="statutory_basis",
                supporting_citation="crpa2009:sec:76",
            )
        )

        sections.append(
            DocumentSectionAST(
                section_id="sec_remedy",
                section_title_en="3. Lawful Relief Requested",
                section_title_bn="৩. প্রার্থিত আইনসম্মত প্রতিকার",
                sentences=sentences_remedy,
            )
        )

        return sections

    @classmethod
    def _generate_telecom_sections(
        cls,
        case: Case,
        facts: dict[str, Any],
        fact_id_map: dict[str, uuid.UUID],
        is_bn: bool,
    ) -> list[DocumentSectionAST]:
        sections: list[DocumentSectionAST] = []
        operator = case.merchant_name or (
            "Telecom Operator / ISP" if not is_bn else "টেলিকম অপারেটর / আইএসপি"
        )
        ticket_no = facts.get("provider_ticket_number", "Unspecified Ticket")

        sections.append(
            DocumentSectionAST(
                section_id="sec_telecom_bg",
                section_title_en="1. Service Account & Prior Grievance Reference",
                section_title_bn="১. সেবা অ্যাকাউন্ট ও পূর্ববর্তী অভিযোগ রেফারেন্স",
                sentences=[
                    DocumentSentenceAST(
                        sentence_id="tel_bg_1",
                        text=(
                            f"I am a registered subscriber of telecom/internet services provided by {operator}."
                            if not is_bn
                            else f"আমি {operator}-এর একজন নিবন্ধিত গ্রাহক।"
                        ),
                        statement_type="user_allegation",
                    ),
                    DocumentSentenceAST(
                        sentence_id="tel_bg_2",
                        text=(
                            f"A formal Stage 1 complaint was previously lodged with {operator} under Ticket No. {ticket_no}."
                            if not is_bn
                            else f"{operator}-এর নিকট পূর্বে ধাপ ১ অভিযোগ দাখিল করা হয়েছিল (টিকিট নম্বর: {ticket_no})।"
                        ),
                        statement_type="reviewed_fact"
                        if "provider_ticket_number" in facts
                        else "user_allegation",
                        supporting_fact_id=fact_id_map.get("provider_ticket_number"),
                        supporting_citation="btrc:consumer_grievance:stage1",
                    ),
                ],
            )
        )

        sections.append(
            DocumentSectionAST(
                section_id="sec_telecom_breach",
                section_title_en="2. Service Disruption & Regulatory SLA Expiry",
                section_title_bn="২. সেবা বিঘ্ন ও নিয়ন্ত্রক সময়সীমা অতিক্রমের বিবরণ",
                sentences=[
                    DocumentSentenceAST(
                        sentence_id="tel_br_1",
                        text=(
                            "The operator failed to rectify the documented service disruption or unexpected billing charges within the regulated resolution window."
                            if not is_bn
                            else "অপারেটর নির্ধারিত সময়সীমার মধ্যে সেবা বিঘ্ন বা অনাকাঙ্ক্ষিত বিলিং সমস্যা সমাধান করতে ব্যর্থ হয়েছে।"
                        ),
                        statement_type="reviewed_fact"
                        if "provider_response_overdue_or_unsatisfactory" in facts
                        else "user_allegation",
                        supporting_citation="btrc:directive:2021:qos",
                    ),
                ],
            )
        )

        sections.append(
            DocumentSectionAST(
                section_id="sec_telecom_prayer",
                section_title_en="3. Requested Regulatory Relief",
                section_title_bn="৩. প্রার্থিত নিয়ন্ত্রক প্রতিকার",
                sentences=[
                    DocumentSentenceAST(
                        sentence_id="tel_rem_1",
                        text=(
                            "Requesting BTRC directive for immediate service restoration, billing adjustment/credit, and QoS compliance review."
                            if not is_bn
                            else "বিটিআরসি নির্দেশিকা অনুযায়ী সেবা পুনঃসংযোগ, অতিরিক্ত বিল সমন্বয় ও সেবার মান নিশ্চিতে হস্তক্ষেপ প্রার্থনা করছি।"
                        ),
                        statement_type="statutory_basis",
                        supporting_citation="btrc:consumer_grievance:stage2",
                    ),
                ],
            )
        )

        return sections

    @classmethod
    def _generate_insurance_sections(
        cls,
        case: Case,
        facts: dict[str, Any],
        fact_id_map: dict[str, uuid.UUID],
        is_bn: bool,
    ) -> list[DocumentSectionAST]:
        sections: list[DocumentSectionAST] = []
        insurer = case.merchant_name or ("Insurance Provider" if not is_bn else "বীমা প্রতিষ্ঠান")
        claim_ref = facts.get("claim_reference", "Unspecified Claim Ref")

        sections.append(
            DocumentSectionAST(
                section_id="sec_ins_bg",
                section_title_en="1. Policyholder & Claim Submission Details",
                section_title_bn="১. পলিসি ও বীমা দাবি দাখিলের বিবরণ",
                sentences=[
                    DocumentSentenceAST(
                        sentence_id="ins_bg_1",
                        text=(
                            f"I hold a valid policy issued by {insurer} and formally submitted Claim Ref: {claim_ref}."
                            if not is_bn
                            else f"আমি {insurer}-এর একটি বৈধ পলিসিধারী এবং পূর্বে দাবি রেফারেন্স {claim_ref} দাখিল করেছি।"
                        ),
                        statement_type="reviewed_fact"
                        if "claim_reference" in facts
                        else "user_allegation",
                        supporting_fact_id=fact_id_map.get("claim_reference"),
                        supporting_citation="insurance_act_2010:sec:72",
                    ),
                ],
            )
        )

        sections.append(
            DocumentSectionAST(
                section_id="sec_ins_breach",
                section_title_en="2. Claim Delay or Unexplained Denial",
                section_title_bn="২. দাবি নিষ্পত্তিতে বিলম্ব বা কারণহীন প্রত্যাখ্যান",
                sentences=[
                    DocumentSentenceAST(
                        sentence_id="ins_br_1",
                        text=(
                            f"{insurer} has either denied the legitimate claim without justifiable statutory grounds or delayed settlement beyond regulated 90-day period."
                            if not is_bn
                            else f"{insurer} কোনো যুক্তিসঙ্গত কারণ ব্যতিরেকে দাবি প্রত্যাখ্যান করেছে বা নির্ধারিত ৯০ দিনের বেশি সময় ধরে নিষ্পত্তি ঝুলিয়ে রেখেছে।"
                        ),
                        statement_type="reviewed_fact"
                        if "claim_denied_or_settlement_delayed_over_90d" in facts
                        else "user_allegation",
                        supporting_citation="insurance_act_2010:sec:72",
                    ),
                ],
            )
        )

        sections.append(
            DocumentSectionAST(
                section_id="sec_ins_remedy",
                section_title_en="3. Reconsideration & IDRA Grievance Relief",
                section_title_bn="৩. পুনর্বিবেচনা ও আইডিআরএ সেলে প্রার্থিত প্রতিকার",
                sentences=[
                    DocumentSentenceAST(
                        sentence_id="ins_rem_1",
                        text=(
                            "Requesting formal reconsideration, comprehensive written explanation of decision, and regulatory grievance review under Insurance Act 2010."
                            if not is_bn
                            else "বীমা আইন ২০১০ অনুযায়ী দাবি পুনর্বিবেচনা, সিদ্ধান্তের লিখিত ব্যাখ্যা ও গ্রাহক সুরক্ষা সেলের তদারকি প্রার্থনা করছি।"
                        ),
                        statement_type="statutory_basis",
                        supporting_citation="idra:dispute_resolution_regulations:2019",
                    ),
                ],
            )
        )

        return sections

    @classmethod
    def _generate_grs_sections(
        cls,
        case: Case,
        facts: dict[str, Any],
        fact_id_map: dict[str, uuid.UUID],
        is_bn: bool,
    ) -> list[DocumentSectionAST]:
        sections: list[DocumentSectionAST] = []
        dept = case.merchant_name or (
            "Designated Authority" if not is_bn else "সংশ্লিষ্ট সরকারি কর্তৃপক্ষ"
        )

        sections.append(
            DocumentSectionAST(
                section_id="sec_grs_bg",
                section_title_en="1. Public Service Application & Authority",
                section_title_bn="১. সেবা আবেদন ও সংশ্লিষ্ট দপ্তরের বিবরণ",
                sentences=[
                    DocumentSentenceAST(
                        sentence_id="grs_bg_1",
                        text=(
                            f"I submitted a formal citizen application for designated public service at {dept}."
                            if not is_bn
                            else f"আমি {dept}-এ একটি নির্দিষ্ট সরকারি সেবার জন্য আনুষ্ঠানিক আবেদন দাখিল করেছি।"
                        ),
                        statement_type="user_allegation",
                        supporting_citation="cabinet_division:grs_guidelines_2015:sec:4",
                    ),
                ],
            )
        )

        sections.append(
            DocumentSectionAST(
                section_id="sec_grs_breach",
                section_title_en="2. Citizen Charter Timeframe Exceeded",
                section_title_bn="২. সিটিজেন চার্টারের সময়সীমা অতিক্রান্তের বিবরণ",
                sentences=[
                    DocumentSentenceAST(
                        sentence_id="grs_br_1",
                        text=(
                            "The statutory Citizen Charter timeframe elapsed without service delivery, progress update, or reasoned response."
                            if not is_bn
                            else "সিটিজেন চার্টারের নির্ধারিত সময়সীমা পার হওয়া সত্ত্বেও সেবা প্রদান বা কোনো যৌক্তিক কারণ জানানো হয়নি।"
                        ),
                        statement_type="user_allegation",
                    ),
                    DocumentSentenceAST(
                        sentence_id="grs_br_2",
                        text=(
                            "I formally confirm that this grievance is NOT sub judice or pending adjudication before any court of law (GRS Section 4)."
                            if not is_bn
                            else "আমি প্রত্যয়ন করছি যে এই বিষয়টি কোনো আদালত বা ট্রাইব্যুনালে বিচারাধীন নয় (জিআরএস ৪ ধারা)।"
                        ),
                        statement_type="statutory_basis",
                        supporting_citation="cabinet_division:grs_guidelines_2015:sec:4",
                    ),
                ],
            )
        )

        sections.append(
            DocumentSectionAST(
                section_id="sec_grs_remedy",
                section_title_en="3. Administrative Redress Requested",
                section_title_bn="৩. প্রার্থিত প্রশাসনিক প্রতিকার",
                sentences=[
                    DocumentSentenceAST(
                        sentence_id="grs_rem_1",
                        text=(
                            "Requesting designated Grievance Redress Officer (GRO) intervention to expedite application and provide written administrative determination."
                            if not is_bn
                            else "অভিযোগ নিষ্পত্তি কর্মকর্তা (GRO)-এর হস্তক্ষেপে সেবাটি দ্রুত নিষ্পত্তি ও প্রয়োজনীয় প্রশাসনিক ব্যবস্থা গ্রহণের অনুরোধ করছি।"
                        ),
                        statement_type="statutory_basis",
                        supporting_citation="cabinet_division:grs_guidelines_2015:sec:4",
                    ),
                ],
            )
        )

        return sections

    @classmethod
    def apply_user_edit(
        cls,
        doc: EditableDocumentAST,
        edit: DocumentEditRequest,
    ) -> EditableDocumentAST:
        """T29 Invariant: Material edits by the user are classified as user_allegation

        and do not inherit independent verified status without verification.
        """
        for sec in doc.sections:
            if sec.section_id == edit.section_id:
                for sent in sec.sentences:
                    if sent.sentence_id == edit.sentence_id:
                        sent.text = edit.new_text
                        sent.is_user_edited = True
                        # T29: User edited text is classified as user_allegation, not certified statutory fact
                        sent.statement_type = "user_allegation"
                        sent.supporting_fact_id = None
                        return doc
        return doc
