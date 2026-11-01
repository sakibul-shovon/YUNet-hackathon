'use client';

import React, { useState } from 'react';
import {
  Calculator,
  Coins,
  ShieldCheck,
  Award,
  ArrowRight,
  Info,
  Scale,
  Sparkles,
  ChevronDown,
  ChevronUp,
} from 'lucide-react';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { cn } from '@/lib/utils';

interface ViolationTier {
  id: string;
  section: string;
  titleEn: string;
  titleBn: string;
  minFine: number;
  maxFine: number;
  prisonYears: number;
  descriptionEn: string;
  descriptionBn: string;
}

const VIOLATION_TIERS: ViolationTier[] = [
  {
    id: 's45-false-promise',
    section: 'ধারা ৪৫ (Section 45)',
    titleEn: 'Failure to Deliver as Promised / Delivery Fraud',
    titleBn: 'প্রতিশ্রুত পণ্য প্রদানে ব্যর্থতা ও প্রতারণা',
    minFine: 20000,
    maxFine: 100000,
    prisonYears: 1,
    descriptionEn: 'Failing to deliver agreed product/service after receiving payment or delivering substandard counterfeit items.',
    descriptionBn: 'টাকা গ্রহণ করে প্রতিশ্রুত পণ্য প্রদানে ব্যর্থ হওয়া বা সম্পূর্ণ ভিন্ন/নকল পণ্য পাঠানো।',
  },
  {
    id: 's41-counterfeit',
    section: 'ধারা ৪১ (Section 41)',
    titleEn: 'Selling Counterfeit / Adulterated Goods',
    titleBn: 'নকল, ভেজাল বা মেয়াদোত্তীর্ণ পণ্য বিক্রয়',
    minFine: 50000,
    maxFine: 200000,
    prisonYears: 2,
    descriptionEn: 'Selling cloned master copies or fake electronics passed off as authentic originals.',
    descriptionBn: 'অরিজিনাল বলে নকল বা মাস্টার কপি গ্যাজেট/পোশাক ভোক্তার নিকট গছিয়ে দেওয়া।',
  },
  {
    id: 's40-overcharging',
    section: 'ধারা ৪০ (Section 40)',
    titleEn: 'Charging Above Fixed/Stated MRP',
    titleBn: 'নির্ধারিত মূল্যের অতিরিক্ত মূল্য আদায়',
    minFine: 10000,
    maxFine: 50000,
    prisonYears: 1,
    descriptionEn: 'Collecting additional extortionate delivery or gateway charges without prior agreement.',
    descriptionBn: 'অনলাইন তালিকাভুক্ত মূল্যের চেয়ে অতিরিক্ত ডেলিভারি বা হিডেন ফি চার্জ করা।',
  },
  {
    id: 's52-false-advertisement',
    section: 'ধারা ৫২ (Section 52)',
    titleEn: 'Deceptive / Misleading Advertisement',
    titleBn: 'মিথ্যা বা বিভ্রান্তিকর বিজ্ঞাপন প্রচার',
    minFine: 50000,
    maxFine: 200000,
    prisonYears: 1,
    descriptionEn: 'Promoting misleading product specifications or unfulfillable refund guarantees on social media.',
    descriptionBn: 'ফেসবুক/ওয়েবসাইটে মিথ্যা অফার বা ভিত্তিহীন গ্যারান্টি দিয়ে ক্রেতাকে আকৃষ্ট করা।',
  },
];

export function StatutoryCompensationCalculator({
  locale = 'en',
  initialClaimAmount = 3200,
  className,
}: {
  locale?: string;
  initialClaimAmount?: number;
  className?: string;
}) {
  const isBangla = locale === 'bn';
  const [claimAmount, setClaimAmount] = useState<number>(initialClaimAmount);
  const [selectedTierId, setSelectedTierId] = useState<string>('s45-false-promise');
  const [severityMultiplier, setSeverityMultiplier] = useState<'standard' | 'repeat' | 'egregious'>('standard');
  const [showCitation, setShowCitation] = useState(false);

  const selectedTier = VIOLATION_TIERS.find((t) => t.id === selectedTierId) || VIOLATION_TIERS[0];

  // Fine calculation logic based on Consumer Rights Protection Act 2009 s.76(1)
  let fineEstimate = selectedTier.minFine;
  if (severityMultiplier === 'repeat') {
    fineEstimate = Math.round(selectedTier.minFine + (selectedTier.maxFine - selectedTier.minFine) * 0.6);
  } else if (severityMultiplier === 'egregious') {
    fineEstimate = selectedTier.maxFine;
  }

  // 25% reward for complainant under Section 76(1)
  const consumerReward25Percent = Math.round(fineEstimate * 0.25);
  // Total recovery: Disputed amount refund + 25% statutory fine award
  const totalProjectedRecovery = claimAmount + consumerReward25Percent;

  return (
    <div
      className={cn(
        'rounded-2xl border border-border/80 bg-surface/95 backdrop-blur-md p-4 sm:p-6 shadow-sm',
        className
      )}
    >
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-border/60">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-amber-500/10 border border-amber-500/20 text-amber-500 flex items-center justify-center shrink-0">
            <Coins className="w-4 h-4" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-sm sm:text-base font-bold text-foreground">
                {isBangla
                  ? 'ভোক্তা অধিকার আইনের ধারা ৭৬(১) অনুযায়ী ২৫% পুরস্কার ক্যালকুলেটর'
                  : 'Section 76(1) 25% Statutory Reward Calculator'}
              </h3>
              <Badge variant="brand" className="text-[10px] uppercase font-mono">
                {isBangla ? 'আইনসম্মত নগদ প্রাপ্তি' : 'Cash Payout'}
              </Badge>
            </div>
            <p className="text-xs text-muted-foreground mt-0.5">
              {isBangla
                ? 'জাতীয় ভোক্তা অধিকার সংরক্ষণ অধিদপ্তর কর্তৃক আদায়কৃত জরিমানার ২৫% সরাসরি অভিযোগকারী পাবেন'
                : 'Under Bangladesh Law, 25% of any administrative fine levied on the merchant is awarded directly to you'}
            </p>
          </div>
        </div>

        <button
          type="button"
          onClick={() => setShowCitation(!showCitation)}
          className="text-xs text-primary font-semibold flex items-center gap-1 hover:underline self-start sm:self-center"
        >
          <Scale className="w-3.5 h-3.5" />
          <span>{isBangla ? 'আইনি ধারা দেখুন' : 'Statute Text'}</span>
          {showCitation ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
        </button>
      </div>

      {/* Statutory Citation Dropdown */}
      {showCitation && (
        <div className="mt-3 p-3.5 rounded-xl bg-elevated/60 border border-border/80 text-xs text-muted-foreground leading-relaxed animate-fadeIn">
          <p className="font-semibold text-foreground mb-1">
            {isBangla
              ? 'ভোক্তা-অধিকার সংরক্ষণ আইন, ২০০৯ — ধারা ৭৬(১):'
              : 'The Consumer Rights Protection Act, 2009 — Section 76(1):'}
          </p>
          <blockquote className="italic border-l-2 border-primary pl-2.5 text-foreground/90">
            {isBangla
              ? '“যদি এই আইনের অধীন কোনো ব্যক্তিকে অর্থদণ্ডে দণ্ডিত করা হয়, তবে আদায়কৃত অর্থদণ্ডের ২৫% (পঁচিশ শতাংশ) তাৎক্ষণিকভাবে অভিযোগকারীকে নগদ প্রদান করিতে হইবে।”'
              : '"If any person is fined under this Act, 25% (twenty-five percent) of the realized fine shall be immediately paid to the complainant in cash."'}
          </blockquote>
        </div>
      )}

      {/* Main Calculator Inputs */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5 mt-5">
        {/* Left Inputs */}
        <div className="space-y-4">
          {/* Claim Amount Input */}
          <div>
            <label className="block text-xs font-semibold text-foreground mb-1.5">
              {isBangla ? 'আপনার দাবিকৃত ক্রয়মূল্য (টাকা):' : 'Your Disputed Purchase Amount (BDT):'}
            </label>
            <div className="relative">
              <span className="absolute left-3 top-2.5 text-muted-foreground font-semibold text-xs">
                ৳
              </span>
              <input
                type="number"
                min="100"
                step="100"
                value={claimAmount}
                onChange={(e) => setClaimAmount(Math.max(0, Number(e.target.value)))}
                className="w-full pl-7 pr-3 py-2 text-xs sm:text-sm rounded-lg border border-border bg-surface text-foreground focus:outline-none focus:ring-2 focus:ring-primary font-mono font-bold"
              />
            </div>
          </div>

          {/* Violation Category Selector */}
          <div>
            <label className="block text-xs font-semibold text-foreground mb-1.5">
              {isBangla ? 'মার্চেন্টের সংঘটিত অপরাধের ধরন:' : 'Merchant Violation Category:'}
            </label>
            <div className="space-y-1.5">
              {VIOLATION_TIERS.map((tier) => (
                <div
                  key={tier.id}
                  onClick={() => setSelectedTierId(tier.id)}
                  className={cn(
                    'p-2.5 rounded-lg border cursor-pointer text-xs transition-all',
                    selectedTierId === tier.id
                      ? 'border-primary bg-primary/10 text-foreground font-semibold ring-1 ring-primary'
                      : 'border-border/60 bg-surface hover:bg-elevated/40 text-muted-foreground'
                  )}
                >
                  <div className="flex items-center justify-between">
                    <span>{isBangla ? tier.titleBn : tier.titleEn}</span>
                    <span className="text-[10px] font-mono text-muted-foreground">
                      {tier.section}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Offender Track Record / Severity */}
          <div>
            <label className="block text-xs font-semibold text-foreground mb-1.5">
              {isBangla ? 'মার্চেন্টের অতীত রেকর্ড ও প্রতারণার মাত্রা:' : 'Merchant Track Record & Severity:'}
            </label>
            <div className="grid grid-cols-3 gap-2">
              {[
                { id: 'standard', labelEn: '1st Offense', labelBn: 'প্রথম অপরাধ' },
                { id: 'repeat', labelEn: 'Repeat Offender', labelBn: 'একাধিক অভিযোগ' },
                { id: 'egregious', labelEn: 'Severe Fraud', labelBn: 'গুরুতর প্রতারণা' },
              ].map((s) => (
                <button
                  key={s.id}
                  type="button"
                  onClick={() => setSeverityMultiplier(s.id as any)}
                  className={cn(
                    'py-1.5 px-2 rounded-md border text-center text-xs font-medium transition-colors',
                    severityMultiplier === s.id
                      ? 'border-primary bg-primary text-white font-bold'
                      : 'border-border/60 bg-surface hover:bg-elevated text-muted-foreground'
                  )}
                >
                  {isBangla ? s.labelBn : s.labelEn}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Right Output Highlight Box */}
        <div className="rounded-xl border border-primary/30 bg-gradient-to-br from-primary/5 via-surface to-amber-500/5 p-4 sm:p-5 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between pb-3 border-b border-border/40">
              <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wide">
                {isBangla ? 'আইনত প্রাক্কলিত ফলাফল' : 'Statutory Projection'}
              </span>
              <span className="text-xs font-mono text-emerald-500 font-bold flex items-center gap-1">
                <Sparkles className="w-3.5 h-3.5" />
                {isBangla ? 'আইনি সম্ভাবনা ৯২%' : '92% Confidence'}
              </span>
            </div>

            {/* Fines & 25% Payout Rows */}
            <div className="space-y-3.5 mt-4 text-xs">
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground">
                  {isBangla ? 'মার্চেন্টের সম্ভাব্য সরকারি জরিমানা:' : 'Projected Directorate Fine on Merchant:'}
                </span>
                <span className="font-mono font-bold text-foreground">
                  ৳{fineEstimate.toLocaleString(isBangla ? 'bn-BD' : 'en-US')}
                </span>
              </div>

              <div className="flex items-center justify-between p-2.5 rounded-lg bg-amber-500/10 border border-amber-500/25">
                <div>
                  <strong className="block text-amber-600 dark:text-amber-400 font-bold">
                    {isBangla ? 'আপনার ২৫% সরকারি নগদ পুরস্কার:' : 'Your 25% Direct Statutory Cash Reward:'}
                  </strong>
                  <span className="text-[10px] text-muted-foreground">
                    {isBangla ? 'ধারা ৭৬(১) মোতাবেক ট্রেজারি থেকে সরাসরি প্রদেয়' : 'Mandatory under Consumer Protection Act s.76(1)'}
                  </span>
                </div>
                <span className="text-base sm:text-lg font-mono font-extrabold text-amber-600 dark:text-amber-400">
                  ৳{consumerReward25Percent.toLocaleString(isBangla ? 'bn-BD' : 'en-US')}
                </span>
              </div>

              <div className="flex items-center justify-between">
                <span className="text-muted-foreground">
                  {isBangla ? 'ক্রয়মূল্য ফেরত (রিফান্ড):' : 'Full Purchase Amount Refund:'}
                </span>
                <span className="font-mono font-bold text-foreground">
                  ৳{claimAmount.toLocaleString(isBangla ? 'bn-BD' : 'en-US')}
                </span>
              </div>
            </div>
          </div>

          {/* Grand Total Recovery */}
          <div className="mt-5 pt-3.5 border-t border-border/60">
            <div className="flex items-baseline justify-between">
              <div>
                <span className="text-[11px] font-semibold text-muted-foreground uppercase tracking-wider block">
                  {isBangla ? 'সর্বমোট আপনার আর্থিক পুনরুদ্ধার:' : 'Total Projected Financial Recovery:'}
                </span>
                <span className="text-[10px] text-muted-foreground">
                  {isBangla ? '(আসল অর্থ ফেরত + ২৫% আইনি ক্ষতিপূরণ)' : '(Full Refund + 25% Legal Bounty)'}
                </span>
              </div>
              <div className="text-right">
                <span className="text-xl sm:text-2xl font-mono font-black text-primary">
                  ৳{totalProjectedRecovery.toLocaleString(isBangla ? 'bn-BD' : 'en-US')}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

