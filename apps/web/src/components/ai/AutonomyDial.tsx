'use client';

import React, { useState, useEffect } from 'react';
import {
  Sliders,
  ShieldCheck,
  Zap,
  Bot,
  Lock,
  Check,
  Sparkles,
  Info,
  Clock,
  Eye,
  FileCheck,
} from 'lucide-react';
import { Badge } from '@/components/ui/Badge';
import { cn } from '@/lib/utils';

export type AutonomyLevel = 'copilot' | 'semiauto' | 'autonomous';

interface AutonomyDialProps {
  initialLevel?: AutonomyLevel;
  caseId?: string;
  locale?: string;
  onChange?: (level: AutonomyLevel) => void;
  className?: string;
}

interface LevelSpec {
  id: AutonomyLevel;
  levelNum: number;
  labelEn: string;
  labelBn: string;
  badgeEn: string;
  badgeBn: string;
  taglineEn: string;
  taglineBn: string;
  descriptionEn: string;
  descriptionBn: string;
  permissionsEn: string[];
  permissionsBn: string[];
  humanGateEn: string;
  humanGateBn: string;
  accent: {
    color: string;
    border: string;
    glow: string;
    pillBg: string;
  };
}

const AUTONOMY_SPECS: Record<AutonomyLevel, LevelSpec> = {
  copilot: {
    id: 'copilot',
    levelNum: 1,
    labelEn: 'Level 1: Passive Copilot',
    labelBn: 'লেভেল ১: সাধারণ সহকারী (কোপাইলট)',
    badgeEn: 'Human-Led',
    badgeBn: 'সম্পূর্ণ মানব-নিয়ন্ত্রিত',
    taglineEn: 'Real-time legal advisory & evidence sanity checks only.',
    taglineBn: 'শুধুমাত্র রিয়েল-টাইম আইনি পরামর্শ ও ডকুমেন্ট যাচাই।',
    descriptionEn: 'The agent analyzes uploads, cross-checks limitation statutes, and surfaces suggestions. No automated actions or draft generation take place without explicit click prompts.',
    descriptionBn: 'এজেন্ট ডকুমেন্টস বিশ্লেষণ করে এবং আইনি সময়সীমা পর্যবেক্ষণ করে পরামর্শ দেয়। আপনার সরাসরি অনুমতি ছাড়া কোনো চিঠি বা খসড়া তৈরি হবে না।',
    permissionsEn: [
      'Document OCR & TrxID Verification',
      'Statutory 30-Day Limitation Alert',
      'Interactive Next Step Prompting',
    ],
    permissionsBn: [
      'ডকুমেন্ট ওসিআর ও লেনদেন যাচাই',
      '৩০ দিনের তামাদি আইনি সতর্কবার্তা',
      'পরবর্তী পদক্ষেপের সক্রিয় পরামর্শ',
    ],
    humanGateEn: '100% Human approval for all drafts & decisions',
    humanGateBn: 'সকল খসড়া ও সিদ্ধান্তের জন্য ১০০% মানব অনুমোদন প্রয়োজন',
    accent: {
      color: 'text-sky-500',
      border: 'border-sky-500/30',
      glow: 'shadow-[0_0_20px_rgba(14,165,233,0.15)]',
      pillBg: 'bg-sky-500/10 text-sky-400 border-sky-500/20',
    },
  },
  semiauto: {
    id: 'semiauto',
    levelNum: 2,
    labelEn: 'Level 2: Semi-Autonomous Agent',
    labelBn: 'লেভেল ২: সেমি-অটোনোমাস এজেন্ট (সুপারিশকৃত)',
    badgeEn: 'Recommended',
    badgeBn: 'সর্বাধিক কার্যকর',
    taglineEn: 'Proactive draft synthesis & recurring merchant radar monitoring.',
    taglineBn: 'স্বয়ংক্রিয় নোটিশ প্রস্তুতকরণ ও মার্চেন্ট স্ক্যাম রাডার নজরদারি।',
    descriptionEn: 'The agent autonomously extracts all fact tables from evidence, drafts statutory formal notices, tracks countdown timers, and highlights procedural bottlenecks.',
    descriptionBn: 'এজেন্ট স্বয়ংক্রিয়ভাবে প্রমাণপত্র থেকে তথ্য সারণি তৈরি করে, আইনি দাবি নোটিশ প্রস্তুত করে এবং তামাদি সময়সীমা ট্র্যাকিং বজায় রাখে।',
    permissionsEn: [
      'Continuous Merchant Scam Intelligence Monitor',
      'Multi-Tone Statutory Notice Drafting',
      'Auto-Extraction of Financial Claims',
      'Real-time Procedural Route Viability Scoring',
    ],
    permissionsBn: [
      'ধারাবাহিক মার্চেন্ট প্রতারণা গোয়েন্দা নজরদারি',
      'মাল্টি-টোন আইনি নোটিশের স্বয়ংক্রিয় খসড়া',
      'আর্থিক দাবির স্বয়ংক্রিয় হিসাব',
      'রিয়েল-টাইম কার্যকারিতা স্কোর আপডেট',
    ],
    humanGateEn: 'Human review & sign-off required prior to final dispatch',
    humanGateBn: 'নোটিশ পাঠানোর পূর্বে ভোক্তার চূড়ান্ত অনুমোদন বাধ্যতামূলক',
    accent: {
      color: 'text-brand',
      border: 'border-primary/40',
      glow: 'shadow-[0_0_24px_rgba(30,126,82,0.2)]',
      pillBg: 'bg-primary/10 text-primary border-primary/25',
    },
  },
  autonomous: {
    id: 'autonomous',
    levelNum: 3,
    labelEn: 'Level 3: Autonomous Consumer Advocate',
    labelBn: 'লেভেল ৩: অটোনোমাস কনজিউমার অ্যাডভোকেট',
    badgeEn: 'Maximum Speed',
    badgeBn: 'সর্বোচ্চ গতি ও সক্রিয়তা',
    taglineEn: 'Full procedural orchestration with auto-prepared ADR hearing briefs.',
    taglineBn: 'সম্পূর্ণ আইনি প্রক্রিয়া পরিচালনা ও স্বয়ংক্রিয় এডিআর ব্রিফ প্রস্তুত।',
    descriptionEn: 'The agent actively coordinates all evidence chains, synchronizes courier tracking slips, generates formal PDF dossiers for DNCRP, and simulates merchant settlement responses.',
    descriptionBn: 'এজেন্ট স্বয়ংক্রিয়ভাবে কুরিয়ার ট্র্যাকিং ও পেমেন্ট হিস্ট্রি সংযুক্ত করে, ভোক্তা অধিদপ্তরের ফর্ম প্রস্তুত রাখে এবং মার্চেন্টের প্রতিক্রিয়ার সম্ভাবনা পর্যালোচনা করে।',
    permissionsEn: [
      'Autonomous Evidence Fusion & Graph Linking',
      'Instant Pre-Action PDF Brief Generation',
      'Settlement Counter-Offer Simulator',
      'Statutory Deadline Emergency Escalation',
    ],
    permissionsBn: [
      'স্বয়ংক্রিয় প্রমাণ লিংকিং ও বিশ্লেষণ',
      'তাৎক্ষণিক প্রি-অ্যাকশন নোটিশ পিডিএফ জেনারেশন',
      'মীমাংসা সমঝোতার স্বয়ংক্রিয় পূর্বাভাস',
      'তামাদি জরুরি সময়ে জরুরি সংকেত অ্যালার্ট',
    ],
    humanGateEn: 'Strict Safety Fence: Zero official portal submission without final consumer OTP',
    humanGateBn: 'নিরাপত্তা বেষ্টনী: চূড়ান্ত ওটিপি সম্মতি ছাড়া কোনো সরকারি পোর্টালে তথ্য যায় না',
    accent: {
      color: 'text-amber-500',
      border: 'border-amber-500/40',
      glow: 'shadow-[0_0_24px_rgba(245,158,11,0.2)]',
      pillBg: 'bg-amber-500/10 text-amber-500 border-amber-500/25',
    },
  },
};

export function AutonomyDial({
  initialLevel = 'semiauto',
  caseId,
  locale = 'en',
  onChange,
  className,
}: AutonomyDialProps) {
  const isBangla = locale === 'bn';
  const [level, setLevel] = useState<AutonomyLevel>(initialLevel);
  const [isUpdating, setIsUpdating] = useState(false);
  const [justSaved, setJustSaved] = useState(false);

  // Read saved preference from localStorage if available
  useEffect(() => {
    if (typeof window !== 'undefined' && caseId) {
      const saved = localStorage.getItem(`claimcraft_autonomy_${caseId}`) as AutonomyLevel | null;
      if (saved && (saved === 'copilot' || saved === 'semiauto' || saved === 'autonomous')) {
        setLevel(saved);
      }
    }
  }, [caseId]);

  const handleSelect = (newLevel: AutonomyLevel) => {
    if (newLevel === level) return;
    setIsUpdating(true);
    setLevel(newLevel);
    if (typeof window !== 'undefined' && caseId) {
      localStorage.setItem(`claimcraft_autonomy_${caseId}`, newLevel);
    }
    onChange?.(newLevel);

    setTimeout(() => {
      setIsUpdating(false);
      setJustSaved(true);
      setTimeout(() => setJustSaved(false), 2400);
    }, 350);
  };

  const current = AUTONOMY_SPECS[level];

  return (
    <div
      className={cn(
        'rounded-xl border border-border/80 bg-surface/95 backdrop-blur-md p-4 sm:p-5 shadow-sm transition-all duration-300',
        current.accent.glow,
        className
      )}
    >
      {/* Header bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2.5 pb-4 border-b border-border/60">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-primary/10 border border-primary/20 flex items-center justify-center text-primary shrink-0">
            <Sliders className="w-4 h-4" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs sm:text-sm font-bold text-foreground">
                {isBangla ? 'এজেন্ট অটোনমি কন্ট্রোল ডায়াল' : 'Agentic Autonomy Policy'}
              </span>
              <Badge variant="brand" className="text-[10px] px-1.5 py-0">
                {isBangla ? 'স্বচ্ছ এআই' : 'Deterministic Sandbox'}
              </Badge>
            </div>
            <p className="text-[11px] text-muted-foreground mt-0.5">
              {isBangla
                ? 'আইনি অধিকার আদায়ের ক্ষেত্রে এআই সহকারীর নিয়ন্ত্রণ স্তর নির্ধারণ করুন'
                : 'Set procedural execution autonomy bounds for this dispute dossier'}
            </p>
          </div>
        </div>

        {/* Live Status indicator */}
        <div className="flex items-center gap-2 text-right sm:self-center">
          {justSaved && (
            <span className="text-[11px] text-emerald-500 font-semibold flex items-center gap-1 animate-fadeIn">
              <Check className="w-3.5 h-3.5" />
              {isBangla ? 'পলিসি সংরক্ষিত' : 'Policy updated'}
            </span>
          )}
          <span className="text-[11px] font-mono text-muted-foreground bg-elevated/70 px-2 py-1 rounded-md border border-border/60">
            {isBangla ? `লেভেল ${current.levelNum}/৩` : `LVL ${current.levelNum} / 3`}
          </span>
        </div>
      </div>

      {/* 3-Level Segmented Radio Switcher */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5 pt-4">
        {(['copilot', 'semiauto', 'autonomous'] as AutonomyLevel[]).map((key) => {
          const spec = AUTONOMY_SPECS[key];
          const isSelected = level === key;

          return (
            <button
              key={key}
              type="button"
              onClick={() => handleSelect(key)}
              className={cn(
                'group relative text-left p-3 rounded-lg border transition-all duration-200 focus:outline-none focus-visible:ring-2 focus-visible:ring-primary',
                isSelected
                  ? cn('bg-elevated border-2', spec.accent.border, spec.accent.glow)
                  : 'border-border/60 bg-surface/50 hover:bg-elevated/40 hover:border-border'
              )}
            >
              {/* Radio Indicator & Label */}
              <div className="flex items-start justify-between gap-1.5 mb-2">
                <div className="flex items-center gap-2">
                  <span
                    className={cn(
                      'w-4 h-4 rounded-full border flex items-center justify-center transition-colors',
                      isSelected
                        ? 'border-primary bg-primary text-white'
                        : 'border-muted-foreground/40 bg-surface group-hover:border-muted-foreground'
                    )}
                  >
                    {isSelected && <span className="w-1.5 h-1.5 rounded-full bg-white" />}
                  </span>
                  <span className="text-xs font-bold text-foreground">
                    {isBangla ? spec.labelBn : spec.labelEn}
                  </span>
                </div>
                <span
                  className={cn(
                    'text-[9px] font-semibold uppercase tracking-wider px-1.5 py-0.5 rounded border',
                    spec.accent.pillBg
                  )}
                >
                  {isBangla ? spec.badgeBn : spec.badgeEn}
                </span>
              </div>

              {/* Tagline */}
              <p className="text-[11px] text-muted-foreground line-clamp-2 leading-relaxed">
                {isBangla ? spec.taglineBn : spec.taglineEn}
              </p>
            </button>
          );
        })}
      </div>

      {/* Selected Policy Feature Grid & Safety Guardrail Banner */}
      <div className="mt-4 p-3.5 rounded-lg bg-elevated/50 border border-border/70 text-xs">
        <div className="flex items-center justify-between mb-2 pb-2 border-b border-border/40">
          <span className="font-semibold text-foreground flex items-center gap-1.5">
            <Bot className="w-3.5 h-3.5 text-primary" />
            <span>{isBangla ? 'সক্রিয় অধিকার ও সক্ষমতা:' : 'Autonomous Capabilities Granted:'}</span>
          </span>
          <span className="text-[10px] text-muted-foreground font-mono">
            Audit ID: cc-pol-{level}
          </span>
        </div>

        {/* Permission Pills */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 mb-3">
          {(isBangla ? current.permissionsBn : current.permissionsEn).map((perm, idx) => (
            <div key={idx} className="flex items-center gap-1.5 text-muted-foreground">
              <Check className="w-3 h-3 text-emerald-500 shrink-0" />
              <span className="text-[11px]">{perm}</span>
            </div>
          ))}
        </div>

        {/* Human-in-the-loop Guardrail */}
        <div className="flex items-start gap-2 p-2 rounded-md bg-surface border border-border/60 text-[11px] text-muted-foreground">
          <ShieldCheck className="w-4 h-4 text-emerald-500 shrink-0 mt-0.5" />
          <div>
            <strong className="text-foreground font-semibold">
              {isBangla ? 'নিরাপত্তা সুরক্ষা গ্যারান্টি: ' : 'Human Guardrail: '}
            </strong>
            <span>{isBangla ? current.humanGateBn : current.humanGateEn}</span>
          </div>
        </div>
      </div>
    </div>
  );
}

