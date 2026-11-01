import datetime
import ipaddress
import socket
from urllib.parse import urlparse

from pydantic import BaseModel, Field

# Section 12.1 Official host allowlist
OFFICIAL_HOST_ALLOWLIST = {
    "dncrp.gov.bd",
    "ccms.dncrp.com",
    "bdlaws.minlaw.gov.bd",
    "bb.org.bd",
    "btrc.gov.bd",
    "dpp.gov.bd",
    "services.portal.gov.bd",
    "dncrp.portal.gov.bd",
}


def is_private_or_restricted_ip(ip_str: str) -> bool:
    """Checks whether an IP address belongs to private, loopback, or metadata networks (SSRF prevention)."""
    try:
        ip = ipaddress.ip_address(ip_str)
        return (
            ip.is_private
            or ip.is_loopback
            or ip.is_link_local
            or ip.is_multicast
            or ip.is_reserved
            or ip_str == "169.254.169.254"  # AWS/GCP/Azure link-local metadata
        )
    except ValueError:
        return True


def is_url_allowlisted(url: str, resolve_dns: bool = False) -> tuple[bool, str]:
    """Validates that a URL strictly belongs to an allowlisted official host and prevents SSRF.

    Returns (is_allowed, reason).
    """
    try:
        parsed = urlparse(url)
    except ValueError as e:
        return False, f"Malformed URL: {e}"

    if parsed.scheme not in ("http", "https"):
        return False, f"Unsupported scheme: '{parsed.scheme}'. Only http and https allowed."

    hostname = (parsed.hostname or "").lower()
    if not hostname:
        return False, "Missing hostname in URL."

    # Validate against host allowlist (exact match or subdomain match)
    matches_allowlist = any(
        hostname == allowed or hostname.endswith(f".{allowed}")
        for allowed in OFFICIAL_HOST_ALLOWLIST
    )
    if not matches_allowlist:
        return False, f"Host '{hostname}' is not in the official government allowlist."

    # Optional DNS resolution to prevent DNS rebinding / SSRF to private addresses
    if resolve_dns:
        try:
            addr_info = socket.getaddrinfo(hostname, None)
            for item in addr_info:
                ip_addr = item[4][0]
                if is_private_or_restricted_ip(ip_addr):
                    return False, f"Resolved IP {ip_addr} for {hostname} is in a restricted/private network."
        except socket.gaierror as e:
            return False, f"DNS resolution failed for {hostname}: {e}"

    return True, "URL is allowlisted"


class SourceRegistryEntry(BaseModel):
    id: str
    title_en: str
    title_bn: str
    issuer: str
    issuer_bn: str
    official_url: str
    document_type: str  # 'statute', 'circular', 'procedure_guide', 'portal_map', 'emergency_contact'
    status: str = Field("candidate", description="'candidate', 'observed', 'unavailable'")
    applicable_domains: list[str]
    fetch_cadence_hours: int = 24
    last_checked_at: datetime.datetime | None = None
    health_status: str = "current_check_passed"  # 'current_check_passed', 'check_overdue', 'temporarily_unavailable'
    procedural_scope: str = "procedure_guidance"  # 'procedure_guidance' or 'reviewed_statutory_guidance'
    is_authoritative_for_penalties: bool = False
    notes: str | None = None


INITIAL_SOURCE_REGISTRY: list[SourceRegistryEntry] = [
    SourceRegistryEntry(
        id="bd_crpa_2009",
        title_en="Consumer Rights Protection Act, 2009 (Act No. 26 of 2009)",
        title_bn="ভোক্তা-অধিকার সংরক্ষণ আইন, ২০০৯ (২০০৯ সনের ২৬ নং আইন)",
        issuer="Legislative and Parliamentary Affairs Division, Ministry of Law",
        issuer_bn="লেজিসলেটিভ ও সংসদ বিষয়ক বিভাগ, আইন মন্ত্রণালয়",
        official_url="http://bdlaws.minlaw.gov.bd/act-1014.html",
        document_type="statute",
        status="observed",
        applicable_domains=["consumer_ecommerce", "retail_goods", "product_safety"],
        procedural_scope="reviewed_statutory_guidance",
        is_authoritative_for_penalties=True,
        notes="Primary statutory basis for consumer complaints, 30-day filing timeline, 25% reward for complainants.",
    ),
    SourceRegistryEntry(
        id="dncrp_ccms_portal",
        title_en="DNCRP Consumer Complaint Management System (CCMS)",
        title_bn="জাতীয় ভোক্তা-অধিকার সংরক্ষণ অধিদপ্তর সিসিএমএস পোর্টাল",
        issuer="Directorate of National Consumer Rights Protection",
        issuer_bn="জাতীয় ভোক্তা-অধিকার সংরক্ষণ অধিদপ্তর",
        official_url="https://ccms.dncrp.com/",
        document_type="portal_map",
        status="observed",
        applicable_domains=["consumer_ecommerce", "retail_goods"],
        procedural_scope="procedure_guidance",
        notes="Official online portal for filing consumer complaints with evidence attachments.",
    ),
    SourceRegistryEntry(
        id="dncrp_official_portal",
        title_en="DNCRP Official Web Portal and Manual Complaint Procedure",
        title_bn="ডিএনসিআরপি অফিসিয়াল ওয়েব পোর্টাল ও অভিযোগ দায়ের পদ্ধতি",
        issuer="Directorate of National Consumer Rights Protection",
        issuer_bn="জাতীয় ভোক্তা-অধিকার সংরক্ষণ অধিদপ্তর",
        official_url="http://dncrp.portal.gov.bd/",
        document_type="procedure_guide",
        status="observed",
        applicable_domains=["consumer_ecommerce", "retail_goods"],
        procedural_scope="procedure_guidance",
        notes="Official guide detailing divisional and district offices, email filing, and required identity proof.",
    ),
    SourceRegistryEntry(
        id="bb_cipc_procedure",
        title_en="Bangladesh Bank Customer Interests Protection Centre (CIPC) Procedure",
        title_bn="বাংলাদেশ ব্যাংক গ্রাহক স্বার্থ সংরক্ষণ কেন্দ্র (সিআইপিসি) পদ্ধতি",
        issuer="Financial Integrity and Customer Services Department (FICSD), Bangladesh Bank",
        issuer_bn="ফাইন্যান্সিয়াল ইন্টিগ্রিটি অ্যান্ড কাস্টমার সার্ভিসেস ডিপার্টমেন্ট, বাংলাদেশ ব্যাংক",
        official_url="https://bb.org.bd/en/index.php/services/cipc_procedure",
        document_type="procedure_guide",
        status="observed",
        applicable_domains=["financial_services", "mfs_banking"],
        procedural_scope="procedure_guidance",
        notes="Two-stage complaint procedure: mandatory first-level complaint to provider followed by CIPC escalation.",
    ),
    SourceRegistryEntry(
        id="bb_mfs_regulations_2022",
        title_en="Bangladesh Bank Mobile Financial Services (MFS) Regulations, 2022",
        title_bn="বাংলাদেশ ব্যাংক মোবাইল ফিন্যান্সিয়াল সার্ভিসেস (এমএফএস) রেগুলেশন্স, ২০২২",
        issuer="Payment Systems Department, Bangladesh Bank",
        issuer_bn="পেমেন্ট সিস্টেমস ডিপার্টমেন্ট, বাংলাদেশ ব্যাংক",
        official_url="https://bb.org.bd/en/index.php/about/financialsystem/mfs",
        document_type="circular",
        status="candidate",
        applicable_domains=["financial_services", "mfs_banking"],
        procedural_scope="procedure_guidance",
        notes="Dispute resolution and unauthorized transaction obligations for bKash, Nagad, Rocket, etc.",
    ),
    SourceRegistryEntry(
        id="btrc_complaint_guidelines",
        title_en="BTRC Telecom & Internet Consumer Grievance System",
        title_bn="বিটিআরসি টেলিযোগাযোগ ও ইন্টারনেট গ্রাহক অভিযোগ প্রতিকার ব্যবস্থা",
        issuer="Bangladesh Telecommunication Regulatory Commission",
        issuer_bn="বাংলাদেশ টেলিযোগাযোগ নিয়ন্ত্রণ কমিশন",
        official_url="http://btrc.gov.bd/",
        document_type="procedure_guide",
        status="candidate",
        applicable_domains=["telecom_isp"],
        procedural_scope="procedure_guidance",
        notes="Escalation procedures for unresolved cellular network, mobile data, and broadband ISP disputes.",
    ),
    SourceRegistryEntry(
        id="dncrp_hotline_16121",
        title_en="National Consumer Rights Dedicated Hotline 16121",
        title_bn="ভোক্তা অধিকার হটলাইন ১৬১২১",
        issuer="Directorate of National Consumer Rights Protection",
        issuer_bn="জাতীয় ভোক্তা-অধিকার সংরক্ষণ অধিদপ্তর",
        official_url="http://dncrp.portal.gov.bd/",
        document_type="emergency_contact",
        status="observed",
        applicable_domains=["consumer_ecommerce", "retail_goods", "product_safety"],
        procedural_scope="procedure_guidance",
        notes="Direct telephone assistance for immediate deceptive practice alerts and urgent guidance.",
    ),
]


def get_source_registry() -> list[SourceRegistryEntry]:
    """Returns the immutable registered source entries."""
    return INITIAL_SOURCE_REGISTRY


def get_source_by_id(source_id: str) -> SourceRegistryEntry | None:
    """Finds a source registry entry by unique ID."""
    for s in INITIAL_SOURCE_REGISTRY:
        if s.id == source_id:
            return s
    return None
