/**
 * ClaimCraft BD — Humanized Formatters for Legal Pathways, Citations, Reasons & Facts.
 * Converts raw internal machine keys into crystal clear, professional Bangla and English.
 */

export const REASON_TRANSLATIONS: Record<string, { en: string; bn: string }> = {
  // GRS Public Service
  'reasons.grs.grievance_needs_submission_proof': {
    en: 'Proof of public service application submission and Citizen Charter timeline expiration required.',
    bn: 'সরকারি দপ্তরে আবেদন দাখিল ও সিটিজেন চার্টার সময়সীমা অতিক্রান্ত হওয়ার প্রমাণ প্রয়োজন।',
  },
  'reasons.grs.grievance_eligible_for_submission': {
    en: 'Eligible for formal submission to Departmental Grievance Officer and Cabinet Division GRS Portal.',
    bn: 'বিভাগীয় অভিযোগ নিষ্পত্তি কর্মকর্তা (GRO) ও ক্যাবিনেট ডিভিশন জিআরএস পোর্টালে দাখিলের যোগ্য।',
  },
  'reasons.grs.grievance_excluded_sub_judice_or_discipline': {
    en: 'Excluded from GRS: Matter is sub judice in court, involves land title disputes, or pertains to service cadre discipline.',
    bn: 'জিআরএস-এর আওতা বহির্ভূত: বিষয়টি আদালতে বিচারাধীন, জমির স্বত্ব সংক্রান্ত বা ক্যাডার শৃঙ্খলা সংক্রান্ত।',
  },
  'reasons.grs.grievance_not_supported': {
    en: 'Grievance criteria not satisfied under Cabinet Division GRS Guidelines.',
    bn: 'মন্ত্রিপরিষদ বিভাগ জিআরএস নির্দেশিকার আওতায় অভিযোগের শর্তাবলি পূরণ হয়নি।',
  },

  // Insurance
  'reasons.insurance.claim_dispute_needs_policy_or_submission': {
    en: 'Insurance policy document and evidence of formal claim submission to insurer required.',
    bn: 'বীমা পলিসি নথি এবং বীমা কোম্পানির নিকট আনুষ্ঠানিকভাবে দাবি দাখিলের প্রমাণ প্রয়োজন।',
  },
  'reasons.insurance.claim_dispute_eligible_for_idra_review': {
    en: 'Claim delayed beyond 90 days without payment; eligible for IDRA Policyholder Protection Cell review.',
    bn: 'বীমা দাবি ৯০ দিনের বেশি অনিষ্পন্ন; আইডিআরএ পলিসিহোল্ডার সুরক্ষা সেলে পর্যালোচনার যোগ্য।',
  },
  'reasons.insurance.claim_dispute_excluded_sub_judice': {
    en: 'Excluded from IDRA administrative review: Matter is subject to active court litigation.',
    bn: 'আইডিআরএ প্রশাসনিক পর্যালোচনার আওতা বহির্ভূত: বিষয়টি আদালতে বিচারাধীন।',
  },
  'reasons.insurance.claim_dispute_not_supported': {
    en: 'Insurance dispute conditions not satisfied.',
    bn: 'বীমা বিরোধ নিষ্পত্তির প্রারম্ভিক শর্ত পূরণ হয়নি।',
  },

  // E-Commerce Delivery Failure
  'reasons.shopping.delivery_failure_eligible': {
    en: 'Statutory non-delivery requirements met under Section 45. Eligible for full refund demand and DNCRP CCMS complaint.',
    bn: 'ভোক্তা অধিকার সংরক্ষণ আইন ২০০৯ (ধারা ৪৫): প্রতিশ্রুত সময়ে পণ্য সরবরাহ না করায় রিফান্ড ও ভোক্তা অধিকারে অভিযোগের শর্ত পূরণ হয়েছে।',
  },
  'reasons.shopping.delivery_failure_needs_facts': {
    en: 'Payment confirmation and proof of passed promised delivery deadline required.',
    bn: 'পণ্য ক্রয়ের মূল্য পরিশোধ ও প্রতিশ্রুত ডেলিভারি সময়সীমা উত্তীর্ণ হওয়ার তথ্য নিশ্চিত করা প্রয়োজন।',
  },
  'reasons.shopping.delivery_failure_excluded': {
    en: 'Excluded: Refund has already been credited or the order was cancelled by the buyer prior to dispatch.',
    bn: 'প্রযোজ্য নয়: পণ্যের মূল্য ইতিমধ্যে রিফান্ড করা হয়েছে অথবা ক্রেতা আগেই অর্ডার বাতিল করেছিলেন।',
  },
  'reasons.shopping.delivery_failure_not_supported': {
    en: 'Delivery failure conditions not satisfied under Section 45.',
    bn: 'ডেলিভারি ব্যর্থতা সংক্রান্ত আইনি শর্তাবলি প্রযোজ্য হয়নি।',
  },

  // Defective Goods
  'reasons.shopping.defective_goods_eligible': {
    en: 'Defect documented within warranty period. Entitled to merchant replacement notice and Section 41 compensation claim.',
    bn: 'ওয়ারেন্টির মধ্যে ত্রুটি চিহ্নিত; বিক্রেতাকে নোটিশ ও ভোক্তা অধিকার ধারা ৪১ অনুযায়ী ক্ষতিপূরণ দাবির যোগ্য।',
  },
  'reasons.shopping.defective_goods_needs_facts': {
    en: 'Proof of reporting the defect to merchant within the applicable return or warranty period required.',
    bn: 'পণ্যের ত্রুটি বিক্রেতাকে অবহিত করার প্রমাণ বা ওয়ারেন্টি দাবির তথ্য প্রয়োজন।',
  },
  'reasons.shopping.defective_goods_excluded': {
    en: 'Excluded: Damage resulted from consumer misuse or unauthorized modification.',
    bn: 'প্রযোজ্য নয়: ক্রেতার নিজস্ব অপব্যবহার বা অননুমোদিত পরিবর্তনের ফলে ত্রুটি ঘটেছে।',
  },
  'reasons.shopping.defective_goods_not_supported': {
    en: 'Defective goods remedy criteria not satisfied.',
    bn: 'ত্রুটিপূর্ণ পণ্যের আইনি প্রতিকার শর্তাবলি সন্তোষজনক নয়।',
  },

  // MFS / Fintech
  'reasons.finance.mfs_charge_needs_ticket': {
    en: 'Formal complaint ticket with MFS provider (e.g. bKash/Nagad) required before escalating to Bangladesh Bank CIPC.',
    bn: 'বাংলাদেশ ব্যাংকে যাওয়ার পূর্বে প্রথমে সংশ্লিষ্ট এমএফএস প্রোভাইডারে (বিকাশ/নগদ) আনুষ্ঠানিক অভিযোগ দাখিল আবশ্যক।',
  },
  'reasons.finance.mfs_charge_eligible_for_bb_escalation': {
    en: 'Provider resolution deadline expired without remedy. Eligible for Bangladesh Bank CIPC portal complaint.',
    bn: 'প্রোভাইডারের অভিযোগ নিষ্পত্তির সময়সীমা অতিক্রান্ত হওয়ায় বাংলাদেশ ব্যাংক সিআইপিসি সেলে অভিযোগ দাখিলের উপযুক্ত।',
  },
  'reasons.finance.mfs_charge_excluded_pin_sharing': {
    en: 'Excluded from provider liability: Disputed transaction authenticated with voluntary consumer PIN/OTP entry.',
    bn: 'প্রোভাইডারের দায় বহির্ভূত: লেনদেনটি গ্রাহকের স্বেচ্ছায় পিন বা ওটিপি প্রদানের মাধ্যমে সম্পন্ন হয়েছিল।',
  },
  'reasons.finance.mfs_charge_not_supported': {
    en: 'Unauthorized charge conditions not satisfied.',
    bn: 'অননুমোদিত লেনদেনের আইনি শর্ত পূরণ হয়নি।',
  },

  // Telecom / Broadband
  'reasons.telecom.complaint_needs_provider_ticket': {
    en: 'Formal complaint ticket with telecom/ISP provider required before BTRC consumer cell escalation.',
    bn: 'বিটিআরসিতে যাওয়ার পূর্বে সংশ্লিষ্ট ইন্টারনেট বা টেলিকম অপারেটরের নিকট আনুষ্ঠানিক অভিযোগ টিকিটের প্রমাণ প্রয়োজন।',
  },
  'reasons.telecom.complaint_eligible_for_btrc_escalation': {
    en: 'Prolonged outage or billing error exceeding QoS limits. Eligible for bill rebate demand and BTRC complaint.',
    bn: 'টানা বিভ্রাট বা অতিরিক্ত বিলিং; বিটিআরসি কোয়ালিটি অব সার্ভিস নির্দেশিকা অনুযায়ী বিল রিবেট ও রেগুলেটর অভিযোগের যোগ্য।',
  },
  'reasons.telecom.complaint_excluded_hardware_or_default': {
    en: 'Excluded: Disruption caused by consumer router hardware defect or unpaid arrears preceding outage.',
    bn: 'প্রযোজ্য নয়: গ্রাহকের নিজস্ব রাউটার ত্রুটি বা পূর্বের বকেয়া বিলের কারণে সংযোগ স্থগিত হয়েছিল।',
  },
  'reasons.telecom.complaint_not_supported': {
    en: 'Telecom QoS criteria not satisfied.',
    bn: 'টেলিকম সেবার মান লঙ্ঘন সংক্রান্ত শর্তাবলি পূরণ হয়নি।',
  },

  // Safety Hazard
  'reasons.safety.immediate_hotline_alert': {
    en: 'Immediate safety hazard detected. Mandatory direct alert via DNCRP Hotline 16121 and local administration.',
    bn: 'তাৎক্ষণিক স্বাস্থ্য বা অগ্নিঝুঁকি শনাক্ত; অবিলম্বে জাতীয় ভোক্তা অধিকার হটলাইন ১৬১২১-এ জানানোর নির্দেশনা।',
  },
  'reasons.safety.needs_hazard_facts': {
    en: 'Physical inspection or lab hazard report facts required.',
    bn: 'পণ্যটির ক্ষতিকর উপাদান বা শারীরিক বিপদের বাস্তব বিবরণ প্রয়োজন।',
  },
  'reasons.safety.no_hazard_identified': {
    en: 'No immediate physical hazard identified in current case facts.',
    bn: 'বর্তমান তথ্যে কোনো জরুরি শারীরিক বিপদের প্রমাণ পাওয়া যায়নি।',
  },
};

export function formatReason(reasonKey: string, isBangla: boolean): string {
  if (!reasonKey) return '';
  const match = REASON_TRANSLATIONS[reasonKey];
  if (match) {
    return isBangla ? match.bn : match.en;
  }
  // If it's a raw dotted string without direct match, format it nicely
  if (reasonKey.startsWith('reasons.')) {
    const parts = reasonKey.replace('reasons.', '').split('.');
    const label = parts[parts.length - 1].replace(/_/g, ' ');
    return isBangla
      ? `অতিরিক্ত আইনি তথ্য প্রয়োজন: ${label}`
      : `Additional statutory facts required: ${label}`;
  }
  return reasonKey;
}

export function formatStatutoryCitation(citation: string, isBangla: boolean): string {
  if (!citation) return '';
  const clean = citation.replace(/^@\s*/, '').trim();

  if (clean.includes('grs_guidelines_2015') || clean.includes('grs_guidelines')) {
    return isBangla
      ? 'মন্ত্রিপরিষদ বিভাগ জিআরএস নির্দেশিকা ২০১৫ (অনুচ্ছেদ ৪.০)'
      : 'Cabinet Division GRS Guidelines 2015 § 4.0';
  }
  if (clean.includes('citizen_charter_directive')) {
    return isBangla
      ? 'সিটিজেন চার্টার বাস্তবায়ন নির্দেশিকা ২০১৮'
      : 'Citizen Charter Directive 2018';
  }
  if (clean.includes('crpa2009:sec:45') || clean.includes('consumers_right_protection_act_2009:sec:45')) {
    return isBangla
      ? 'ভোক্তা অধিকার সংরক্ষণ আইন ২০০৯ (ধারা ৪৫ - পণ্য প্রদানে ব্যর্থতা)'
      : "Consumers' Right Protection Act 2009 (Sec 45 - Non-Delivery)";
  }
  if (clean.includes('crpa2009:sec:76') || clean.includes('consumers_right_protection_act_2009:sec:76')) {
    return isBangla
      ? 'ভোক্তা অধিকার সংরক্ষণ আইন ২০০৯ (ধারা ৭৬ - সিসিএমএস অভিযোগ দায়ের)'
      : "Consumers' Right Protection Act 2009 (Sec 76 - CCMS Filing)";
  }
  if (clean.includes('crpa2009:sec:41') || clean.includes('consumers_right_protection_act_2009:sec:41')) {
    return isBangla
      ? 'ভোক্তা অধিকার সংরক্ষণ আইন ২০০৯ (ধারা ৪১ - ভেজাল/ত্রুটিপূর্ণ পণ্য)'
      : "Consumers' Right Protection Act 2009 (Sec 41 - Defective Goods)";
  }
  if (clean.includes('crpa2009:sec:60') || clean.includes('consumers_right_protection_act_2009:sec:60')) {
    return isBangla
      ? 'ভোক্তা অধিকার সংরক্ষণ আইন ২০০৯ (ধারা ৬০ - ৩০ দিনের তামাদি সময়সীমা)'
      : "Consumers' Right Protection Act 2009 (Sec 60 - 30-Day Limitation)";
  }
  if (clean.includes('insurance_act_2010')) {
    return isBangla
      ? 'বীমা আইন ২০১০ (ধারা ৭২ - দাবি নিষ্পত্তি বাধ্যবাধকতা)'
      : 'Insurance Act 2010 (Sec 72 - Claim Settlement)';
  }
  if (clean.includes('idra_dispute_resolution') || clean.includes('idra:dispute_resolution')) {
    return isBangla
      ? 'আইডিআরএ বিরোধ নিষ্পত্তি বিধিমালা ২০১৯'
      : 'IDRA Dispute Resolution Regulations 2019';
  }
  if (clean.includes('mfs_regulations_2022') || clean.includes('mfs_regulations')) {
    return isBangla
      ? 'বাংলাদেশ ব্যাংক এমএফএস রেগুলেশন ২০২২ ও সিআইপিসি ফ্রেমওয়ার্ক'
      : 'Bangladesh Bank MFS Regulations 2022 & CIPC Framework';
  }
  if (clean.includes('btrc_telecom_qos') || clean.includes('btrc:directive')) {
    return isBangla
      ? 'বিটিআরসি টেলিকম কোয়ালিটি অব সার্ভিস (QoS) নির্দেশিকা'
      : 'BTRC Telecom Quality of Service (QoS) Directives';
  }

  // Fallback: clean up colons and underscores
  return clean.replace(/:/g, ' ').replace(/_/g, ' ');
}

export function formatIssueType(issueType: string, isBangla: boolean): string {
  switch (issueType) {
    case 'ecommerce_delivery_failure':
      return isBangla
        ? 'ভোক্তা অধিকার সংরক্ষণ অধিদপ্তর (DNCRP) — ধারা ৪৫ ও ৭৬ (পণ্য ডেলিভারি ব্যর্থতা)'
        : 'DNCRP CCMS: Non-Delivery Complaint (Sec 45 & 76)';
    case 'defective_goods':
      return isBangla
        ? 'ত্রুটিপূর্ণ পণ্য প্রতিকার: বিক্রেতা রিপ্লেসমেন্ট নোটিশ ও DNCRP অভিযোগ (ধারা ৪১)'
        : 'Defective Goods Remedy: Merchant Notice & CCMS Complaint (Sec 41)';
    case 'mfs_unauthorized_charge':
      return isBangla
        ? 'আর্থিক বিরোধ: এমএফএস প্রোভাইডার গ্রিভেন্স ও বাংলাদেশ ব্যাংক CIPC'
        : 'Financial Dispute: MFS Provider Grievance & BB CIPC';
    case 'telecom_billing_and_outage':
      return isBangla
        ? 'টেলিকম ও ব্রডব্যান্ড বিভ্রাট: অপারেটর বিল রিবেট ও BTRC সেল'
        : 'Telecom/ISP Dispute: Provider Bill Rebate & BTRC Complaint';
    case 'insurance_claim_dispute':
      return isBangla
        ? 'বীমা দাবি বিরোধ: কোম্পানি পুনর্বিবেচনা আবেদন ও আইডিআরএ সেল'
        : 'Insurance Dispute: Insurer Reconsideration & IDRA Grievance';
    case 'public_service_grievance':
      return isBangla
        ? 'সরকারি সেবা সনদ বিলম্ব: সিটিজেন চার্টার ও কেন্দ্রীয় জিআরএস (GRS)'
        : 'Public Service Grievance: Citizen Charter & Cabinet Division GRS';
    case 'product_safety_hazard':
      return isBangla
        ? 'জরুরি ভোক্তা অধিকার হটলাইন ১৬১২১ অ্যালার্ট ও নিরাপত্তা নোটিশ'
        : 'Emergency Safety Alert: DNCRP Hotline 16121';
    default:
      return issueType ? issueType.replace(/_/g, ' ') : '';
  }
}

export function formatRuleBadge(ruleId: string, isBangla: boolean): string {
  if (ruleId.includes('ecommerce_delivery_failure')) {
    return isBangla ? 'ভোক্তা অধিকার সংরক্ষণ আইন ২০০৯ • ধারা ৪৫' : 'CRPA 2009 • Section 45';
  }
  if (ruleId.includes('defective_goods')) {
    return isBangla ? 'ভোক্তা অধিকার সংরক্ষণ আইন ২০০৯ • ধারা ৪১' : 'CRPA 2009 • Section 41';
  }
  if (ruleId.includes('mfs_unauthorized_charge')) {
    return isBangla ? 'বাংলাদেশ ব্যাংক ফিনটেক ফ্রেমওয়ার্ক ২০২২' : 'Bangladesh Bank MFS Framework 2022';
  }
  if (ruleId.includes('product_safety_hazard') || ruleId.includes('hazardous_product')) {
    return isBangla ? 'জাতীয় ভোক্তা অধিকার হটলাইন ১৬১২১' : 'DNCRP Safety Hotline 16121';
  }
  if (ruleId.includes('public_service_grievance')) {
    return isBangla ? 'মন্ত্রিপরিষদ বিভাগ জিআরএস ফ্রেমওয়ার্ক' : 'Cabinet Division GRS Framework';
  }
  if (ruleId.includes('insurance_claim_dispute')) {
    return isBangla ? 'বীমা উন্নয়ন ও নিয়ন্ত্রণ কর্তৃপক্ষ (IDRA)' : 'IDRA Insurance Regulatory Guidelines';
  }
  if (ruleId.includes('telecom_billing_and_outage')) {
    return isBangla ? 'বিটিআরসি টেলিকম রেগুলেশন (BTRC)' : 'BTRC Telecom Quality Directives';
  }
  return ruleId.replace(/^bd\./, '').replace(/_/g, ' ');
}

export function formatRouteStatus(status: string, isBangla: boolean): {
  label: string;
  variant: 'brand' | 'warning' | 'danger' | 'neutral';
} {
  switch (status?.toLowerCase()) {
    case 'supported':
      return {
        label: isBangla ? '✅ আইনিভাবে সক্রিয় ও কার্যকর' : '✅ Statutorily Eligible & Active',
        variant: 'brand',
      };
    case 'needs_facts':
      return {
        label: isBangla ? 'ℹ️ তথ্যের স্পষ্টীকরণ প্রয়োজন' : 'ℹ️ Clarifying Facts Needed',
        variant: 'warning',
      };
    case 'source_caution':
      return {
        label: isBangla ? '⚠️ আইনি সূত্র পুনর্বিবেচনাধীন' : '⚠️ Source Under Review',
        variant: 'warning',
      };
    case 'excluded':
      return {
        label: isBangla ? '⛔ আইনি শর্তের বাইরে (Excluded)' : '⛔ Legally Excluded',
        variant: 'danger',
      };
    case 'not_supported':
      return {
        label: isBangla ? '❌ বর্তমান তথ্যে প্রযোজ্য নয়' : '❌ Not Applicable to Case',
        variant: 'neutral',
      };
    default:
      return { label: status, variant: 'neutral' };
  }
}

export const FACT_LABELS: Record<string, { en: string; bn: string }> = {
  goods_delivered: {
    en: 'Goods physically delivered to consumer',
    bn: 'পণ্য কি ক্রেতার হাতে পৌঁছানো হয়েছিল',
  },
  promised_delivery_date_passed: {
    en: 'Promised delivery date expired without delivery',
    bn: 'প্রতিশ্রুত ডেলিভারি সময়সীমা উত্তীর্ণ হয়েছে',
  },
  refund_already_issued: {
    en: 'Refund has already been credited to buyer',
    bn: 'টাকা ইতিমধ্যে রিফান্ড দেওয়া হয়েছে',
  },
  order_cancelled_by_buyer_before_dispatch: {
    en: 'Order cancelled by buyer prior to dispatch',
    bn: 'পণ্য পাঠানোর আগেই ক্রেতা নিজে অর্ডার বাতিল করেছিলেন',
  },
  goods_received_defective: {
    en: 'Delivered goods were broken, defective, or counterfeit',
    bn: 'ডেলিভারিকৃত পণ্য ভাঙা, ত্রুটিপূর্ণ বা নকল ছিল',
  },
  user_inflicted_damage: {
    en: 'Damage caused by consumer misuse or unauthorized repair',
    bn: 'ক্রেতার নিজস্ব অপব্যবহার বা অননুমোদিত মেরামতে ত্রুটি',
  },
  seller_notified_within_warranty: {
    en: 'Defect formally reported to seller within warranty',
    bn: 'ওয়ারেন্টি সময়সীমার মধ্যে বিক্রেতাকে অবহিত করা হয়েছে',
  },
  provider_ticket_filed: {
    en: 'Formal dispute ticket filed with service provider/merchant',
    bn: 'সেলার বা প্রোভাইডারের কাস্টমার কেয়ারে আনুষ্ঠানিক অভিযোগ দাখিল',
  },
  product_presents_immediate_hazard: {
    en: 'Product presents immediate physical, toxic, or fire danger',
    bn: 'পণ্যটি জরুরি অগ্নিঝুঁকি, বিষাক্ততা বা শারীরিক ক্ষতির কারণ',
  },
  purchase_channel: {
    en: 'Purchase Channel (E-Commerce/In-Person)',
    bn: 'পণ্য ক্রয়ের মাধ্যম (অনলাইন/ই-কমার্স)',
  },
  transaction_unauthorized: {
    en: 'Financial transaction was unauthorized or fraudulent',
    bn: 'লেনদেনটি অননুমোদিত বা প্রতারণামূলক ছিল',
  },
};

export function formatFactName(factName: string, isBangla: boolean): string {
  if (!factName) return '';
  const match = FACT_LABELS[factName];
  if (match) {
    return isBangla ? match.bn : match.en;
  }
  return factName.replace(/_/g, ' ');
}

export function formatBdtMoney(minorUnits: number, locale = 'en'): string {
  const isBangla = locale === 'bn';
  const val = (minorUnits / 100).toLocaleString(isBangla ? 'bn-BD' : 'en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
  return isBangla ? `৳${val}` : `৳${val} BDT`;
}

export function formatFactLabel(factName: string, locale = 'en'): string {
  const isBangla = locale === 'bn';
  return formatFactName(factName, isBangla);
}
