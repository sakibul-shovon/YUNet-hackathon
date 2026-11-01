"""Interactive Synthetic Scenario Manifests for Judge Sandboxes.

Adheres to Section 20.1 & T52:
- Exactly eight scenarios: A, B, C, D, E, F, G, H
- Three featured quick starts: A, B, H
- Real pipeline execution with isolated state; concurrent judges cannot share mutations
- Real synthetic inputs with explicit non-filing and synthetic notice
"""

from typing import Any

from pydantic import BaseModel


class SyntheticScenarioManifest(BaseModel):
    scenario_id: str
    scenario_letter: str
    is_featured: bool
    title_en: str
    title_bn: str
    domain: str
    inputs_en: str
    inputs_bn: str
    description_en: str
    description_bn: str
    differentiator_en: str
    differentiator_bn: str
    sample_story: str
    merchant_name: str
    initial_facts: dict[str, Any]


SCENARIO_MANIFESTS: list[SyntheticScenarioManifest] = [
    SyntheticScenarioManifest(
        scenario_id="scenario_a",
        scenario_letter="A",
        is_featured=True,
        title_en="Prepaid Phone Non-Delivery with Amount Mismatch",
        title_bn="অগ্রিম পরিশোধিত অনলাইন ফোন অর্ডার ডেলিভারি হয়নি",
        domain="E-Commerce",
        inputs_en="Bangla Story + bKash Receipt Image",
        inputs_bn="বাংলা বিবরণ + বিকাশ পেমেন্ট রসিদ",
        description_en="Multi-payment discrepancy, provenance, merchant vs provider why-not, what-if, prepared consumer request.",
        description_bn="বহু-পেমেন্ট অসঙ্গতি, প্রোভাইডার বনাম বিক্রেতা বিরোধ, হোয়াট-ইফ সিমুলেশন ও ভোক্তা আবেদন।",
        differentiator_en="Contradiction resolution (৳5,500 narration vs ৳5,000 receipt) and non-delivery Section 45 filing.",
        differentiator_bn="টাকার পরিমাণের অমিল সমাধান (৫৫০০ বনাম ৫০০০ টাকা) এবং ধারা ৪৫ অনুযায়ী প্রতিকার প্রস্তুতি।",
        sample_story="আমি দারাজ থেকে গত ১০ জানুয়ারি একটি স্যামসাং ফোন অর্ডার করি। ৫,৫০০ টাকা পেমেন্ট করার কথা ছিল কিন্তু ডেলিভারি ডেট পার হয়ে গেলেও পণ্য পাইনি।",
        merchant_name="Daraz Bangladesh Ltd",
        initial_facts={
            "purchase_channel": "ecommerce",
            "goods_delivered": False,
            "promised_delivery_date_passed": True,
            "refund_already_issued": False,
            "order_cancelled_by_buyer_before_dispatch": False,
        },
    ),
    SyntheticScenarioManifest(
        scenario_id="scenario_b",
        scenario_letter="B",
        is_featured=True,
        title_en="MFS Unsuccessful Transfer & Auto-Reversal Delay",
        title_bn="এমএফএস অসফল লেনদেন: ব্যালেন্স কর্তন কিন্তু মার্চেন্টে জমা হয়নি",
        domain="Fintech / MFS",
        inputs_en="Voice Note + App Screenshot",
        inputs_bn="ভয়েস অডিও + অ্যাপ স্ক্রিনশট",
        description_en="Complete voice-to-case, provider-service distinction, stage-based complaint channel and reassessment.",
        description_bn="ভয়েস-টু-কেস, প্রোভাইডার সার্ভিস বিরোধ, দুই ধাপের অভিযোগ শৃঙ্খলা (ধাপ ১ প্রোভাইডার -> ধাপ ২ বাংলাদেশ ব্যাংক)।",
        differentiator_en="T20 procedural hierarchy: Mandatory provider formal letter before BB CIPC escalation.",
        differentiator_bn="টি২০ আইনি শৃঙ্খলা: বাংলাদেশ ব্যাংকে যাওয়ার পূর্বে প্রোভাইডারে অভিযোগ দাখিল বাধ্যতামূলক।",
        sample_story="বিকাশ অ্যাপ থেকে মার্চেন্ট পেমেন্ট করার সময় একাউন্ট থেকে ৪,২০০ টাকা কেটে নেওয়া হয় কিন্তু মার্চেন্ট টাকা পায়নি। প্রোভাইডারে টিকিট করা হয়নি।",
        merchant_name="bKash Limited",
        initial_facts={
            "payment_instrument_kind": "mfs_wallet",
            "transaction_unauthorized": True,
            "alleged_provider_service_failure": True,
            "provider_ticket_filed": False,
        },
    ),
    SyntheticScenarioManifest(
        scenario_id="scenario_c",
        scenario_letter="C",
        is_featured=False,
        title_en="Defective Purchase & Repudiated Return",
        title_bn="ত্রুটিপূর্ণ পণ্য ক্রয় ও ওয়ারেন্টি প্রদানে অস্বীকৃতি",
        domain="Retail Goods",
        inputs_en="English Text Narrative + Return Policy PDF",
        inputs_bn="ইংরেজি বিবরণ + দোকানের রিটার্ন পলিসি নথি",
        description_en="Native parsing, policy-vs-law distinction, desired replacement/refund request, original citations.",
        description_bn="নথি পার্সিং, দোকানের নিজস্ব পলিসি বনাম আইনি অধিকারের পার্থক্য ও ধারা ৪১/৪৪ ক্ষতিপূরণ।",
        differentiator_en="Enforces Consumer Rights Protection Act over private merchant 'no return' terms.",
        differentiator_bn="দোকানের ব্যক্তিগত 'বিক্রিত মাল ফেরত নেওয়া হয় না' শর্তের ওপর ভোক্তা অধিকার আইনের প্রাধান্য।",
        sample_story="Purchased a smart TV from a physical showroom. Screen had major flickering defect on day 2. Shop manager refused return citing invoice fine print.",
        merchant_name="Apex Electronics",
        initial_facts={
            "purchase_channel": "retail_store",
            "goods_delivered": True,
            "alleged_defect": True,
            "defect_reported_within_warranty": True,
        },
    ),
    SyntheticScenarioManifest(
        scenario_id="scenario_d",
        scenario_letter="D",
        is_featured=False,
        title_en="Telecom/ISP Prolonged Outage & Unexpected Overbilling",
        title_bn="ব্রডব্যান্ড ইন্টারনেট একটানা ৫ দিন বিচ্ছিন্ন ও বাড়তি বিল",
        domain="Telecom / ISP",
        inputs_en="Bill Image + Support Chat Ticket",
        inputs_bn="বিলের ছবি + কাস্টমার সাপোর্ট চ্যাট",
        description_en="Image clarification, provider fields, location prerequisites and reviewed BTRC destination.",
        description_bn="স্ক্রিনশট স্পষ্টকরণ, অপারেটর টিকিট ট্র্যাকিং ও বিটিআরসি অভিযোগ প্রতিকার পথ।",
        differentiator_en="BTRC QoS directive credit clauses and formal regulator escalation.",
        differentiator_bn="বিটিআরসি কোয়ালিটি অব সার্ভিস নির্দেশিকা অনুযায়ী ক্ষতিপূরণ ও নিয়ন্ত্রক সংস্থায় আবেদন।",
        sample_story="Metro ISP connection was down for 5 days continuously in February. Provider refused bill rebate and charged full monthly fee.",
        merchant_name="Metro Net Broadband ISP",
        initial_facts={
            "telecom_provider_ticket_filed": True,
            "provider_response_overdue_or_unsatisfactory": True,
            "service_disruption_or_billing_error_documented": True,
            "issue_is_handset_hardware_only": False,
            "consumer_has_unpaid_due_prior_to_dispute": False,
        },
    ),
    SyntheticScenarioManifest(
        scenario_id="scenario_e",
        scenario_letter="E",
        is_featured=False,
        title_en="Insurance Legitimate Claim Settlement Denial",
        title_bn="স্বাস্থ্য বীমা দাবি অন্যায্যভাবে প্রত্যাখ্যান ও বিলম্ব",
        domain="Insurance",
        inputs_en="Policy Terms + Denial Letter PDF",
        inputs_bn="বীমা পলিসি শর্তাবলী + প্রত্যাখ্যান পত্র",
        description_en="Mixed page extraction, uncertain policy interpretation, precise evidence links and conditional insurer/IDRA guidance.",
        description_bn="স্ক্যান নথি পার্সিং, ৯১ দিন বিলম্বের আইনি পর্যালোচনা ও আইডিআরএ গ্রাহক সুরক্ষা সেলে আবেদন।",
        differentiator_en="Discloses staged depth; abstains from guaranteed payouts; links IDRA policyholder cell.",
        differentiator_bn="ধাপভিত্তিক বিশ্লেষণ; কোনো গ্যারান্টিযুক্ত ক্ষতিপূরণের মিথ্যা আশ্বাস নেই; আইডিআরএ অভিযোগ পথ।",
        sample_story="Submitted medical hospitalization claim of BDT 85,000 on Nov 15. Insurer rejected claim without written explanation after 95 days.",
        merchant_name="Pragati Life Insurance Ltd",
        initial_facts={
            "insurance_policy_documented": True,
            "formal_claim_submitted_to_insurer": True,
            "claim_denied_or_settlement_delayed_over_90d": True,
            "subject_of_ongoing_court_litigation": False,
            "fraudulent_misrepresentation_admitted": False,
        },
    ),
    SyntheticScenarioManifest(
        scenario_id="scenario_f",
        scenario_letter="F",
        is_featured=False,
        title_en="Ongoing Phishing & Security Credential Hazard",
        title_bn="জরুরি ফিশিং ও নিরাপত্তা ঝুঁকি",
        domain="Safety & Security",
        inputs_en="Suspicious SMS Text + Fake Portal Screenshot",
        inputs_bn="সন্দেহজনক এসএমএস + ভুয়া পেমেন্ট পোর্টাল",
        description_en="Safety-first next action, no secrets collection, preservation and independently checked provider channel.",
        description_bn="জরুরি নিরাপত্তা অগ্রাধিকার, ওটিপি/পিন সংগ্রহ সম্পূর্ণ নিষিদ্ধকরণ ও হটলাইন ১৬১২১ নির্দেশনা।",
        differentiator_en="T32 Invariant: Instant safety override, zero OTP/PIN collection, direct emergency hotline.",
        differentiator_bn="টি৩২ আইনি নিশ্চয়তা: তাৎক্ষণিক জরুরি হটলাইন অগ্রাধিকার, কোনো ওটিপি/পিন চাওয়া হয় না।",
        sample_story="Received an urgent SMS claiming my account will be suspended unless I provide OTP on a third-party link.",
        merchant_name="Unknown Phishing Sender",
        initial_facts={
            "product_presents_immediate_hazard": True,
        },
    ),
    SyntheticScenarioManifest(
        scenario_id="scenario_g",
        scenario_letter="G",
        is_featured=False,
        title_en="Public Service Grievance & Citizen Charter Delay",
        title_bn="সরকারি সেবা প্রদান বিলম্ব ও সিটিজেন চার্টার লঙ্ঘন",
        domain="Public GRS",
        inputs_en="Application Memo + Citizen Charter Directive",
        inputs_bn="আবেদন মেমো + সিটিজেন চার্টার নির্দেশিকা",
        description_en="Secondary GRS scope, court/appeal exclusions and direct official references.",
        description_bn="সরকারি সেবা সনদ (সিটিজেন চার্টার) সময়সীমা লঙ্ঘন, বিভাগীয় কর্মকর্তা ও কেন্দ্রীয় জিআরএস পথ।",
        differentiator_en="Prepares departmental GRO notice and grs.gov.bd central filing while excluding sub judice matters.",
        differentiator_bn="বিভাগীয় অভিযোগ নিষ্পত্তি কর্মকর্তা ও কেন্দ্রীয় জিআরএস পথ; বিচারাধীন মামলা থেকে স্পষ্ট বিরত থাকা।",
        sample_story="Urgent passport renewal application pending for 45 days at Regional Passport Office despite 15-day Citizen Charter commitment.",
        merchant_name="Regional Passport Office",
        initial_facts={
            "public_service_request_submitted": True,
            "citizen_charter_timeline_exceeded": True,
            "relevant_office_contacted_first": True,
            "subject_of_ongoing_court_litigation": False,
            "service_cadre_discipline_or_promotion": False,
            "alternative_statutory_appeal_pending": False,
        },
    ),
    SyntheticScenarioManifest(
        scenario_id="scenario_h",
        scenario_letter="H",
        is_featured=True,
        title_en="Living Case, Decision Changes & Adversarial Isolation",
        title_bn="চলমান কেস ট্র্যাকিং, সিদ্ধান্ত পরিবর্তন ও নিরাপত্তা প্রতিরক্ষা",
        domain="Living Case & Audit",
        inputs_en="New Merchant Response + Adversarial Prompt Injection",
        inputs_bn="বিক্রেতার নতুন উত্তর + প্রম্পট ইনজেকশন টেক্সট",
        description_en="Versioned decision changes, injection isolation, source-health caution, actual processing details.",
        description_bn="সংস্করণভিত্তিক সিদ্ধান্ত পরিবর্তন (Diff), প্রম্পট ইনজেকশন প্রতিরোধ ও স্বচ্ছ প্রসেসিং লগ।",
        differentiator_en="Demonstrates semantic decision diffs (T39) and immunity against prompt injection (T47).",
        differentiator_bn="অর্থবহ সিদ্ধান্ত পরিবর্তন (টি৩৯) এবং প্রম্পট ইনজেকশন সম্পূর্ণ ব্যর্থ হওয়ার প্রমাণ (টি৪৭)।",
        sample_story="Ordered tablet online. Later received seller reply offering partial credit note. Story contains injection test.",
        merchant_name="Pickaboo BD",
        initial_facts={
            "purchase_channel": "ecommerce",
            "goods_delivered": False,
            "promised_delivery_date_passed": True,
            "refund_already_issued": False,
            "order_cancelled_by_buyer_before_dispatch": False,
        },
    ),
]


def get_scenario_manifest(scenario_id: str) -> SyntheticScenarioManifest | None:
    return next((m for m in SCENARIO_MANIFESTS if m.scenario_id == scenario_id), None)
