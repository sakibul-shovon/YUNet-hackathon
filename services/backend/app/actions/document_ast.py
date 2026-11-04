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
    supporting_record: dict[str, Any] | None = None
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
        "PREPARATION MATERIAL ONLY — NOT SUBMITTED BY EBARKI. "
        "Review carefully and file personally via official portal or merchant contact."
    )
    unsubmitted_disclaimer_bn: str = (
        "শুধুমাত্র প্রস্তুতির খসড়া - Ebarki কোথাও জমা দেয়নি। "
        "তথ্য মিলিয়ে প্রয়োজনমতো বদলে নিজে ব্যবহার করুন।"
    )
    lifecycle_state: str = "unsubmitted_draft"
    is_filed: bool = False
    is_sent: bool = False
    created_at: str
    case_version: int = 1
    revision: int = 1
    template_version: int = 2


class DocumentEditRequest(BaseModel):
    document_type: str
    section_id: str
    sentence_id: str
    new_text: str
    locale: str = "en"
    expected_revision: int | None = None


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
        remedy_choice = case.desired_outcomes[0] if case.desired_outcomes else "request_review"
        sections: list[DocumentSectionAST] = []

        # Find supporting fact IDs
        fact_id_map = {a.field_name: a.id for a in assertions}

        # All channels use an account-grounded preparation document. Route
        # references belong in the separate assessment, not automatic entitlements.
        sections = cls._generate_preparation_sections(case, facts, assertions, fact_id_map, is_bn)

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
            title=f"অভিযোগের প্রস্তুতি - {case.title}" if is_bn else f"Dispute preparation - {case.title}",
            counterpart_name=merchant,
            desired_remedy=remedy_choice,
            sections=sections,
            evidence_index=ev_index,
            preparation_checklist=checklist,
            created_at=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=6))).date().isoformat(),
        )

    @classmethod
    def _generate_preparation_sections(cls, case, facts, assertions, fact_id_map, is_bn):
        def text(en, bn):
            return bn if is_bn else en

        def sentence(identity, wording, field=None):
            fact = next((a for a in assertions if a.field_name == field), None)
            reviewed = fact and getattr(fact, 'review_outcome', None) in {'accepted', 'corrected'}
            return DocumentSentenceAST(sentence_id=identity, text=wording,
                statement_type='reviewed_fact' if reviewed else 'user_allegation',
                supporting_fact_id=fact_id_map.get(field))

        date = facts.get('incident_date') or case.incident_date
        amount = facts.get('amount_paid')
        date_text = text(f'The date I recorded is {date}.', f'আমার দেওয়া তারিখ: {date}।') if date else text(
            'The transaction date still needs to be confirmed.', 'লেনদেনের তারিখ এখনো নিশ্চিত করা বাকি।')
        amount_text = text(f'I report paying BDT {amount/100:,.2f}.', f'আমার বক্তব্য অনুযায়ী দেওয়া টাকা: BDT {amount/100:,.2f}।') if isinstance(amount, int) else text(
            'The payment amount still needs to be confirmed.', 'টাকার অঙ্ক এখনো নিশ্চিত করা বাকি।')
        background = [sentence('bg_1', date_text, 'incident_date'), sentence('bg_2', amount_text, 'amount_paid')]
        if case.merchant_name:
            background.append(sentence('bg_merchant', text('Merchant or provider I named: ', 'আমার দেওয়া বিক্রেতা বা সেবাদাতার নাম: ') + case.merchant_name, 'merchant_name'))
        if case.story_narrative:
            background.append(sentence('bg_3', text('My original account: ', 'আমার মূল বক্তব্য: ') + case.story_narrative))
        if facts.get('goods_delivered') is False:
            detail = text('I report that the ordered goods have not arrived.', 'আমার বক্তব্য হলো, অর্ডার করা পণ্য পাইনি।')
            field = 'goods_delivered'
        elif facts.get('goods_received_defective') is True:
            detail = text('I report a problem with the goods I received.', 'হাতে পাওয়া পণ্যে সমস্যা আছে বলে জানিয়েছি।')
            field = 'goods_received_defective'
        elif facts.get('transaction_unauthorized') is True:
            detail = text('I report a transaction that I did not authorize. Please review it.', 'আমার অনুমতি ছাড়া একটি লেনদেন হয়েছে বলে জানাচ্ছি। বিষয়টি যাচাই করার অনুরোধ করছি।')
            field = 'transaction_unauthorized'
        else:
            detail = text('Please review my account and the attached records to clarify the issue.', 'আমার বক্তব্য ও যুক্ত নথি দেখে বিষয়টি পরিষ্কার করার অনুরোধ করছি।')
            field = None
        choice = case.desired_outcomes[0] if case.desired_outcomes else None
        if choice in {'full_refund', 'refund'}:
            remedy = text('I request a refund, subject to checking the payment and any refund records.', 'টাকা দেওয়া ও ফেরতের নথি মিলিয়ে টাকা ফেরত দেওয়ার অনুরোধ করছি।')
        elif choice == 'replacement':
            remedy = text('I request a replacement. Please explain the available next step in writing.', 'পণ্য বদলে দেওয়ার অনুরোধ করছি। পরের পদক্ষেপটি লিখিতভাবে জানাবেন।')
        else:
            remedy = text('Please review my concern and explain the available resolution in writing.', 'আমার সমস্যাটি দেখে কীভাবে সমাধান করা যায় লিখিতভাবে জানানোর অনুরোধ করছি।')
        return [
            DocumentSectionAST(section_id='sec_background', section_title_en='1. My recorded account', section_title_bn='১. আমার দেওয়া তথ্য', sentences=background),
            DocumentSectionAST(section_id='sec_breach', section_title_en='2. The issue I report', section_title_bn='২. যে সমস্যাটি জানিয়েছি', sentences=[sentence('br_1', detail, field)]),
            DocumentSectionAST(section_id='sec_remedy', section_title_en='3. My request', section_title_bn='৩. আমার অনুরোধ', sentences=[sentence('rem_1', remedy)]),
        ]

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
                        sent.supporting_citation = None
                        sent.supporting_record = None
                        return doc
        return doc
