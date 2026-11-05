import datetime
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
    link_health: str = "linked_unconfirmed"
    checked_at: str | None = None
    verification_note: str = 'Read-only destination information; filing is completed by the user.'
    fallback_instructions_en: str
    fallback_instructions_bn: str


DESTINATION_REGISTRY: dict[str, dict[str, Any]] = {'dncrp_ccms_portal': {'destination_id': 'dncrp_ccms_portal',
                       'title_en': 'DNCRP Central Complaint Management System (CCMS)',
                       'title_bn': 'ভোক্তা অধিকার সংরক্ষণ অধিদপ্তর (সিসিএমএস পোর্টাল)',
                       'authority_name': "Directorate of National Consumers' Right Protection (DNCRP)",
                       'official_portal_url': 'https://dncrp.com/',
                       'procedure_guide_url': 'https://dncrp.portal.gov.bd/',
                       'prerequisites_en': ["An active mobile number for your own official account", "Money receipt, memo, or invoice showing merchant identity and date", "Evidence of non-delivery or product defect (screenshots/SMS)", "Check the complaint time limit and its starting date against the official guidance."],
                       'prerequisites_bn': ["নিজের সরকারি অ্যাকাউন্ট খোলার জন্য সচল মোবাইল নম্বর", "ক্রয় রশিদ বা ক্যাশমেমো যাতে বিক্রেতার নাম ও তারিখ উল্লেখ রয়েছে", "পণ্য না পাওয়া বা ত্রুটির সুনির্দিষ্ট প্রমাণ (স্ক্রিনশট/এসএমএস)", "অভিযোগের সময়সীমা ও কোন তারিখ থেকে হিসাব হবে, সরকারি নির্দেশনায় মিলিয়ে নিন।"],
                       'link_health': 'healthy',
                       'fallback_instructions_en': "If the portal is unavailable, check the authority's "
                                                   'current official guidance for support and alternative '
                                                   'filing instructions.',
                       'fallback_instructions_bn': 'পোর্টাল চালু না থাকলে সহায়তা ও অন্যভাবে অভিযোগ করার নিয়ম '
                                                   'অধিদপ্তরের বর্তমান সরকারি নির্দেশনায় দেখুন।',
                       'checked_at': '2026-11-05T05:40:40+06:00',
                       'verification_note': 'Read-only page observation; no complaint was submitted. Recheck '
                                            'the authority page before use.'},
 'bb_cipc_portal': {'destination_id': 'bb_cipc_portal',
                    'title_en': 'Bangladesh Bank Customer Interests Protection Centre (CIPC)',
                    'title_bn': 'বাংলাদেশ ব্যাংক গ্রাহক স্বার্থ সংরক্ষণ কেন্দ্র (সিআইপিসি)',
                    'authority_name': 'Bangladesh Bank Customer Interest Protection Centre (CIPC), TRDS',
                    'official_portal_url': 'https://cms.bb.org.bd/ords/f?p=107%3A133%3A',
                    'procedure_guide_url': 'https://www.bb.org.bd/en/index.php/services/cipc_procedure',
                    'prerequisites_en': ["Contact the bank, finance company or MFS provider first, then its complaint cell.", "Keep the provider response and relevant transaction records.", "Include your contact details when personally filing with CIPC."],
                    'prerequisites_bn': ["আগে ব্যাংক, আর্থিক প্রতিষ্ঠান বা এমএফএস সেবাদাতা এবং তাদের অভিযোগ সেলে যোগাযোগ করুন।", "সেবাদাতার জবাব ও প্রাসঙ্গিক লেনদেনের নথি রাখুন।", "সিআইপিসিতে নিজে অভিযোগ করার সময় যোগাযোগের তথ্য দিন।"],
                    'link_health': 'linked_unconfirmed',
                    'fallback_instructions_en': 'Target form link timed out in automated checks. Use '
                                                'official procedure page fallback or email '
                                                'bb.cipc@bb.org.bd, or call hotline 16236.',
                    'fallback_instructions_bn': 'সরাসরি ফর্ম লিংকে কারিগরি সমস্যা হলে অফিসিয়াল নির্দেশিকা '
                                                'পেজ দেখুন অথবা bb.cipc@bb.org.bd-এ ইমেইল পাঠান বা ১৬২৩৬ '
                                                'নম্বরে কল করুন।',
                    'checked_at': '2026-11-05T05:40:40+06:00',
                    'verification_note': 'Read-only page observation; no complaint was submitted. Recheck '
                                         'the authority page before use.'},
 'dncrp_hotline_16121': {'destination_id': 'dncrp_hotline_16121',
                         'title_en': 'National Consumer Rights Complaint and Information Hotline 16121',
                         'title_bn': 'জাতীয় ভোক্তা অধিকার সংরক্ষণ হটলাইন ১৬১২১',
                         'authority_name': 'Directorate of National Consumer Rights Protection',
                         'official_portal_url': 'tel:16121',
                         'procedure_guide_url': 'https://dncrp.portal.gov.bd/',
                         'prerequisites_en': ["For consumer complaint guidance; this is not an emergency rescue service.", "Avoid handling or preserving a dangerous item if doing so would be unsafe."],
                         'prerequisites_bn': ["ভোক্তা অভিযোগের নির্দেশনার জন্য; এটি জরুরি উদ্ধারসেবা নয়।", "বিপজ্জনক পণ্য নাড়াচাড়া বা নমুনা রাখতে গিয়ে নিজেকে ঝুঁকিতে ফেলবেন না।"],
                         'link_health': 'linked_unconfirmed',
                         'fallback_instructions_en': 'Check the current DNCRP authority page for complaint '
                                                     'guidance. Seek appropriate emergency assistance for '
                                                     'immediate danger.',
                         'fallback_instructions_bn': 'অভিযোগের নিয়ম অধিদপ্তরের বর্তমান সরকারি পাতায় দেখুন। '
                                                     'তাৎক্ষণিক বিপদে উপযুক্ত জরুরি সহায়তা নিন।',
                         'checked_at': '2026-11-05T05:40:40+06:00',
                         'verification_note': 'Read-only page observation; no complaint was submitted. '
                                              'Recheck the authority page before use.'},
 'btrc_consumer_cell': {'destination_id': 'btrc_consumer_cell',
                        'title_en': 'BTRC Telecom Consumer Grievance Cell & Hotline 100',
                        'title_bn': 'বিটিআরসি গ্রাহক অভিযোগ সেল ও হটলাইন ১০০',
                        'authority_name': 'Bangladesh Telecommunication Regulatory Commission (BTRC)',
                        'official_portal_url': 'https://crm.btrc.gov.bd/',
                        'procedure_guide_url': 'https://btrc.gov.bd/',
                        'prerequisites_en': ["Describe the service issue and location.", "Keep operator contact, response and ticket details if available."],
                        'prerequisites_bn': ["সেবার সমস্যা ও এলাকার তথ্য দিন।", "অপারেটরের সঙ্গে যোগাযোগ, জবাব ও টিকিটের তথ্য থাকলে রাখুন।"],
                        'link_health': 'healthy',
                        'fallback_instructions_en': 'Use BTRC complaint guidance or the published telecom '
                                                    'complaint hotline 100; no unverified email address is '
                                                    'supplied.',
                        'fallback_instructions_bn': 'বিটিআরসির অভিযোগের নির্দেশনা বা প্রকাশিত টেলিযোগাযোগ '
                                                    'অভিযোগের হটলাইন ১০০ ব্যবহার করুন।',
                        'checked_at': '2026-11-05T05:40:40+06:00',
                        'verification_note': 'Read-only page observation; no complaint was submitted. '
                                             'Recheck the authority page before use.'},
 'idra_grievance_cell': {'destination_id': 'idra_grievance_cell',
                         'title_en': 'IDRA Insurance Policyholder Grievance Redress Cell',
                         'title_bn': 'আইডিআরএ বীমা গ্রাহক অভিযোগ প্রতিকার সেল',
                         'authority_name': 'Insurance Development and Regulatory Authority (IDRA)',
                         'official_portal_url': 'https://cms.idra.org.bd/grievence-form',
                         'procedure_guide_url': 'https://idra.portal.gov.bd/pages/web-forms/6922d3c181fc96cef9e9bf15',
                         'prerequisites_en': ["Keep the policy and insurer claim or response documents.", "Describe the grievance. No universal 90-day complaint-filing deadline is asserted here."],
                         'prerequisites_bn': ["পলিসি এবং বীমা প্রতিষ্ঠানে দেওয়া দাবি বা তাদের জবাবের নথি রাখুন।", "অভিযোগের ঘটনা লিখুন। সব অভিযোগের জন্য ৯০ দিনের সময়সীমা ধরে নেওয়া হয়নি।"],
                         'link_health': 'healthy',
                         'fallback_instructions_en': 'Use the current IDRA government complaint page if the '
                                                     'form is unavailable. No unverified complaint email is '
                                                     'supplied.',
                         'fallback_instructions_bn': 'ফর্ম চালু না থাকলে আইডিআরএর বর্তমান সরকারি অভিযোগের '
                                                     'পাতা দেখুন।',
                         'checked_at': '2026-11-05T05:40:40+06:00',
                         'verification_note': 'Read-only page observation; no complaint was submitted. '
                                              'Recheck the authority page before use.'},
 'cabinet_grs_portal': {'destination_id': 'cabinet_grs_portal',
                        'title_en': 'Cabinet Division Central Grievance Redress System (GRS)',
                        'title_bn': 'মন্ত্রিপরিষদ বিভাগ কেন্দ্রীয় অভিযোগ প্রতিকার ব্যবস্থা (জিআরএস)',
                        'authority_name': 'Cabinet Division, Government of Bangladesh',
                        'official_portal_url': 'https://www.grs.gov.bd/',
                        'procedure_guide_url': 'https://www.grs.gov.bd/',
                        'prerequisites_en': ["Public service application tracking number or receipt", "Citizen Charter response window has elapsed", "Matter must NOT be sub judice or pending before any court of law"],
                        'prerequisites_bn': ["সরকারি সেবার আবেদন ট্র্যাকিং নম্বর বা প্রাপ্তিস্বীকার পত্র", "সিটিজেন চার্টারের নির্ধারিত সময় অতিক্রান্ত হওয়া", "বিষয়টি কোনো আদালতে বিচারাধীন (সাব-জুডিস) হওয়া চলবে না"],
                        'link_health': 'healthy',
                        'fallback_instructions_en': 'If portal is unreachable, file grievance in person with '
                                                    'the departmental Grievance Redress Officer (GRO).',
                        'fallback_instructions_bn': 'অনলাইন পোর্টাল অনুপলব্ধ হলে সংশ্লিষ্ট দপ্তরের অভিযোগ '
                                                    'নিষ্পত্তি কর্মকর্তার (GRO) নিকট সরাসরি আবেদন দিন।',
                        'checked_at': '2026-11-05T05:40:40+06:00',
                        'verification_note': 'Read-only page observation; no complaint was submitted. '
                                             'Recheck the authority page before use.'}}


class ComplaintDestinationService:
    """P09.7 & T54: Official complaint destination registry and link-health fallback."""

    @classmethod
    def get_destination(cls, destination_id: str) -> ComplaintDestinationOut:
        data = DESTINATION_REGISTRY.get(destination_id)
        if not data:
            from fastapi import HTTPException
            raise HTTPException(404, 'Unknown filing destination.')
        result = ComplaintDestinationOut.model_validate(data)
        if result.link_health == 'healthy' and result.checked_at and (
            datetime.datetime.now(datetime.UTC)-datetime.datetime.fromisoformat(result.checked_at) > datetime.timedelta(hours=24)
        ):
            result.link_health = 'linked_unconfirmed'
        return result

    @classmethod
    def list_destinations(cls) -> list[ComplaintDestinationOut]:
        return [cls.get_destination(key) for key in DESTINATION_REGISTRY]
