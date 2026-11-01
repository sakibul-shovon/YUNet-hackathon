"""Governed Canonical Statutory & Procedural Provisions for ClaimCraft BD.

Contains verified provisions for:
1. Consumers' Right Protection Act, 2009 (CRPA 2009 / ভোক্তা-অধিকার সংরক্ষণ আইন, ২০০৯)
2. Bangladesh Bank Customer Interests Protection Centre (BB CIPC) Procedure

All provisions maintain:
- Hierarchical structure (Act -> Section -> Subsection -> Proviso/Exception)
- Long Bengali clauses with untruncated qualification and proviso clauses ("তবে শর্ত থাকে যে...")
- Exact section aliases for bilingual lookup (Latin/Bengali numerals and prefixes)
- Stable immutable citation handles
"""

from typing import Any

CANONICAL_PROVISIONS: list[dict[str, Any]] = [
    # -------------------------------------------------------------------------
    # CRPA 2009: Section 45
    # -------------------------------------------------------------------------
    {
        "citation_handle": "crpa2009:sec:45",
        "source_id": "bd_crpa_2009",
        "provision_path": "sec:45",
        "section_number": "45",
        "section_bn": "৪৫",
        "title_en": "Punishment for failure to sell or deliver promised goods or services",
        "title_bn": "প্রতিশ্রুত পণ্য বা সেবা যথাযথভাবে বিক্রয় বা সরবরাহ না করার দণ্ড",
        "parent_path": None,
        "document_type": "statute",
        "canonical_text_en": (
            "If any person, having accepted the fixed or promised price or part of the price of any goods, "
            "or having accepted part of the promised consideration for the purpose of rendering a service, "
            "fails to properly sell or deliver the promised goods or provide the service, he shall be punished "
            "with imprisonment for a term not exceeding one year, or with a fine not exceeding fifty thousand taka, "
            "or with both: Provided that where delivery or performance becomes impossible due to unavoidable or "
            "reasonable causes, the full consideration paid must be refunded to the consumer without delay."
        ),
        "canonical_text_bn": (
            "কোনো ব্যক্তি কোনো পণ্যের নির্ধারিত বা প্রতিশ্রুত মূল্য বা পণ্যের মূল্যের অংশবিশেষ গ্রহণ করিয়া "
            "বা সেবা প্রদানের উদ্দেশ্যে প্রতিশ্রুত সেবা মূল্যের অংশবিশেষ গ্রহণ করিয়া যদি প্রতিশ্রুত পণ্য বা সেবা "
            "যথাযথভাবে বিক্রয় বা সরবরাহ না করেন, তাহা হইলে তিনি অনধিক ১ (এক) বৎসর কারাদণ্ড, বা অনধিক ৫০,০০০ (পঞ্চাশ হাজার) "
            "টাকা অর্থদণ্ড, বা উভয় দণ্ডে দণ্ডিত হইবেন: তবে শর্ত থাকে যে, কোনো অনিবার্য কারণবশত বা যুক্তিসঙ্গত কারণে সরবরাহ "
            "সম্ভব না হইলে অনতিবিলম্বে ক্রেতাকে সমুদয় অর্থ ফেরত প্রদান করিতে হইবে।"
        ),
        "qualifications_and_exceptions": [
            "তবে শর্ত থাকে যে, কোনো অনিবার্য কারণবশত বা যুক্তিসঙ্গত কারণে সরবরাহ সম্ভব না হইলে অনতিবিলম্বে ক্রেতাকে সমুদয় অর্থ ফেরত প্রদান করিতে হইবে।"
        ],
        "key_definitions": {
            "promised_goods": "Goods agreed upon sale or for which consideration was received",
            "consideration": "Price, advance payment, or partial payment in BDT",
            "unjustified_default": "Failure to deliver within promised schedule without refund",
        },
        "penalties": {
            "imprisonment_max": "1 year",
            "fine_bdt_max": 50000,
        },
        "aliases": [
            "sec:45",
            "sec 45",
            "section 45",
            "section:45",
            "ধারা ৪৫",
            "ধারা:৪৫",
            "৪৫ ধারা",
            "crpa:45",
            "crpa:sec:45",
            "crpa2009:45",
        ],
        "effective_from": "2009-04-06",
        "effective_to": None,
    },
    # -------------------------------------------------------------------------
    # CRPA 2009: Section 45(2) Subclause (Refund and Timeline Proviso)
    # -------------------------------------------------------------------------
    {
        "citation_handle": "crpa2009:sec:45(2)",
        "source_id": "bd_crpa_2009",
        "provision_path": "sec:45(2)",
        "section_number": "45(2)",
        "section_bn": "৪৫(২)",
        "title_en": "Mandatory refund proviso upon failure to supply",
        "title_bn": "সরবরাহে ব্যর্থতায় অবিলম্বে মূল্য ফেরত প্রদানের বাধ্যবাধকতা",
        "parent_path": "sec:45",
        "document_type": "statute",
        "canonical_text_en": (
            "Provided that where delivery of goods or rendering of services becomes impossible due to unavoidable "
            "or reasonable causes, the seller or service provider shall immediately refund the entire amount of money "
            "received to the buyer or consumer without any deduction."
        ),
        "canonical_text_bn": (
            "তবে শর্ত থাকে যে, কোনো অনিবার্য কারণবশত বা যুক্তিসঙ্গত কারণে পণ্য বা সেবা সরবরাহ সম্ভব না হইলে "
            "অনতিবিলম্বে ক্রেতা বা ভোক্তাকে গৃহীত সমুদয় অর্থ ফেরত প্রদান করিতে হইবে।"
        ),
        "qualifications_and_exceptions": [
            "অনতিবিলম্বে ক্রেতাকে সমুদয় অর্থ ফেরত প্রদান করিতে হইবে (ব্যতিক্রমহীন সম্পূর্ণ মূল্য ফেরত)।"
        ],
        "key_definitions": {
            "immediate_refund": "Refund must be issued promptly upon realization of delivery failure",
        },
        "penalties": None,
        "aliases": [
            "sec:45(2)",
            "sec 45(2)",
            "section 45(2)",
            "section:45(2)",
            "ধারা ৪৫(২)",
            "ধারা:৪৫(২)",
            "৪৫(২) ধারা",
            "ধারা ৪৫ এর ২",
            "crpa:45(2)",
            "crpa:sec:45(2)",
        ],
        "effective_from": "2009-04-06",
        "effective_to": None,
    },
    # -------------------------------------------------------------------------
    # CRPA 2009: Section 41 (Adulteration and Prohibited Sale)
    # -------------------------------------------------------------------------
    {
        "citation_handle": "crpa2009:sec:41",
        "source_id": "bd_crpa_2009",
        "provision_path": "sec:41",
        "section_number": "41",
        "section_bn": "৪১",
        "title_en": "Punishment for selling adulterated or hazardous goods",
        "title_bn": "ভেজাল বা ক্ষতিকর পণ্য বিক্রয়ের দণ্ড",
        "parent_path": None,
        "document_type": "statute",
        "canonical_text_en": (
            "If any person sells or offers for sale any goods adulterated with harmful ingredients or noxious materials, "
            "or any goods unfit for human consumption, he shall be punished with imprisonment for a term not exceeding "
            "three years, or with a fine not exceeding two lakh taka, or with both."
        ),
        "canonical_text_bn": (
            "কোনো ব্যক্তি মানুষের জীবনের জন্য ক্ষতিকর বা স্বাস্থ্যের জন্য হানিকর কোনো দ্রব্য মিশ্রিত বা ভেজালযুক্ত কোনো "
            "পণ্য বিক্রয় করিলে বা বিক্রয়ের প্রস্তাব করিলে তিনি অনধিক ৩ (তিন) বৎসর কারাদণ্ড, বা অনধিক ২,০০,০০০ (দুই লাখ) "
            "টাকা অর্থদণ্ড, বা উভয় দণ্ডে দণ্ডিত হইবেন।"
        ),
        "qualifications_and_exceptions": [
            "ঔষধ বা বিশেষ অনুমোদিত সামগ্রীর ক্ষেত্রে প্রযোজ্য বিশেষ আইনের বিধানসমূহ ক্ষুণ্ণ হইবে না।"
        ],
        "key_definitions": {
            "adulterated_goods": "Goods containing unwholesome, hazardous, or prohibited foreign ingredients",
        },
        "penalties": {
            "imprisonment_max": "3 years",
            "fine_bdt_max": 200000,
        },
        "aliases": [
            "sec:41",
            "sec 41",
            "section 41",
            "section:41",
            "ধারা ৪১",
            "ধারা:৪১",
            "৪১ ধারা",
            "crpa:41",
        ],
        "effective_from": "2009-04-06",
        "effective_to": None,
    },
    # -------------------------------------------------------------------------
    # CRPA 2009: Section 44 (Deceptive Advertising)
    # -------------------------------------------------------------------------
    {
        "citation_handle": "crpa2009:sec:44",
        "source_id": "bd_crpa_2009",
        "provision_path": "sec:44",
        "section_number": "44",
        "section_bn": "৪৪",
        "title_en": "Punishment for false advertisement and deceiving consumers",
        "title_bn": "মিথ্যা বিজ্ঞাপন দ্বারা ক্রেতা সাধারণকে প্রতারিত করার দণ্ড",
        "parent_path": None,
        "document_type": "statute",
        "canonical_text_en": (
            "If any person deceives the general purchasing public by false or untruthful advertisement regarding the "
            "quality, quantity, purity, or standard of goods or services, he shall be punished with imprisonment for "
            "a term not exceeding one year, or with a fine not exceeding two lakh taka, or with both."
        ),
        "canonical_text_bn": (
            "কোনো ব্যক্তি কোনো পণ্য বা সেবা সম্পর্কে অসত্য বা মিথ্যা বিজ্ঞাপন দ্বারা ক্রেতা সাধারণকে প্রতারিত করিলে "
            "তিনি অনধিক ১ (এক) বৎসর কারাদণ্ড, বা অনধিক ২,০০,০০০ (দুই লাখ) টাকা অর্থদণ্ড, বা উভয় দণ্ডে দণ্ডিত হইবেন।"
        ),
        "qualifications_and_exceptions": [],
        "key_definitions": {
            "false_advertisement": "Untruthful claims or representation concerning product quality or specifications",
        },
        "penalties": {
            "imprisonment_max": "1 year",
            "fine_bdt_max": 200000,
        },
        "aliases": [
            "sec:44",
            "sec 44",
            "section 44",
            "section:44",
            "ধারা ৪৪",
            "ধারা:৪৪",
            "৪৪ ধারা",
            "crpa:44",
        ],
        "effective_from": "2009-04-06",
        "effective_to": None,
    },
    # -------------------------------------------------------------------------
    # CRPA 2009: Section 60 (Limitation Period - 30 Days)
    # -------------------------------------------------------------------------
    {
        "citation_handle": "crpa2009:sec:60",
        "source_id": "bd_crpa_2009",
        "provision_path": "sec:60",
        "section_number": "60",
        "section_bn": "৬০",
        "title_en": "Limitation period for filing consumer complaints (30 Days)",
        "title_bn": "অভিযোগ দায়েরের তামাদি বা সময়সীমা (৩০ দিন)",
        "parent_path": None,
        "document_type": "statute",
        "canonical_text_en": (
            "No complaint shall be entertained under this Act unless a consumer or complainant files the complaint in writing "
            "to the Director General or an authorized officer within thirty days from the date of the occurrence of the "
            "offense or the date when the cause of action arose."
        ),
        "canonical_text_bn": (
            "এই আইনের অধীন কোনো অপরাধ সংঘটিত হইবার বা কারণ উদ্ভব হইবার তারিখ হইতে ৩০ (ত্রিশ) দিনের মধ্যে মহাপরিচালক বা "
            "তদকর্তৃক ক্ষমতাপ্রাপ্ত কোনো কর্মকর্তার নিকট কোনো ভোক্তা বা অভিযোগকারী লিখিতভাবে অভিযোগ দায়ের না করিলে উক্ত "
            "অভিযোগ গ্রহণযোগ্য হইবে না।"
        ),
        "qualifications_and_exceptions": [
            "৩০ দিনের সময়সীমা কঠোরভাবে বাধ্যতামূলক; কারণ উদ্ভব হইবার ৩০ দিন অতিক্রান্ত হইলে সাধারণ অভিযোগ তামাদি বলিয়া বিবেচিত হইবে।"
        ],
        "key_definitions": {
            "limitation_period": "30 calendar days from the date cause of action arose",
            "written_complaint": "Complaint submitted in prescribed writing with supporting evidence",
        },
        "penalties": None,
        "aliases": [
            "sec:60",
            "sec 60",
            "section 60",
            "section:60",
            "ধারা ৬০",
            "ধারা:৬০",
            "৬০ ধারা",
            "তামাদি ৬০",
            "crpa:60",
        ],
        "effective_from": "2009-04-06",
        "effective_to": None,
    },
    # -------------------------------------------------------------------------
    # CRPA 2009: Section 76 (Complainant Reward - 25%)
    # -------------------------------------------------------------------------
    {
        "citation_handle": "crpa2009:sec:76",
        "source_id": "bd_crpa_2009",
        "provision_path": "sec:76",
        "section_number": "76",
        "section_bn": "৭৬",
        "title_en": "Disbursement of 25% collected fine to the complainant",
        "title_bn": "অভিযোগকারীকে আদায়কৃত অর্থদণ্ডের শতকরা ২৫ ভাগ প্রদান",
        "parent_path": None,
        "document_type": "statute",
        "canonical_text_en": (
            "When any administrative fine is imposed and realized under Section 70 of this Act, twenty-five percent "
            "of the realized fine amount shall be paid immediately to the complainant who lodged the complaint."
        ),
        "canonical_text_bn": (
            "এই আইনের ধারা ৭০ এর অধীন কোনো অপরাধের জন্য আরোপিত অর্থদণ্ড আদায় করা হইলে, আদায়কৃত অর্থদণ্ডের শতকরা ২৫ "
            "(পঁচিশ) ভাগ অর্থ তাৎক্ষণিকভাবে অভিযোগকারীকে প্রদান করিতে হইবে।"
        ),
        "qualifications_and_exceptions": [
            "অর্থদণ্ড অবশ্যই আনুষ্ঠানিকভাবে আদায় বা উসুল হইতে হইবে; শুধুমাত্র জরিমানা ধার্য হওয়াই অর্থপ্রাপ্তির নিশ্চয়তা নহে।"
        ],
        "key_definitions": {
            "complainant_share": "25% of fine realized and collected from violator",
        },
        "penalties": None,
        "aliases": [
            "sec:76",
            "sec 76",
            "section 76",
            "section:76",
            "ধারা ৭৬",
            "ধারা:৭৬",
            "৭৬ ধারা",
            "পুরস্কার ৭৬",
            "crpa:76",
        ],
        "effective_from": "2009-04-06",
        "effective_to": None,
    },
    # -------------------------------------------------------------------------
    # BB CIPC: Stage 1 (Provider Grievance)
    # -------------------------------------------------------------------------
    {
        "citation_handle": "bb_cipc:stage:provider_grievance",
        "source_id": "bb_cipc_procedure",
        "provision_path": "stage:provider_grievance",
        "section_number": "stage-1",
        "section_bn": "স্তর-১",
        "title_en": "Mandatory Stage 1: Grievance submission to bank or MFS provider",
        "title_bn": "বাধ্যতামূলক স্তর ১: ব্যাংক বা এমএফএস প্রতিষ্ঠানের নিকট অভিযোগ দায়ের",
        "parent_path": None,
        "document_type": "procedure_guide",
        "canonical_text_en": (
            "An aggrieved financial consumer must first submit a formal grievance directly to the concerned scheduled bank, "
            "financial institution, or Mobile Financial Service (MFS) provider (e.g., bKash, Nagad, Rocket). The consumer "
            "must obtain and preserve a written ticket or tracking reference number. The provider is mandated to resolve "
            "or formally respond in writing within 10 business days."
        ),
        "canonical_text_bn": (
            "আক্রান্ত গ্রাহককে সর্বপ্রথম সংশ্লিষ্ট তফসিলি ব্যাংক বা মোবাইল ফাইন্যান্সিয়াল সার্ভিস (এমএফএস) প্রতিষ্ঠানের নিকট "
            "আনুষ্ঠানিকভাবে অভিযোগ দায়ের করিতে হইবে এবং অভিযোগ গ্রহণের ট্র্যাকিং বা টিকিট নম্বর সংরক্ষণ করিতে হইবে। সংশ্লিষ্ট "
            "প্রতিষ্ঠানকে অনধিক ১০ (দশ) কার্যদিবসের মধ্যে অভিযোগ নিষ্পত্তি বা লিখিত ব্যাখ্যা প্রদান করিতে হইবে।"
        ),
        "qualifications_and_exceptions": [
            "ব্যাংক বা এমএফএস প্রতিষ্ঠানের টিকিট নম্বর ছাড়া সরাসরি বাংলাদেশ ব্যাংকে প্রেরিত অভিযোগ সাধারণত প্রাথমিক পর্যালোচনায় প্রতিষ্ঠানে ফেরত পাঠানো হয়।"
        ],
        "key_definitions": {
            "provider_ticket": "Official grievance ticket reference number issued by bank or MFS",
            "resolution_window": "10 business days for standard domestic disputes",
        },
        "penalties": None,
        "aliases": [
            "stage:1",
            "stage:provider_grievance",
            "bb:stage1",
            "স্তর ১",
            "স্তর-১",
            "ব্যাংক অভিযোগ",
        ],
        "effective_from": "2022-01-01",
        "effective_to": None,
    },
    # -------------------------------------------------------------------------
    # BB CIPC: Stage 2 (Escalation to Bangladesh Bank CIPC)
    # -------------------------------------------------------------------------
    {
        "citation_handle": "bb_cipc:stage:cipc_escalation",
        "source_id": "bb_cipc_procedure",
        "provision_path": "stage:cipc_escalation",
        "section_number": "stage-2",
        "section_bn": "স্তর-২",
        "title_en": "Stage 2: Formal escalation to Bangladesh Bank CIPC",
        "title_bn": "স্তর ২: বাংলাদেশ ব্যাংক সিআইপিসি-তে আনুষ্ঠানিক অভিযোগ উত্থাপন",
        "parent_path": "stage:provider_grievance",
        "document_type": "procedure_guide",
        "canonical_text_en": (
            "If the scheduled bank or MFS provider fails to resolve the grievance within 10 business days, or provides "
            "an unsatisfactory resolution, the consumer may escalate the complaint directly to the Customer Interests "
            "Protection Centre (CIPC), Financial Integrity and Customer Services Department (FICSD), Bangladesh Bank. "
            "The submission must include the provider ticket number and proof of prior grievance submission."
        ),
        "canonical_text_bn": (
            "ব্যাংক বা এমএফএস প্রতিষ্ঠান ১০ কার্যদিবসের মধ্যে সন্তোষজনক সমাধান না দিলে বা কোনো উত্তর না দিলে, গ্রাহক "
            "বাংলাদেশ ব্যাংকের ফাইন্যান্সিয়াল ইন্টিগ্রিটি অ্যান্ড কাস্টমার সার্ভিসেস ডিপার্টমেন্ট (FICSD)-এর অধীন গ্রাহক "
            "স্বার্থ সংরক্ষণ কেন্দ্র (CIPC)-এ সরাসরি অভিযোগ দায়ের করিতে পারিবেন। আবেদনে পূর্ববর্তী টিকিট নম্বর ও সংশ্লিষ্ট "
            "প্রমাণাদি সংযুক্ত করা বাধ্যতামূলক।"
        ),
        "qualifications_and_exceptions": [
            "আদালতে বিচারাধীন বিষয় বা আইনি মোকদ্দমা সংশ্লিষ্ট বিরোধ সিআইপিসি-এর আওতাভুক্ত নহে।"
        ],
        "key_definitions": {
            "cipc_portal": "Online CIPC portal bb.org.bd and email cipc.ficsd@bb.org.bd",
            "toll_free_hotline": "16236 (Bangladesh Bank CIPC)",
        },
        "penalties": None,
        "aliases": [
            "stage:2",
            "stage:cipc_escalation",
            "bb:stage2",
            "স্তর ২",
            "স্তর-২",
            "সিআইপিসি অভিযোগ",
            "বাংলাদেশ ব্যাংক অভিযোগ",
        ],
        "effective_from": "2022-01-01",
        "effective_to": None,
    },
]

