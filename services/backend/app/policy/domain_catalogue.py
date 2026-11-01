from typing import Any

from pydantic import BaseModel


class DomainCapabilityEntry(BaseModel):
    domain_id: str
    title_en: str
    title_bn: str
    support_status: str  # 'fully_supported', 'staged_depth', 'secondary_civic', 'unsupported'
    support_depth: str
    disclosed_routes: list[str]
    statutory_basis: str
    is_fully_supported: bool
    caveat_en: str | None = None
    caveat_bn: str | None = None


class DomainCatalogueResponse(BaseModel):
    jurisdiction: str = "BD"
    domains: list[DomainCapabilityEntry]
    disclaimer_en: str = (
        "ClaimCraft BD discloses exact supported depths for each domain. "
        "Unapproved or experimental domains are never advertised as fully supported."
    )
    disclaimer_bn: str = (
        "ক্লেইমক্রাফট বিডি প্রতিটি ডোমেইনের অনুমোদিত সক্ষমতার মাত্রা স্বচ্ছভাবে প্রকাশ করে। "
        "অননুমোদিত কোনো ডোমেইনকে সম্পূর্ণ সমর্থিত হিসেবে উপস্থাপন করা হয় না।"
    )


DOMAIN_CATALOGUE: list[DomainCapabilityEntry] = [
    DomainCapabilityEntry(
        domain_id="consumer_ecommerce",
        title_en="Retail Goods & E-Commerce",
        title_bn="খুচরা পণ্য ও ই-কমার্স",
        support_status="fully_supported",
        support_depth="end_to_end",
        is_fully_supported=True,
        disclosed_routes=["seller_notice", "dncrp_ccms_portal", "dncrp_hotline_16121"],
        statutory_basis="Consumer Rights Protection Act, 2009 (Act No. 26 of 2009)",
    ),
    DomainCapabilityEntry(
        domain_id="financial_services",
        title_en="Banking & Mobile Financial Services (MFS)",
        title_bn="ব্যাংকিং ও মোবাইল ফিন্যান্সিয়াল সার্ভিস (এমএফএস)",
        support_status="fully_supported",
        support_depth="end_to_end",
        is_fully_supported=True,
        disclosed_routes=["provider_ticket", "provider_formal_letter", "bb_cipc_escalation"],
        statutory_basis="Bangladesh Bank CIPC Framework & MFS Regulations 2022",
    ),
    DomainCapabilityEntry(
        domain_id="telecom_isp",
        title_en="Telecom & Internet Service Providers (ISP)",
        title_bn="টেলিকম ও ইন্টারনেট সার্ভিস প্রোভাইডার (আইএসপি)",
        support_status="fully_supported",
        support_depth="provider_and_btrc",
        is_fully_supported=True,
        disclosed_routes=["telecom_provider_notice", "btrc_complaint"],
        statutory_basis="BTRC Telecom Quality of Service Directives & Consumer Grievance System",
    ),
    DomainCapabilityEntry(
        domain_id="insurance",
        title_en="Insurance Claim Disputes",
        title_bn="বীমা দাবি সংক্রান্ত বিরোধ",
        support_status="staged_depth",
        support_depth="explanation_and_idra_guidance",
        is_fully_supported=False,
        disclosed_routes=["insurer_reconsideration_request", "idra_grievance"],
        statutory_basis="Insurance Act, 2010 (Act No. 13 of 2010) & IDRA Regulations",
        caveat_en="ClaimCraft BD provides explanation of regulated grievance steps and denial reasons. It does not assess actuarial underwriting or guarantee claim payout.",
        caveat_bn="ক্লেইমক্রাফট বিডি আইনি অভিযোগ ও প্রত্যাখ্যাত হওয়ার কারণ বিশ্লেষণে সহায়তা করে। এটি কোনো অ্যাকচুয়ারিয়াল বা বীমা দাবির নিশ্চয়তা দেয় না।",
    ),
    DomainCapabilityEntry(
        domain_id="government_grs",
        title_en="Government Grievance Redress System (GRS)",
        title_bn="সরকারি অভিযোগ প্রতিকার ব্যবস্থা (জিআরএস)",
        support_status="secondary_civic",
        support_depth="administrative_grievance",
        is_fully_supported=False,
        disclosed_routes=["departmental_grievance", "grs_submission"],
        statutory_basis="Cabinet Division GRS Guidelines 2015",
        caveat_en="Secondary civic track for public service delays. Strictly excludes sub judice court matters, land title litigations, and service cadre discipline.",
        caveat_bn="পাবলিক সার্ভিস সংক্রান্ত অভিযোগের সহায়ক ট্র্যাক। বিচারাধীন আদালত মামলা, জমির স্বত্ব বিরোধ বা সার্ভিস ক্যাডার শৃঙ্খলা এর আওতাভুক্ত নয়।",
    ),
]


class DomainCatalogueService:
    """P12.4: Domain capability catalogue, disclosures, and unsupported-jurisdiction fallback."""

    @classmethod
    def get_catalogue(cls, jurisdiction: str = "BD") -> DomainCatalogueResponse:
        """Returns catalogue of verified domain packs and disclosed support depths."""
        return DomainCatalogueResponse(
            jurisdiction=jurisdiction,
            domains=DOMAIN_CATALOGUE,
        )

    @classmethod
    def check_domain_support(cls, domain_id: str, jurisdiction: str = "BD") -> dict[str, Any]:
        """Checks domain support status. Abstains and warns on unsupported jurisdictions or domains."""
        # 1. Unsupported jurisdiction check
        if jurisdiction != "BD":
            return {
                "domain_id": domain_id,
                "jurisdiction": jurisdiction,
                "is_supported": False,
                "support_status": "unsupported_jurisdiction",
                "advisory_en": (
                    f"Jurisdiction '{jurisdiction}' is not supported. "
                    "ClaimCraft BD is strictly designed for Bangladesh consumer statutory frameworks."
                ),
                "advisory_bn": (
                    f"'{jurisdiction}' বিচারব্যবস্থা সমর্থিত নয়। "
                    "ক্লেইমক্রাফট বিডি শুধুমাত্র বাংলাদেশের ভোক্তা আইনি কাঠামোর জন্য প্রস্তুত।"
                ),
            }

        # 2. Find domain in catalogue
        entry = next((d for d in DOMAIN_CATALOGUE if d.domain_id == domain_id), None)
        if not entry:
            return {
                "domain_id": domain_id,
                "jurisdiction": jurisdiction,
                "is_supported": False,
                "support_status": "unsupported_domain",
                "advisory_en": (
                    f"Domain '{domain_id}' is not an approved domain pack. "
                    "ClaimCraft BD refuses to advertise or process unapproved domains as fully supported."
                ),
                "advisory_bn": (
                    f"'{domain_id}' কোনো অনুমোদিত ডোমেইন প্যাক নয়। "
                    "অননুমোদিত কোনো বিষয়ে সিদ্ধান্ত প্রদান থেকে বিরত থাকা হচ্ছে।"
                ),
            }

        return {
            "domain_id": entry.domain_id,
            "jurisdiction": jurisdiction,
            "is_supported": True,
            "support_status": entry.support_status,
            "is_fully_supported": entry.is_fully_supported,
            "support_depth": entry.support_depth,
            "disclosed_routes": entry.disclosed_routes,
            "statutory_basis": entry.statutory_basis,
            "caveat_en": entry.caveat_en,
            "caveat_bn": entry.caveat_bn,
        }
