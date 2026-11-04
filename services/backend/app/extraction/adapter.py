import re
from typing import Any

from pydantic import ValidationError

from app.extraction.schemas import (
    ALLOWED_DOMAINS,
    ALLOWED_FIELD_NAMES,
    ALLOWED_FIELD_TYPES,
    ALLOWED_ISSUES,
    FactProposal,
    FactProposalSet,
    TextSpan,
)
from app.facts.normalization import (
    normalize_bd_date,
    normalize_bdt_money,
)


class CaseExtractor:
    """Bounded text extraction adapter supporting Bangla, Banglish, and English narratives (T08)."""

    @classmethod
    def find_spans_in_text(cls, narrative: str, patterns: list[str]) -> list[tuple[str, int, int]]:
        spans: list[tuple[str, int, int]] = []
        for pat in patterns:
            for match in re.finditer(pat, narrative, re.IGNORECASE):
                spans.append((match.group(0), match.start(), match.end()))
        return spans

    @classmethod
    def propose(cls, narrative: str) -> FactProposalSet:
        """Deterministically extracts structured fact proposals and links them to verbatim text spans."""
        text = narrative.strip()
        if not text:
            return FactProposalSet(
                detected_domain="consumer_ecommerce",
                detected_issue="other_consumer_dispute",
                spans=[],
                proposals=[],
            )

        spans_out: list[TextSpan] = []
        proposals_out: list[FactProposal] = []
        span_counter = 0

        # 1. Detect Domain & Issue with T19 distinction
        lower_text = text.lower()
        is_order_delivery = any(
            w in lower_text
            for w in (
                "order",
                "অর্ডার",
                "delivery",
                "ডেলিভারি",
                "daraz",
                "দারাজ",
                "evaly",
                "ইভ্যালি",
                "chaldal",
                "চালডাল",
                "পণ্য",
                "product",
                "মার্চেন্ট",
                "বিক্রেতা",
                "দোকান",
            )
        )
        is_unauthorized_mfs = any(
            w in lower_text
            for w in (
                "unauthorized",
                "টাকা কাটা",
                "টাকা কেটে",
                "কাটা গেছে",
                "হ্যাক",
                "fraud",
                "scam",
                "না জানিয়ে কাটা",
                "অননুমোদিত",
            )
        )
        is_defective = any(
            w in lower_text
            for w in ("নষ্ট", "ভাঙা", "ত্রুটিপূর্ণ", "defective", "damaged", "broken", "faulty")
        )
        is_hazard = any(
            w in lower_text
            for w in ("বিষাক্ত", "কেমিক্যাল", "বিপজ্জনক", "poison", "toxic", "hazard", "fire", "danger")
        )
        is_telecom = any(
            w in lower_text
            for w in (
                "grameenphone",
                "gp",
                "robi",
                "banglalink",
                "teletalk",
                "broadband",
                "isp",
                "sim",
                "telecom",
                "টেলিকম",
                "ইন্টারনেট",
                "সিম",
                "নেটওয়ার্ক",
                "কলড্রপ",
            )
        )
        is_insurance = any(
            w in lower_text
            for w in (
                "insurance",
                "বীমা",
                "বিমা",
                "idra",
                "policy",
                "পলিসি",
                "claim",
                "প্রিমিয়াম",
                "premium",
            )
        )
        is_grs = any(
            w in lower_text
            for w in (
                "grs",
                "জিআরএস",
                "সরকারি সেবা",
                "সিটিজেন চার্টার",
                "citizen charter",
                "পাসপোর্ট অফিস",
                "মন্ত্রণালয়",
            )
        )

        if is_hazard:
            detected_domain = "product_safety"
            detected_issue = "product_safety_hazard"
        elif is_telecom:
            detected_domain = "telecom_isp"
            detected_issue = "telecom_billing_and_outage"
        elif is_insurance:
            detected_domain = "insurance"
            detected_issue = "insurance_claim_dispute"
        elif is_grs:
            detected_domain = "government_grs"
            detected_issue = "public_service_grievance"
        elif is_unauthorized_mfs or (
            not is_order_delivery
            and any(
                w in lower_text for w in ("bkash", "বিকাশ", "nagad", "নগদ", "rocket", "রকেট", "bank")
            )
        ):
            detected_domain = "financial_services"
            detected_issue = "mfs_unauthorized_charge"
        elif is_defective:
            detected_domain = "consumer_ecommerce"
            detected_issue = "defective_goods"
        else:
            detected_domain = "consumer_ecommerce"
            detected_issue = "ecommerce_delivery_failure"

        # 2. Extract Merchant Name
        if detected_domain == "financial_services":
            merchant_patterns = [
                r"\b(?:bkash|বিকাশ|nagad|নগদ|rocket|রকেট|upay|উপায়|bank)\b",
            ]
        else:
            merchant_patterns = [
                r"\b(?:daraz|দারাজ|chaldal|চালডাল|evaly|ইভ্যালি|rokomari|রকমারি|aarong|আড়ং|shwapno|স্বপ্ন)\b",
                r"(?:from|থেকে)\s+([A-Za-z0-9\u0980-\u09FF\s]{2,20})(?:\s+(?:online|shop|theke|thek))?",
            ]
        for pat in merchant_patterns:
            m = re.search(pat, text, re.IGNORECASE)
            if m:
                matched_str = m.group(1) if m.groups() else m.group(0)
                matched_str = matched_str.strip()
                span_id = f"span_{span_counter}"
                span_counter += 1
                spans_out.append(
                    TextSpan(
                        span_id=span_id,
                        text=matched_str,
                        start_offset=m.start(),
                        end_offset=m.end(),
                    )
                )
                proposals_out.append(
                    FactProposal(
                        field_name="merchant_name",
                        field_type="string",
                        raw_value=matched_str,
                        original_text=matched_str,
                        span_ids=[span_id],
                        confidence=0.95,
                    )
                )
                break

        # 2b. Extract Payment Instrument if present
        mfs_pat = r"(?:bkash|বিকাশ|nagad|নগদ|rocket|রকেট|upay|উপায়)"
        m_mfs = re.search(mfs_pat, text, re.IGNORECASE)
        if m_mfs:
            matched_str = m_mfs.group(0).strip()
            span_id = f"span_{span_counter}"
            span_counter += 1
            spans_out.append(
                TextSpan(
                    span_id=span_id,
                    text=matched_str,
                    start_offset=m_mfs.start(),
                    end_offset=m_mfs.end(),
                )
            )
            proposals_out.append(
                FactProposal(
                    field_name="payment_instrument_kind",
                    field_type="string",
                    raw_value="mfs_wallet",
                    original_text=matched_str,
                    span_ids=[span_id],
                    confidence=0.95,
                )
            )

        # 3. Extract Amount Paid
        amount_patterns = [
            r"[৳]\s*[\d,০-৯]+(?:\.[\d০-৯]+)?",
            r"[\d,০-৯]+(?:\.[\d০-৯]+)?\s*(?:টাকা|টাকার|tk\.?|bdt)",
            r"(?:tk\.?|bdt)\s*[\d,০-৯]+(?:\.[\d০-৯]+)?",
        ]
        for pat in amount_patterns:
            m = re.search(pat, text, re.IGNORECASE)
            if m:
                matched_str = m.group(0).strip()
                span_id = f"span_{span_counter}"
                span_counter += 1
                spans_out.append(
                    TextSpan(
                        span_id=span_id,
                        text=matched_str,
                        start_offset=m.start(),
                        end_offset=m.end(),
                    )
                )
                try:
                    norm_money = normalize_bdt_money(matched_str)
                    proposals_out.append(
                        FactProposal(
                            field_name="amount_paid",
                            field_type="money",
                            raw_value=norm_money.minor_units,
                            original_text=matched_str,
                            span_ids=[span_id],
                            confidence=0.98,
                        )
                    )
                except (ValueError, TypeError, ValidationError):
                    pass
                break

        # 4. Extract Date / Incident Date
        date_patterns = [
            r"(?<![\d০-৯])[\d০-৯]{4}-[\d০-৯]{2}-[\d০-৯]{2}(?![\d০-৯])",
            r"[\d০-৯]{1,2}[-/.]\s*[\d০-৯]{1,2}[-/.]\s*[\d০-৯]{4}",
            r"[\d০-৯]{1,2}\s+(?:জানুয়ারি|ফেব্রুয়ারি|মার্চ|এপ্রিল|মে|জুন|জুলাই|আগস্ট|সেপ্টেম্বর|অক্টোবর|নভেম্বর|ডিসেম্বর|january|february|march|april|may|june|july|august|september|october|november|december)\s+[\d০-৯]{4}",
        ]
        for pat in date_patterns:
            m = re.search(pat, text, re.IGNORECASE)
            if m:
                matched_str = m.group(0).strip()
                span_id = f"span_{span_counter}"
                span_counter += 1
                spans_out.append(
                    TextSpan(
                        span_id=span_id,
                        text=matched_str,
                        start_offset=m.start(),
                        end_offset=m.end(),
                    )
                )
                try:
                    norm_date = normalize_bd_date(matched_str)
                    proposals_out.append(
                        FactProposal(
                            field_name="incident_date",
                            field_type="date",
                            raw_value=norm_date.date,
                            original_text=matched_str,
                            span_ids=[span_id],
                            confidence=0.90,
                        )
                    )
                except (ValueError, TypeError, ValidationError):
                    pass
                break

        # 5. Extract Delivery / Defect Status
        delivery_failure_pat = r"(?:(?:ডেলিভারি|পণ্য|অর্ডার|পার্সেল)(?:টি|টা)?\s*পাইনি|(?:ডেলিভারি|পণ্য|অর্ডার|পার্সেল)(?:টি|টা)?\s*পাই\s*নাই|পাইনি|পাই\s*নাই|not\s*delivered|never\s*received|didn'?t\s*receive|failed\s*to\s*deliver|delivery\s*pai\s*nai)"
        m_del = re.search(delivery_failure_pat, text, re.IGNORECASE)
        if m_del:
            matched_str = m_del.group(0).strip()
            span_id = f"span_{span_counter}"
            span_counter += 1
            spans_out.append(
                TextSpan(
                    span_id=span_id,
                    text=matched_str,
                    start_offset=m_del.start(),
                    end_offset=m_del.end(),
                )
            )
            proposals_out.append(
                FactProposal(
                    field_name="goods_delivered",
                    field_type="boolean",
                    raw_value=False,
                    original_text=matched_str,
                    span_ids=[span_id],
                    confidence=0.99,
                )
            )
            proposals_out.append(
                FactProposal(
                    field_name="purchase_channel",
                    field_type="string",
                    raw_value="ecommerce",
                    original_text=matched_str,
                    span_ids=[span_id],
                    confidence=0.95,
                )
            )

        defect_pat = r"(?:নষ্ট|ভাঙা|ত্রুটিপূর্ণ|defective|damaged|broken|faulty)"
        m_def = re.search(defect_pat, text, re.IGNORECASE)
        if m_def:
            matched_str = m_def.group(0).strip()
            span_id = f"span_{span_counter}"
            span_counter += 1
            spans_out.append(
                TextSpan(
                    span_id=span_id,
                    text=matched_str,
                    start_offset=m_def.start(),
                    end_offset=m_def.end(),
                )
            )
            proposals_out.append(
                FactProposal(
                    field_name="goods_received_defective",
                    field_type="boolean",
                    raw_value=True,
                    original_text=matched_str,
                    span_ids=[span_id],
                    confidence=0.95,
                )
            )

        return FactProposalSet(
            detected_domain=detected_domain,
            detected_issue=detected_issue,
            spans=spans_out,
            proposals=proposals_out,
        )

    @classmethod
    def repair_and_validate(
        cls, raw_payload: dict[str, Any], allowed_spans: list[TextSpan]
    ) -> FactProposalSet:
        """T08: Performs bounded schema repair on unvalidated model/LLM outputs.

        - Rejects foreign span IDs.
        - Drops unrecognized fields and invalid enums.
        - Strips unexpected extra fields.
        - Falls back to manual entry safely if schema is irreparable.
        """
        valid_span_ids = {s.span_id for s in allowed_spans}

        domain = raw_payload.get("detected_domain")
        if domain not in ALLOWED_DOMAINS:
            domain = "consumer_ecommerce"

        issue = raw_payload.get("detected_issue")
        if issue not in ALLOWED_ISSUES:
            issue = "ecommerce_delivery_failure"

        repaired_proposals: list[FactProposal] = []
        raw_proposals = raw_payload.get("proposals", [])
        if isinstance(raw_proposals, list):
            for p in raw_proposals:
                if not isinstance(p, dict):
                    continue

                field_name = p.get("field_name")
                if field_name not in ALLOWED_FIELD_NAMES:
                    continue  # Drop unknown field (T08)

                field_type = p.get("field_type")
                if field_type not in ALLOWED_FIELD_TYPES:
                    continue  # Drop invalid field type enum (T08)

                raw_val = p.get("raw_value")
                orig_text = str(p.get("original_text", raw_val))

                # Filter span IDs to strictly authorized set
                span_ids = [s for s in p.get("span_ids", []) if s in valid_span_ids]

                try:
                    fp = FactProposal(
                        field_name=field_name,
                        field_type=field_type,
                        raw_value=raw_val,
                        original_text=orig_text,
                        span_ids=span_ids,
                        confidence=float(p.get("confidence", 0.8)),
                        uncertainty_rationale=p.get("uncertainty_rationale"),
                    )
                    repaired_proposals.append(fp)
                except (ValueError, TypeError, ValidationError):
                    continue

        return FactProposalSet(
            detected_domain=domain,
            detected_issue=issue,
            spans=allowed_spans,
            proposals=repaired_proposals,
        )
