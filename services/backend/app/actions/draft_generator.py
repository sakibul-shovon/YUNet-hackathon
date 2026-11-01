import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

FORBIDDEN_THREAT_KEYWORDS = {
    "shut down your business",
    "put you in jail",
    "ruin your reputation",
    "defame you",
    "destroy you",
    "physical harm",
    "police encounter",
    "ব্যবসা বন্ধ করে দেব",
    "জেলে ঢুকিয়ে দেব",
    "মারধর",
}

FORBIDDEN_FALSE_CLAIMS = {
    "officially filed by claimcraft",
    "dncrp has already declared you guilty",
    "court judgment already passed",
    "আদালতের রায় ঘোষণা",
}


class DraftRequestOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    document_type: str = "pre_filing_merchant_notice"
    locale: str = "en"
    subject: str
    recipient: str
    body_text: str
    citations: list[str] = Field(default_factory=list)
    lifecycle_state: str = "unsubmitted_draft"
    is_sent: bool = False
    is_filed: bool = False
    unsubmitted_banner_notice_en: str = (
        "UNSUBMITTED DRAFT — Prepared for your personal review. "
        "ClaimCraft BD does NOT send or file communications on your behalf. "
        "Copying or viewing this draft does not change external filing status."
    )
    unsubmitted_banner_notice_bn: str = (
        "অননুমোদিত খসড়া — শুধুমাত্র আপনার ব্যক্তিগত পর্যালোচনার জন্য প্রস্তুত। "
        "ক্লেমক্র্যাফট বিডি কোনো স্বয়ংক্রিয় মেসেজ বা মামলা পাঠায় না। "
        "এই খসড়া দেখা বা কপি করা মানেই এটি আনুষ্ঠানিকভাবে প্রেরিত বা দায়েরকৃত নয়।"
    )
    created_at: str


class DraftRequestGenerator:
    """T26: Generates respectful, factual pre-filing dispute drafts lacking threats, fake dates, or false filed status."""

    @classmethod
    def validate_safety_and_tone(cls, text: str) -> None:
        """T26 Guard: Validates that draft contains zero abusive threats, defamatory language, or false legal authority."""
        lower = text.lower()
        for kw in FORBIDDEN_THREAT_KEYWORDS:
            if kw in lower:
                raise ValueError(f"Draft violates safety policy: Contains aggressive threat or extortion phrase '{kw}' (T26).")
        for fc in FORBIDDEN_FALSE_CLAIMS:
            if fc in lower:
                raise ValueError(f"Draft violates safety policy: Falsely claims official filing or adjudicated guilt '{fc}' (T26).")

    @classmethod
    def generate_draft(
        cls,
        case_title: str,
        merchant_name: str | None,
        facts: dict[str, Any],
        locale: str = "en",
        remedy: str = "full_refund",
    ) -> DraftRequestOut:
        """Constructs a factual, respectful, citation-grounded pre-filing request."""
        today_str = datetime.date.today().isoformat()
        recipient = merchant_name or ("Seller / Merchant" if locale == "en" else "বিক্রেতা / মার্চেন্ট")

        amount_val = facts.get("amount_paid")
        if isinstance(amount_val, int):
            amount_str_en = f"৳ {amount_val / 100:,.2f} BDT"
            amount_str_bn = f"৳ {amount_val / 100:,.2f} টাকা"
        else:
            amount_str_en = "the paid purchase amount"
            amount_str_bn = "পরিশোধিত মূল্য"

        incident_date = facts.get("incident_date", "recent date")
        is_delivery_failure = facts.get("goods_delivered") is False
        is_defective = facts.get("goods_received_defective") is True
        is_unauthorized_mfs = facts.get("transaction_unauthorized") is True

        citations = []
        if is_unauthorized_mfs:
            if locale == "bn":
                citations = [
                    "বাংলাদেশ ব্যাংক এমএফএস নীতিমালা, ২০২২ (অভিযোগ দাখিল)",
                    "বাংলাদেশ ব্যাংক গ্রাহক স্বার্থ সংরক্ষণ কেন্দ্র (CIPC) পদ্ধতি",
                ]
            else:
                citations = [
                    "Bangladesh Bank MFS Regulations, 2022 (Dispute Reporting)",
                    "Bangladesh Bank Customer Interests Protection Centre (CIPC) Procedure",
                ]
            doc_type = "provider_dispute_letter"
            if locale == "bn":
                subject = f"অননুমোদিত লেনদেন পর্যালোচনা ও সমন্বয়ের আবেদন - {case_title}"
                body = (
                    f"তারিখ: {today_str}\n"
                    f"বরাবর: গ্রাহক সেবা বিভাগ, {recipient}\n\n"
                    f"বিষয়: অননুমোদিত লেনদেনের বিষয়ে জরুরি তদন্ত ও টাকা সমন্বয়ের আবেদন।\n\n"
                    f"জনাব,\n"
                    f"আমি বিনীতভাবে জানাচ্ছি যে, গত {incident_date} তারিখে আমার ওয়ালেট/হিসাব থেকে {amount_str_bn} "
                    f"একটি অননুমোদিত লেনদেনের মাধ্যমে কর্তন করা হয়েছে। উক্ত লেনদেনটি আমার সম্মতিক্রমে সম্পন্ন হয়নি।\n\n"
                    f"বাংলাদেশ ব্যাংকের বিধিমালা অনুযায়ী, উক্ত বিষয়ে দ্রুত তদন্তপূর্বক কর্তনকৃত অর্থ "
                    f"ফেরত প্রদানের জন্য বিনীত অনুরোধ জানাচ্ছি।\n\n"
                    f"ধন্যবাদান্তে,\n"
                    f"[আপনার নাম ও মোবাইল নম্বর]\n"
                )
            else:
                subject = f"Formal Grievance: Unauthorized Transaction Dispute - {case_title}"
                body = (
                    f"Date: {today_str}\n"
                    f"To: Customer Services Department, {recipient}\n\n"
                    f"Subject: Formal dispute and review request regarding unauthorized transaction of {amount_str_en}.\n\n"
                    f"Dear Sir/Madam,\n"
                    f"I am writing to formally report an unauthorized transaction of {amount_str_en} that occurred on {incident_date}. "
                    f"This deduction was not authorized by me.\n\n"
                    f"In accordance with Bangladesh Bank guidelines, I kindly request an official investigation "
                    f"and reversal of the disputed charge. Please provide a formal tracking ticket for this dispute.\n\n"
                    f"Sincerely,\n"
                    f"[Your Name & Contact Details]\n"
                )
        else:
            if locale == "bn":
                citations = [
                    "ভোক্তা-অধিকার সংরক্ষণ আইন, ২০০৯ (ধারা ৪৫ / ধারা ৪১)",
                    "জাতীয় ভোক্তা-অধিকার সংরক্ষণ অধিদপ্তর (DNCRP) অভিযোগ নিষ্পত্তি পদ্ধতি",
                ]
            else:
                citations = [
                    "Consumers' Right Protection Act, 2009 (Section 45 / Section 41)",
                    "Directorate of National Consumer Rights Protection (DNCRP) Procedure",
                ]
            doc_type = "pre_filing_merchant_notice"
            if is_delivery_failure:
                dispute_reason_en = "the promised goods have not been delivered despite the passing of the committed timeline"
                dispute_reason_bn = "প্রতিশ্রুত সময়সীমা অতিক্রান্ত হওয়া সত্ত্বেও পণ্যটি এখনও ডেলিভারি দেওয়া হয়নি"
            elif is_defective:
                dispute_reason_en = "the delivered goods were found defective/non-conforming upon arrival"
                dispute_reason_bn = "ডেলিভারিকৃত পণ্যটি ত্রুটিপূর্ণ ও অকার্যকর অবস্থায় পাওয়া গেছে"
            else:
                dispute_reason_en = "the contractual service commitment was not fulfilled"
                dispute_reason_bn = "চুক্তিমোতাবেক প্রতিশ্রুত সেবা প্রদান করা হয়নি"

            remedy_text_en = (
                f"a full refund of {amount_str_en}"
                if remedy == "full_refund"
                else "an immediate replacement of the product"
            )
            remedy_text_bn = (
                f"{amount_str_bn} সম্পূর্ণ মূল্য ফেরত"
                if remedy == "full_refund"
                else "দ্রুত পণ্য প্রতিস্থাপন"
            )

            if locale == "bn":
                subject = f"অর্ডার সংক্রান্ত প্রতিকারের আবেদন - {case_title}"
                body = (
                    f"তারিখ: {today_str}\n"
                    f"বরাবর: স্বত্বাধিকারী / গ্রাহক সেবা, {recipient}\n\n"
                    f"বিষয়: অর্ডার সংক্রান্ত সমস্যার শান্তিপূর্ণ সমাধান ও {remedy_text_bn}-এর আবেদন।\n\n"
                    f"জনাব,\n"
                    f"আমি আপনার প্রতিষ্ঠান থেকে {incident_date} তারিখে {amount_str_bn} মূল্যে একটি অর্ডার সম্পন্ন করেছিলাম। "
                    f"পরিতাপের বিষয় এই যে, {dispute_reason_bn}।\n\n"
                    f"ভোক্তা-অধিকার সংরক্ষণ আইন, ২০০৯-এর বিধিবিধান অনুযায়ী আমি বিষয়টি আনুষ্ঠানিকভাবে আপনার দৃষ্টিগোচর করছি এবং "
                    f"আগামী ৫ কর্মদিবসের মধ্যে {remedy_text_bn}-এর জন্য অনুরোধ জানাচ্ছি।\n\n"
                    f"আশা করি সৌহার্দ্যপূর্ণভাবে বিষয়টি নিষ্পত্তি হবে।\n\n"
                    f"বিনীত,\n"
                    f"[আপনার নাম ও মোবাইল নম্বর]\n"
                )
            else:
                subject = f"Formal Resolution Request regarding Order - {case_title}"
                body = (
                    f"Date: {today_str}\n"
                    f"To: Management / Customer Support, {recipient}\n\n"
                    f"Subject: Formal resolution request regarding {case_title} ({amount_str_en}).\n\n"
                    f"Dear Sir/Madam,\n"
                    f"I am writing regarding my purchase of {amount_str_en} completed on {incident_date}. "
                    f"Regrettably, {dispute_reason_en}.\n\n"
                    f"In the spirit of fair consumer practices and under applicable guidelines of the Consumers' Right Protection Act, 2009, "
                    f"I respectfully request {remedy_text_en} within the next 5 business days.\n\n"
                    f"I look forward to resolving this matter amicably.\n\n"
                    f"Sincerely,\n"
                    f"[Your Name & Contact Details]\n"
                )

        cls.validate_safety_and_tone(body)

        return DraftRequestOut(
            document_type=doc_type,
            locale=locale,
            subject=subject,
            recipient=recipient,
            body_text=body,
            citations=citations,
            lifecycle_state="unsubmitted_draft",
            is_sent=False,
            is_filed=False,
            created_at=datetime.datetime.now(datetime.UTC).isoformat(),
        )
