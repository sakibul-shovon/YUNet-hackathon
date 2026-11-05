from typing import Any

from pydantic import BaseModel, ConfigDict

from app.actions.destinations import ComplaintDestinationService


class PortalFieldDef(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    field_key: str
    label_en: str
    label_bn: str
    fact_source: str
    required: bool = True
    prepared_value: str | None = None
    transformation: str | None = None
    notes: str | None = None


class PortalFieldMapOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    portal_id: str
    portal_name_en: str
    portal_name_bn: str
    official_destination_url: str
    procedure_guide_url: str | None = None
    destination_link_health: str = 'linked_unconfirmed'
    map_version: str
    is_stale: bool = False
    stale_reason: str | None = None
    fields: list[PortalFieldDef]
    disclaimer_en: str = (
        "Review the authority's current form before copying prepared values yourself. "
        "Ebarki never asks for, enters, or stores portal credentials (T33)."
    )
    disclaimer_bn: str = (
        "সরকারি অফিশিয়াল পোর্টালে ফিল্ড অনুযায়ী তথ্য কপি করে বসান। "
        "Ebarki কখনোই আপনার পোর্টাল পাসওয়ার্ড চায় না বা স্বয়ংক্রিয়ভাবে প্রবেশ করে না (T33)।"
    )


PORTAL_MAP_REGISTRY: dict[str, dict[str, Any]] = {
    "dncrp_ccms": {
        "portal_id": "dncrp_ccms",
        "portal_name_en": "DNCRP Central Complaint Management System (CCMS)",
        "portal_name_bn": "ভোক্তা অধিকার সংরক্ষণ অধিদপ্তর সিসিএমএস পোর্টাল",
        "official_destination_url": "https://dncrp.com/",
        "map_version": "2026.1",
        "is_stale": False,
        "stale_reason": None,
        "fields": [
            {
                "field_key": "opposite_party_name",
                "label_en": "Opposite Party / Merchant Name",
                "label_bn": "অভিযুক্ত প্রতিষ্ঠান / বিক্রেতার নাম",
                "fact_source": "merchant_name",
                "required": True,
            },
            {
                "field_key": "incident_date",
                "label_en": "Date of Occurrence",
                "label_bn": "ঘটনার তারিখ",
                "fact_source": "incident_date",
                "required": True,
            },
            {
                "field_key": "claim_amount_bdt",
                "label_en": "Total Claim Amount (BDT)",
                "label_bn": "দাবিকৃত অর্থের পরিমাণ (টাকা)",
                "fact_source": "amount_paid",
                "required": True,
                "transformation": "minor_units_to_bdt",
            },
            {
                "field_key": "brief_description",
                "label_en": "Brief Description of Consumer Violation",
                "label_bn": "অভিযোগের সংক্ষিপ্ত বিবরণ",
                "fact_source": "story_narrative",
                "required": True,
            },
            {
                "field_key": "desired_relief",
                "label_en": "Outcome You Are Requesting",
                "label_bn": "যে সমাধান চাইছেন",
                "fact_source": "desired_outcomes",
                "required": True,
            },
        ],
    },
    "bb_cipc": {
        "portal_id": "bb_cipc",
        "portal_name_en": "Bangladesh Bank Customer Interests Protection Centre (CIPC)",
        "portal_name_bn": "বাংলাদেশ ব্যাংক সিআইপিসি অভিযোগ সেল",
        "official_destination_url": "https://cms.bb.org.bd/ords/f?p=107%3A133%3A",
        "map_version": "2026.1",
        "is_stale": False,
        "stale_reason": None,
        "fields": [
            {
                "field_key": "provider_name",
                "label_en": "MFS Provider / Bank Name",
                "label_bn": "এমএফএস / ব্যাংক প্রোভাইডারের নাম",
                "fact_source": "merchant_name",
                "required": True,
            },
            {
                "field_key": "provider_ticket_number",
                "label_en": "Stage 1 Complaint Ticket Number",
                "label_bn": "ধাপ ১ অভিযোগ ট্র্যাকিং টিকিট নম্বর",
                "fact_source": "provider_ticket_number",
                "required": True,
                "notes": "Mandatory prior grievance reference (T20)",
            },
            {
                "field_key": "disputed_transaction_id",
                "label_en": "Transaction ID (TrxID)",
                "label_bn": "ট্রানজেকশন আইডি (TrxID)",
                "fact_source": "transaction_id",
                "required": True,
            },
            {
                "field_key": "disputed_amount_bdt",
                "label_en": "Disputed Amount (BDT)",
                "label_bn": "বিরোধপূর্ণ টাকার পরিমাণ",
                "fact_source": "amount_paid",
                "required": True,
                "transformation": "minor_units_to_bdt",
            },
            {
                "field_key": "grievance_narrative",
                "label_en": "Detailed Chronology of Incident",
                "label_bn": "ঘটনার বিস্তারিত বিবরণ",
                "fact_source": "story_narrative",
                "required": True,
            },
        ],
    },
    "btrc_complaint": {
        "portal_id": "btrc_complaint",
        "portal_name_en": "BTRC Telecom & Internet Consumer Grievance Portal",
        "portal_name_bn": "বিটিআরসি টেলিযোগাযোগ ও ইন্টারনেট অভিযোগ প্রতিকার পোর্টাল",
        "official_destination_url": "https://crm.btrc.gov.bd/",
        "map_version": "2026.1",
        "is_stale": False,
        "stale_reason": None,
        "fields": [
            {
                "field_key": "operator_name",
                "label_en": "Telecom Operator / ISP Name",
                "label_bn": "টেলিকম অপারেটর / আইএসপির নাম",
                "fact_source": "merchant_name",
                "required": True,
            },
            {
                "field_key": "provider_ticket_number",
                "label_en": "Stage 1 Operator Complaint Ticket",
                "label_bn": "অপারেটরের পূর্বের টিকিট নম্বর",
                "fact_source": "provider_ticket_number",
                "required": True,
                "notes": "Mandatory prior operator grievance reference",
            },
            {
                "field_key": "dispute_description",
                "label_en": "Disruption or Billing Error Details",
                "label_bn": "সেবা বিঘ্ন বা বিলিং ভুলের বিবরণ",
                "fact_source": "story_narrative",
                "required": True,
            },
            {
                "field_key": "incident_date",
                "label_en": "Date of Occurrence",
                "label_bn": "ঘটনার তারিখ",
                "fact_source": "incident_date",
                "required": True,
            },
        ],
    },
    "idra_grievance": {
        "portal_id": "idra_grievance",
        "portal_name_en": "IDRA Insurance Grievance Cell",
        "portal_name_bn": "আইডিআরএ বীমা অভিযোগ সেল",
        "official_destination_url": "https://cms.idra.org.bd/grievence-form",
        "map_version": "2026.1",
        "is_stale": False,
        "stale_reason": None,
        "fields": [
            {
                "field_key": "insurer_name",
                "label_en": "Insurance Company Name",
                "label_bn": "বীমা কোম্পানির নাম",
                "fact_source": "merchant_name",
                "required": True,
            },
            {
                "field_key": "claim_reference",
                "label_en": "Prior Claim Reference Number",
                "label_bn": "বীমা দাবির পূর্ববর্তী রেফারেন্স",
                "fact_source": "claim_reference",
                "required": True,
            },
            {
                "field_key": "grievance_narrative",
                "label_en": "Details of Claim Denial or Delay",
                "label_bn": "দাবি প্রত্যাখ্যান বা বিলম্বের বিবরণ",
                "fact_source": "story_narrative",
                "required": True,
            },
        ],
    },
    "cabinet_grs": {
        "portal_id": "cabinet_grs",
        "portal_name_en": "Cabinet Division Central Grievance Redress System (GRS)",
        "portal_name_bn": "মন্ত্রিপরিষদ বিভাগ কেন্দ্রীয় অভিযোগ প্রতিকার ব্যবস্থা (জিআরএস)",
        "official_destination_url": "https://www.grs.gov.bd/",
        "map_version": "2026.1",
        "is_stale": False,
        "stale_reason": None,
        "fields": [
            {
                "field_key": "department_name",
                "label_en": "Public Department / Authority",
                "label_bn": "সরকারি বিভাগ বা কর্তৃপক্ষের নাম",
                "fact_source": "merchant_name",
                "required": True,
            },
            {
                "field_key": "grievance_narrative",
                "label_en": "Service Delay or Irregularity Description",
                "label_bn": "সেবা প্রদানে বিলম্ব বা অনিয়মের বিবরণ",
                "fact_source": "story_narrative",
                "required": True,
            },
        ],
    },
}


class PortalFieldMapService:
    """P09.3 & T33: Prepares versioned portal field maps with reviewed fact mapping

    and safe per-field copy. Stale map fallback supported.
    """

    @classmethod
    def get_field_map(
        cls,
        portal_id: str,
        case_data: dict[str, Any],
        facts: dict[str, Any],
    ) -> PortalFieldMapOut:
        raw_map = PORTAL_MAP_REGISTRY.get(portal_id)
        if not raw_map:
            raise ValueError('Unknown filing preparation channel.')
        destination_id = {'dncrp_ccms': 'dncrp_ccms_portal', 'bb_cipc': 'bb_cipc_portal',
                          'btrc_complaint': 'btrc_consumer_cell', 'idra_grievance': 'idra_grievance_cell',
                          'cabinet_grs': 'cabinet_grs_portal'}[portal_id]
        destination = ComplaintDestinationService.get_destination(destination_id)

        fields_out: list[PortalFieldDef] = []
        is_stale = raw_map.get("is_stale", False)

        for f in raw_map["fields"]:
            fact_src = f["fact_source"]
            val = facts[fact_src] if fact_src in facts else case_data.get(fact_src)

            prep_val = None
            if not is_stale and val is not None:
                if f.get("transformation") == "minor_units_to_bdt" and isinstance(val, int):
                    prep_val = f"{val / 100:,.2f}"
                elif isinstance(val, list):
                    prep_val = ", ".join(str(x) for x in val)
                else:
                    prep_val = str(val)

            fields_out.append(
                PortalFieldDef(
                    field_key=f["field_key"],
                    label_en=f["label_en"],
                    label_bn=f["label_bn"],
                    fact_source=f["fact_source"],
                    required=f.get("required", True),
                    prepared_value=prep_val,
                    transformation=f.get("transformation"),
                    notes=f.get("notes"),
                )
            )

        return PortalFieldMapOut(
            portal_id=raw_map["portal_id"],
            portal_name_en=raw_map["portal_name_en"],
            portal_name_bn=raw_map["portal_name_bn"],
            official_destination_url=destination.official_portal_url,
            procedure_guide_url=destination.procedure_guide_url,
            destination_link_health=destination.link_health,
            map_version=raw_map["map_version"],
            is_stale=is_stale,
            stale_reason=raw_map.get("stale_reason"),
            fields=fields_out,
        )
