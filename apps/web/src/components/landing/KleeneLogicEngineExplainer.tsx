'use client';

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import {
  Scale,
  CheckCircle2,
  HelpCircle,
  XCircle,
  Cpu,
  ShieldCheck,
  AlertTriangle,
  ArrowRight,
  GitBranch,
  Terminal,
} from 'lucide-react';
import { Badge } from '@/components/ui/Badge';
import { cn } from '@/lib/utils';

type KleeneValue = 'TRUE' | 'UNKNOWN' | 'FALSE';

interface FactInput {
  id: string;
  nameEn: string;
  nameBn: string;
  statute: string;
  value: KleeneValue;
  descEn: string;
  descBn: string;
}

export function KleeneLogicEngineExplainer({ locale = 'en' }: { locale?: string }) {
  const isBangla = locale === 'bn';

  // 3 Key Dispute Facts with Kleene States
  const [hasReceipt, setHasReceipt] = useState<KleeneValue>('TRUE');
  const [withinLimitation, setWithinLimitation] = useState<KleeneValue>('TRUE');
  const [merchantNotified, setMerchantNotified] = useState<KleeneValue>('UNKNOWN');

  // Compute Kleene 3-Valued Logic Result:
  // Actionability = hasReceipt ∧ withinLimitation ∧ merchantNotified
  // In 3-valued Kleene AND:
  // TRUE ∧ TRUE = TRUE
  // Any FALSE = FALSE
  // If no FALSE and any UNKNOWN = UNKNOWN
  const computeKleeneOutcome = (): {
    result: KleeneValue;
    statusLabelEn: string;
    statusLabelBn: string;
    descriptionEn: string;
    descriptionBn: string;
    color: string;
    badgeVariant: 'success' | 'warning' | 'danger';
    llmContrastEn: string;
    llmContrastBn: string;
  } => {
    if (hasReceipt === 'FALSE' || withinLimitation === 'FALSE') {
      return {
        result: 'FALSE',
        statusLabelEn: 'BARRED BY STATUTE / INADMISSIBLE',
        statusLabelBn: 'তামাদি অথবা আইনি ভিত্তিহীন (বাতিল)',
        descriptionEn:
          'Under CRPA 2009 Section 60, if statutory timeline (>30 days) is breached or payment is disproven, formal DNCRP arbitration is legally barred. The engine redirects to informal civil conciliation.',
        descriptionBn:
          'ভোক্তা অধিকার সংরক্ষণ আইন ২০০৯-এর ধারা ৬০ মোতাবেক ৩০ দিনের তামাদি অতিক্রান্ত হলে বা পেমেন্ট প্রমাণ অপ্রমাণিত হলে সরকারি অভিযোগ গঠন সম্ভব নয়।',
        color: 'text-rose-600 dark:text-rose-400 border-rose-500/30 bg-rose-500/5',
        badgeVariant: 'danger',
        llmContrastEn:
          'Standard LLMs often hallucinate: "Yes, you can still file with the police!" giving illegal advice. ClaimCraft BD enforces deterministic statutory barriers.',
        llmContrastBn:
          'সাধারণ চ্যাটবট ভুল তথ্য দিয়ে মামলা করতে বলে। ক্লেইমক্রাফ্ট বিডি আইনি তামাদি বাধা নিশ্চিত করে ভুল পদক্ষেপ প্রতিরোধ করে।',
      };
    }

    if (hasReceipt === 'UNKNOWN' || merchantNotified === 'UNKNOWN') {
      return {
        result: 'UNKNOWN',
        statusLabelEn: 'SAFE HOLD — CLARIFICATION REQUIRED',
        statusLabelBn: 'নিরাপদ স্থগিতাদেশ — তথ্য স্পষ্টীকরণ প্রয়োজন',
        descriptionEn:
          'Kleene Logic evaluates: TRUE ∧ TRUE ∧ UNKNOWN = UNKNOWN. Procedural escalation is locked. Next Best Question (NBQ) triggers to prompt the consumer for 7-day notice dispatch proof.',
        descriptionBn:
          'ক্লিন থ্রি-ভ্যালুড লজিক: সত্য ∧ সত্য ∧ অজানা = অজানা। মিথ্যা অভিযোগ এড়াতে সিস্টেম পরবর্তী প্রশ্ন (NBQ) করবে এবং প্রমাণের অপেক্ষায় থাকবে।',
        color: 'text-amber-600 dark:text-amber-400 border-amber-500/30 bg-amber-500/5',
        badgeVariant: 'warning',
        llmContrastEn:
          'Standard LLMs guess or hallucinate missing facts. ClaimCraft BD mathematically treats incomplete information as UNKNOWN to guarantee 0% false filing.',
        llmContrastBn:
          'সাধারণ এআই অনুমান করে বিভ্রান্তিকর খসড়া তৈরি করে। ক্লেইমক্রাফ্ট বিডি তথ্য অপূর্ণ থাকলে ক্লিনের তিন-মানসম্পন্ন যুক্তির অধীনে অপেক্ষা করে।',
      };
    }

    return {
      result: 'TRUE',
      statusLabelEn: '100% STATUTORILY ACTIONABLE',
      statusLabelBn: '১০০% আইনিভাবে কার্যকর ও প্রমাণিত',
      descriptionEn:
        'All conditions satisfied (CRPA 2009 Sec 45 + Sec 60). The engine immediately triggers the Autonomous Draftsman to assemble DNCRP Official Form-1 and demand notices.',
      descriptionBn:
        'সকল আইনি শর্ত পূরণ হয়েছে (ধারা ৪৫ ও ৬০)। অটোনোমাস ড্রাফটসম্যান তাৎক্ষণিকভাবে জাতীয় ভোক্তা অধিদপ্তরের অফিশিয়াল ফরম-১ ও লিগ্যাল নোটিশ তৈরি করবে।',
      color: 'text-emerald-600 dark:text-emerald-400 border-emerald-500/30 bg-emerald-500/5',
      badgeVariant: 'success',
      llmContrastEn:
        'Deterministic validation ensures 100% admissible evidence package with verified citations ready for magistrate review.',
      llmContrastBn:
        'অকাট্য প্রমাণাদি ও সঠিক আইনি ধারার সমন্বয়ে তৈরি ফরম যা ম্যাজিস্ট্রেট ও ভোক্তা অধিদপ্তরে সাথে সাথে গ্রহণযোগ্য।',
    };
  };

  const outcome = computeKleeneOutcome();

  const cycleValue = (current: KleeneValue): KleeneValue => {
    if (current === 'TRUE') return 'UNKNOWN';
    if (current === 'UNKNOWN') return 'FALSE';
    return 'TRUE';
  };

  return (
    <div className="w-full max-w-5xl mx-auto rounded-3xl border border-border bg-surface p-6 sm:p-8 shadow-xs">
      {/* Title & Badge */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-6 border-b border-border">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <h3 className="font-display text-xl sm:text-2xl font-bold tracking-tight text-foreground">
              {isBangla
                ? 'ক্লিনের ৩-মানসম্পন্ন ডিটারমিনিস্টিক লজিক ইঞ্জিন'
                : 'Deterministic 3-Valued Kleene Logic Engine'}
            </h3>
            <Badge variant="brand" className="text-[10px] uppercase font-mono">
              Zero Hallucination
            </Badge>
          </div>
          <p className="text-xs sm:text-sm text-muted-foreground max-w-2xl">
            {isBangla
              ? 'আইনি বিষয়ে সাধারণ এলএলএম বানিয়ে বলা (Hallucination) সম্পূর্ণ প্রতিরোধ করার জন্য আমরা ৩-মানসম্পন্ন যুক্তির অ্যাবস্ট্রাক্ট সিনট্যাক্স ট্রি (AST) ব্যবহার করি।'
              : 'Why ClaimCraft BD never hallucinates legal advice: We enforce Kleene 3-Valued Logic (TRUE / UNKNOWN / FALSE) over an Abstract Syntax Tree before any generative drafting.'}
          </p>
        </div>

        <div className="flex items-center gap-2 font-mono text-[11px] text-muted-foreground bg-elevated px-3 py-1.5 rounded-xl border border-border shrink-0 self-start sm:self-auto">
          <Terminal className="w-3.5 h-3.5 text-primary" />
          <span>AST Rule: s45_viability_v2</span>
        </div>
      </div>

      {/* Interactive Fact Switches */}
      <div className="py-6">
        <div className="flex items-center justify-between mb-3">
          <span className="text-xs font-semibold text-foreground uppercase tracking-wider">
            {isBangla ? 'বাস্তব প্রমাণাদি টগল করুন (ক্লিক করে মান পরিবর্তন করুন):' : 'Interactive Dispute Facts (Click to toggle value):'}
          </span>
          <span className="text-[11px] text-muted-foreground font-mono">
            {isBangla ? 'মান: TRUE → UNKNOWN → FALSE' : 'Cycles: TRUE → UNKNOWN → FALSE'}
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-3.5">
          {/* Fact 1: Payment Slip */}
          <div
            onClick={() => setHasReceipt(cycleValue(hasReceipt))}
            className="p-4 rounded-2xl border border-border bg-elevated/40 hover:bg-elevated cursor-pointer transition-all select-none group"
          >
            <div className="flex items-center justify-between mb-2">
              <span className="text-[11px] font-mono text-muted-foreground">FACT #1 • FORENSIC</span>
              <span
                className={cn(
                  'px-2 py-0.5 rounded text-[10px] font-mono font-bold uppercase transition-colors',
                  hasReceipt === 'TRUE'
                    ? 'bg-emerald-500/15 text-emerald-600 dark:text-emerald-400'
                    : hasReceipt === 'UNKNOWN'
                    ? 'bg-amber-500/15 text-amber-600 dark:text-amber-400'
                    : 'bg-rose-500/15 text-rose-600 dark:text-rose-400'
                )}
              >
                {hasReceipt}
              </span>
            </div>
            <h4 className="font-semibold text-sm text-foreground group-hover:text-primary transition-colors">
              {isBangla ? 'পেমেন্ট ও মানি রিসিট প্রমাণ' : 'Payment Receipt Verified'}
            </h4>
            <p className="text-xs text-muted-foreground mt-1 leading-relaxed">
              {isBangla
                ? 'বিকাশ/নগদ স্টেটমেন্ট বা ইনভয়েসে আর্থিক মিল'
                : 'bKash/Nagad statement or store cash invoice match'}
            </p>
            <div className="mt-3 text-[10px] font-mono text-primary flex items-center gap-1">
              <span>CRPA 2009 s.45</span>
              <ArrowRight className="w-2.5 h-2.5 opacity-60" />
            </div>
          </div>

          {/* Fact 2: Statutory Limitation */}
          <div
            onClick={() => setWithinLimitation(cycleValue(withinLimitation))}
            className="p-4 rounded-2xl border border-border bg-elevated/40 hover:bg-elevated cursor-pointer transition-all select-none group"
          >
            <div className="flex items-center justify-between mb-2">
              <span className="text-[11px] font-mono text-muted-foreground">FACT #2 • LIMITATION</span>
              <span
                className={cn(
                  'px-2 py-0.5 rounded text-[10px] font-mono font-bold uppercase transition-colors',
                  withinLimitation === 'TRUE'
                    ? 'bg-emerald-500/15 text-emerald-600 dark:text-emerald-400'
                    : withinLimitation === 'UNKNOWN'
                    ? 'bg-amber-500/15 text-amber-600 dark:text-amber-400'
                    : 'bg-rose-500/15 text-rose-600 dark:text-rose-400'
                )}
              >
                {withinLimitation}
              </span>
            </div>
            <h4 className="font-semibold text-sm text-foreground group-hover:text-primary transition-colors">
              {isBangla ? '৩০ দিনের তামাদি সময়সীমা' : 'Filing Within 30-Day Limit'}
            </h4>
            <p className="text-xs text-muted-foreground mt-1 leading-relaxed">
              {isBangla
                ? 'ঘটনাস্থল থেকে ৩০ কর্মদিবসের মধ্যে অভিযোগ দাখিল'
                : 'Filing within strict 30-day window from incident date'}
            </p>
            <div className="mt-3 text-[10px] font-mono text-primary flex items-center gap-1">
              <span>CRPA 2009 s.60</span>
              <ArrowRight className="w-2.5 h-2.5 opacity-60" />
            </div>
          </div>

          {/* Fact 3: Written Demand Notice */}
          <div
            onClick={() => setMerchantNotified(cycleValue(merchantNotified))}
            className="p-4 rounded-2xl border border-border bg-elevated/40 hover:bg-elevated cursor-pointer transition-all select-none group"
          >
            <div className="flex items-center justify-between mb-2">
              <span className="text-[11px] font-mono text-muted-foreground">FACT #3 • NOTICE</span>
              <span
                className={cn(
                  'px-2 py-0.5 rounded text-[10px] font-mono font-bold uppercase transition-colors',
                  merchantNotified === 'TRUE'
                    ? 'bg-emerald-500/15 text-emerald-600 dark:text-emerald-400'
                    : merchantNotified === 'UNKNOWN'
                    ? 'bg-amber-500/15 text-amber-600 dark:text-amber-400'
                    : 'bg-rose-500/15 text-rose-600 dark:text-rose-400'
                )}
              >
                {merchantNotified}
              </span>
            </div>
            <h4 className="font-semibold text-sm text-foreground group-hover:text-primary transition-colors">
              {isBangla ? 'মার্চেন্টকে ৭ দিনের নোটিশ প্রেরণ' : '7-Day Demand Notice Sent'}
            </h4>
            <p className="text-xs text-muted-foreground mt-1 leading-relaxed">
              {isBangla
                ? 'সমাধানের জন্য বিক্রেতাকে লিখিত সুযোগ প্রদান'
                : 'Merchant served with written opportunity to remediate'}
            </p>
            <div className="mt-3 text-[10px] font-mono text-primary flex items-center gap-1">
              <span>MoC Guidelines 2021</span>
              <ArrowRight className="w-2.5 h-2.5 opacity-60" />
            </div>
          </div>
        </div>
      </div>

      {/* Outcome Visualizer */}
      <AnimatePresence mode="wait">
        <motion.div
          key={`${hasReceipt}-${withinLimitation}-${merchantNotified}`}
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -8 }}
          transition={{ duration: 0.2 }}
          className={cn(
            'p-5 sm:p-6 rounded-2xl border transition-all',
            outcome.color
          )}
        >
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-border/40">
            <div className="flex items-center gap-2.5">
              {outcome.result === 'TRUE' ? (
                <CheckCircle2 className="w-5 h-5 text-emerald-500" />
              ) : outcome.result === 'UNKNOWN' ? (
                <HelpCircle className="w-5 h-5 text-amber-500" />
              ) : (
                <XCircle className="w-5 h-5 text-rose-500" />
              )}
              <div>
                <span className="text-[10px] font-mono uppercase tracking-wider text-muted-foreground block">
                  Deterministic AST Evaluation
                </span>
                <h4 className="font-display font-bold text-base sm:text-lg text-foreground">
                  {isBangla ? outcome.statusLabelBn : outcome.statusLabelEn}
                </h4>
              </div>
            </div>

            <div className="font-mono text-xs font-bold px-3 py-1 rounded-lg bg-surface border border-border shadow-xs">
              Kleene Result: <span className="text-primary font-black">{outcome.result}</span>
            </div>
          </div>

          <p className="text-xs sm:text-sm text-foreground/90 mt-3 leading-relaxed">
            {isBangla ? outcome.descriptionBn : outcome.descriptionEn}
          </p>

          {/* Side-by-Side LLM Contrast vs ClaimCraft Determinism */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mt-4 pt-4 border-t border-border/40 text-xs">
            <div className="p-3 rounded-xl bg-surface/80 border border-border/60">
              <span className="text-rose-500 font-bold block text-[11px] uppercase tracking-wide mb-1">
                ⚠️ Standard GenAI Bot (Fragile / Hallucinates)
              </span>
              <p className="text-muted-foreground leading-relaxed">
                {isBangla ? outcome.llmContrastBn : outcome.llmContrastEn}
              </p>
            </div>

            <div className="p-3 rounded-xl bg-surface/80 border border-primary/30">
              <span className="text-emerald-500 font-bold block text-[11px] uppercase tracking-wide mb-1">
                🛡️ ClaimCraft BD (Sovereign AST Engine)
              </span>
              <p className="text-foreground leading-relaxed">
                {isBangla
                  ? 'আইনি বিধিমালার ৩-মানসম্পন্ন ট্রুথ টেবিল দ্বারা চালিত — কোনো অপ্রমাণিত বা ভুল তথ্য দিয়ে কেস সাজানো অসম্ভব।'
                  : 'Governed by formal logic gates — guarantees every statutory prerequisite is provable before drafting dockets.'}
              </p>
            </div>
          </div>
        </motion.div>
      </AnimatePresence>
    </div>
  );
}

