from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ComplaintDestinationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    destination_id: str
    title_en: str
    title_bn: str
    authority_name: str
    official_portal_url: str
    procedure_guide_url: str
    prerequisites_en: list[str] = Field(default_factory=list)
    prerequisites_bn: list[str] = Field(default_factory=list)
    link_health: str = "healthy"  # 'healthy', 'linked_unconfirmed', 'degraded', 'fallback_active'
    fallback_instructions_en: str
    fallback_instructions_bn: str


DESTINATION_REGISTRY: dict[str, dict[str, Any]] = {
    "dncrp_ccms_portal": {
        "destination_id": "dncrp_ccms_portal",
        "title_en": "DNCRP Central Complaint Management System (CCMS)",
        "title_bn": "ভোক্তা অধিকার সংরক্ষণ অধিদপ্তর (সিসিএমএস পোর্টাল)",
        "authority_name": "Directorate of National Consumers' Right Protection (DNCRP)",
        "official_portal_url": "https://ccms.dncrp.com/",
        "procedure_guide_url": "https://dncrp.portal.gov.bd/",
        "prerequisites_en": [
            "National ID (NID) or active mobile number for citizen authentication",
            "Money receipt, memo, or invoice showing merchant identity and date",
            "Evidence of non-delivery or product defect (screenshots/SMS)",
            "Filing must be within 30 statutory working days from incident (Section 60)",
        ],
        "prerequisites_bn": [
            "নাগরিক লগইনের জন্য জাতীয় পরিচয়পত্র (NID) বা সচল মোবাইল নম্বর",
            "ক্রয় রশিদ বা ক্যাশমেমো যাতে বিক্রেতার নাম ও তারিখ উল্লেখ রয়েছে",
            "পণ্য না পাওয়া বা ত্রুটির সুনির্দিষ্ট প্রমাণ (স্ক্রিনশট/এসএমএস)",
            "ঘটনার ৩০ কার্যদিবসের মধ্যে অভিযোগ দাখিল করতে হবে (৬০ ধারা)",
        ],
        "link_health": "healthy",
        "fallback_instructions_en": "If the online CCMS portal is undergoing maintenance, submit your complaint directly via email to ncrp@dncrp.gov.bd with attached evidence.",
        "fallback_instructions_bn": "যদি সিসিএমএস অনলাইন পোর্টালে ত্রুটি দেখা দেয়, তবে প্রমাণাদিসহ সরাসরি ncrp@dncrp.gov.bd ঠিকানায় ইমেইল পাঠিয়ে অভিযোগ করুন।",
    },
    "bb_cipc_portal": {
        "destination_id": "bb_cipc_portal",
        "title_en": "Bangladesh Bank Customer Interests Protection Centre (CIPC)",
        "title_bn": "বাংলাদেশ ব্যাংক গ্রাহক স্বার্থ সংরক্ষণ কেন্দ্র (সিআইপিসি)",
        "authority_name": "Bangladesh Bank (Payment Systems & Customer Protection)",
        "official_portal_url": "https://cms.bb.org.bd/ords/f?p=107%3A133%3A",
        "procedure_guide_url": "https://www.bb.org.bd/en/index.php/services/cipc_procedure",
        "prerequisites_en": [
            "Stage 1 formal grievance ticket reference number from MFS provider (Mandatory T20)",
            "Transaction TrxID and account statement copy",
            "Provider response SLA has elapsed without resolution",
        ],
        "prerequisites_bn": [
            "এমএফএস প্রোভাইডারের নিকট ধাপ ১ অভিযোগের টিকিট রেফারেন্স নম্বর (বাধ্যতামূলক T20)",
            "ট্রানজেকশন TrxID ও স্টেটমেন্টের কপি",
            "প্রোভাইডারের সমাধানের সময়সীমা পার হওয়া বা অসন্তোষজনক সমাধান",
        ],
        "link_health": "linked_unconfirmed",
        "fallback_instructions_en": "Target form link timed out in automated checks. Use official procedure page fallback or email cipc@bb.org.bd, or call hotline 16236.",
        "fallback_instructions_bn": "সরাসরি ফর্ম লিংকে কারিগরি সমস্যা হলে অফিসিয়াল নির্দেশিকা পেজ দেখুন অথবা cipc@bb.org.bd-এ ইমেইল পাঠান বা ১৬২৩৬ নম্বরে কল করুন।",
    },
    "dncrp_hotline_16121": {
        "destination_id": "dncrp_hotline_16121",
        "title_en": "National Consumer Rights Emergency Hotline 16121",
        "title_bn": "জাতীয় ভোক্তা অধিকার সংরক্ষণ হটলাইন ১৬১২১",
        "authority_name": "DNCRP Emergency Enforcement Cell",
        "official_portal_url": "tel:16121",
        "procedure_guide_url": "https://dncrp.portal.gov.bd/",
        "prerequisites_en": [
            "Immediate physical safety risk, explosion, fire, or chemical toxicity",
            "Keep physical sample and packaging preserved",
        ],
        "prerequisites_bn": [
            "তাৎক্ষণিক শারীরিক ঝুঁকি, অগ্নিকাণ্ড বা বিষক্রিয়ার আশঙ্কা",
            "পণ্যটির নমুনা ও মোড়ক সাবধানে সংরক্ষণ করুন",
        ],
        "link_health": "healthy",
        "fallback_instructions_en": "Alternative phone: +8802223381655",
        "fallback_instructions_bn": "বিকল্প ফোন: +৮৮০২২২৩৩৮১৬৫৫",
    },
    "btrc_consumer_cell": {
        "destination_id": "btrc_consumer_cell",
        "title_en": "BTRC Telecom Consumer Grievance Cell & Hotline 100",
        "title_bn": "বিটিআরসি গ্রাহক অভিযোগ সেল ও হটলাইন ১০০",
        "authority_name": "Bangladesh Telecommunication Regulatory Commission (BTRC)",
        "official_portal_url": "http://btrc.gov.bd/",
        "procedure_guide_url": "http://btrc.gov.bd/",
        "prerequisites_en": [
            "Prior complaint ticket number from cellular operator or ISP",
            "Unresolved dispute exceeding operator SLA period",
            "Billing statement or proof of service outage",
        ],
        "prerequisites_bn": [
            "মোবাইল অপারেটর বা আইএসপিতে পূর্বে দাখিলকৃত অভিযোগের টিকিট নম্বর",
            "নির্ধারিত সময়সীমা পার হওয়ার পরও সমাধান না হওয়া",
            "বিলিং স্টেটমেন্ট বা সেবা বিঘ্নের প্রমাণাদি",
        ],
        "link_health": "healthy",
        "fallback_instructions_en": "Call BTRC Consumer Grievance Hotline 100 or email btrc@btrc.gov.bd directly.",
        "fallback_instructions_bn": "সরাসরি বিটিআরসি হটলাইন ১০০-তে কল করুন বা btrc@btrc.gov.bd ইমেইলে যোগাযোগ করুন।",
    },
    "idra_grievance_cell": {
        "destination_id": "idra_grievance_cell",
        "title_en": "IDRA Insurance Policyholder Grievance Redress Cell",
        "title_bn": "আইডিআরএ বীমা গ্রাহক অভিযোগ প্রতিকার সেল",
        "authority_name": "Insurance Development and Regulatory Authority (IDRA)",
        "official_portal_url": "http://idra.gov.bd/",
        "procedure_guide_url": "http://idra.gov.bd/",
        "prerequisites_en": [
            "Formal claim submission proof to the insurance company",
            "Insurer denial letter or proof of settlement delay exceeding 90 days",
            "Copy of insurance policy schedule",
        ],
        "prerequisites_bn": [
            "বীমা কোম্পানির নিকট আনুষ্ঠানিক দাবি দাখিলের প্রমাণ",
            "দাবি প্রত্যাখ্যানপত্র বা ৯০ দিনের বেশি সময় ধরে নিষ্পত্তির বিলম্ব",
            "বীমা পলিসি শিডিউলের কপি",
        ],
        "link_health": "healthy",
        "fallback_instructions_en": "Submit written grievance to IDRA complaint desk or email idra.complaint@gmail.com.",
        "fallback_instructions_bn": "আইডিআরএ অভিযোগ সেলে লিখিত আবেদন জমা দিন অথবা idra.complaint@gmail.com-এ ইমেইল করুন।",
    },
    "cabinet_grs_portal": {
        "destination_id": "cabinet_grs_portal",
        "title_en": "Cabinet Division Central Grievance Redress System (GRS)",
        "title_bn": "মন্ত্রিপরিষদ বিভাগ কেন্দ্রীয় অভিযোগ প্রতিকার ব্যবস্থা (জিআরএস)",
        "authority_name": "Cabinet Division, Government of Bangladesh",
        "official_portal_url": "http://grs.gov.bd/",
        "procedure_guide_url": "http://grs.gov.bd/",
        "prerequisites_en": [
            "Public service application tracking number or receipt",
            "Citizen Charter response window has elapsed",
            "Matter must NOT be sub judice or pending before any court of law",
        ],
        "prerequisites_bn": [
            "সরকারি সেবার আবেদন ট্র্যাকিং নম্বর বা প্রাপ্তিস্বীকার পত্র",
            "সিটিজেন চার্টারের নির্ধারিত সময় অতিক্রান্ত হওয়া",
            "বিষয়টি কোনো আদালতে বিচারাধীন (সাব-জুডিস) হওয়া চলবে না",
        ],
        "link_health": "healthy",
        "fallback_instructions_en": "If portal is unreachable, file grievance in person with the departmental Grievance Redress Officer (GRO).",
        "fallback_instructions_bn": "অনলাইন পোর্টাল অনুপলব্ধ হলে সংশ্লিষ্ট দপ্তরের অভিযোগ নিষ্পত্তি কর্মকর্তার (GRO) নিকট সরাসরি আবেদন দিন।",
    },
}


class ComplaintDestinationService:
    """P09.7 & T54: Official complaint destination registry and link-health fallback."""

    @classmethod
    def get_destination(cls, destination_id: str) -> ComplaintDestinationOut:
        data = DESTINATION_REGISTRY.get(destination_id)
        if not data:
            data = DESTINATION_REGISTRY["dncrp_ccms_portal"]
        return ComplaintDestinationOut.model_validate(data)

    @classmethod
    def list_destinations(cls) -> list[ComplaintDestinationOut]:
        return [ComplaintDestinationOut.model_validate(d) for d in DESTINATION_REGISTRY.values()]

