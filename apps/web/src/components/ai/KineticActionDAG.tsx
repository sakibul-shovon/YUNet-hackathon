'use client';

import React, { useState } from 'react';
import {
  CheckCircle2,
  Clock,
  ArrowRight,
  ShieldAlert,
  Sparkles,
  FileText,
  Lock,
  Zap,
  Layers,
  ChevronRight,
  Info,
  Scale,
} from 'lucide-react';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { cn } from '@/lib/utils';

export interface DAGNode {
  id: string;
  stageNum: number;
  titleEn: string;
  titleBn: string;
  categoryEn: string;
  categoryBn: string;
  status: 'completed' | 'active' | 'armed' | 'contingency';
  timelineEn: string;
  timelineBn: string;
  statutoryBasis: string;
  descriptionEn: string;
  descriptionBn: string;
  deliverablesEn: string[];
  deliverablesBn: string[];
}

const DEFAULT_NODES: DAGNode[] = [
  {
    id: 'node-evidence',
    stageNum: 1,
    titleEn: 'Forensic Evidence Lockdown',
    titleBn: 'প্রমাণপত্র ও ডিজিটাল সত্যতা যাচাই',
    categoryEn: 'Prerequisite Phase',
    categoryBn: 'প্রাথমিক ভিত্তি',
    status: 'completed',
    timelineEn: 'Day 0 • Completed',
    timelineBn: 'দিন ০ • সম্পন্ন',
    statutoryBasis: 'Section 45 & ISO/IEC 27037 Digital Forensics',
    descriptionEn: 'MFS transaction statement and digital payment receipt cross-referenced against logistics tracking slip and merchant communications.',
    descriptionBn: 'ডিজিটাল লেনদেন রসিদ, কুরিয়ার ট্র্যাকিং চালান এবং বিক্রেতার সাথে চ্যাট ইতিহাস ফরেনসিক এআই দ্বারা যাচাইকৃত।',
    deliverablesEn: [
      'Digital Tamper-Proof Audit Manifest',
      'Fact Assertion Matrix (3 assertions grounded)',
    ],
    deliverablesBn: [
      'ডিজিটাল প্রমাণপত্রের অডিট রিপোর্ট',
      '৩টি আইনি তথ্যের শতভাগ ম্যাচিং নিশ্চিতকরণ',
    ],
  },
  {
    id: 'node-notice',
    stageNum: 2,
    titleEn: '72-Hour Pre-Action Demand Notice',
    titleBn: '৭২ ঘণ্টার আইনি প্রি-অ্যাকশন নোটিশ',
    categoryEn: 'Current Execution Stage',
    categoryBn: 'বর্তমান পদক্ষেপ',
    status: 'active',
    timelineEn: 'Day 1–3 • In Progress',
    timelineBn: 'দিন ১–৩ • চলমান',
    statutoryBasis: 'Section 45 Consumer Rights Act 2009',
    descriptionEn: 'Formally communicates statutory violation to merchant with a mandatory 72-hour rectification window prior to regulatory escalation.',
    descriptionBn: 'ভোক্তা অধিকার সংরক্ষণ আইন ২০০৯ এর ৪৫ ধারা অনুসারে মার্চেন্টকে ৭২ ঘণ্টার মধ্যে টাকা ফেরত বা সমাধানের দাবি জানিয়ে নোটিশ।',
    deliverablesEn: [
      'Bilingual Formal Demand Notice (PDF & Email)',
      'Statutory 72-Hour Countdown Lock',
    ],
    deliverablesBn: [
      'দ্বিভাষিক আইনি দাবি নোটিশ (পিডিএফ ও টেক্সট)',
      '৭২ ঘণ্টার স্বয়ংক্রিয় কাউন্টডাউন টাইমার',
    ],
  },
  {
    id: 'node-dncrp',
    stageNum: 3,
    titleEn: 'DNCRP Regulatory Portal Filing',
    titleBn: 'ভোক্তা অধিকার অধিদপ্তরে অভিযোগ দাখিল',
    categoryEn: 'Armed Escalation Stage',
    categoryBn: 'প্রস্তুত আইনি পদক্ষেপ',
    status: 'armed',
    timelineEn: 'Day 4 • Armed if Merchant Refuses',
    timelineBn: 'দিন ৪ • নোটিশ উপেক্ষা করলে স্বয়ংক্রিয় প্রস্তুত',
    statutoryBasis: 'Section 60 & 76 Consumer Rights Act 2009',
    descriptionEn: 'Official consumer complaint dossier filed directly to Directorate of National Consumer Rights Protection. Consumer is entitled to 25% of administrative fines.',
    descriptionBn: 'জাতীয় ভোক্তা অধিকার সংরক্ষণ অধিদপ্তরে অফিসিয়াল অভিযোগ পেশ। ভোক্তা আইন অনুযায়ী জরিমানার ২৫% অর্থ প্রাপ্তির যোগ্য।',
    deliverablesEn: [
      'Official DNCRP Schedule Complaint Form (PDF)',
      'Statutory 25% Fine Compensation Claim Brief',
    ],
    deliverablesBn: [
      'ভোক্তা অধিদপ্তরের নির্ধারিত অভিযোগ ফর্ম (পিডিএফ)',
      '২৫% ক্ষতিপূরণ দাবি সম্বলিত আইনি সারসংক্ষেপ',
    ],
  },
  {
    id: 'node-adr',
    stageNum: 4,
    titleEn: 'Executive ADR / Civil Settlement',
    titleBn: 'বিকল্প বিরোধ নিষ্পত্তি (ADR) ও রিকভারি',
    categoryEn: 'Contingency Resolution',
    categoryBn: 'চূড়ান্ত নিষ্পত্তি',
    status: 'contingency',
    timelineEn: 'Day 7–14 • Projected Path',
    timelineBn: 'দিন ৭–১৪ • সম্ভাব্য পরিণতি',
    statutoryBasis: 'Code of Civil Procedure (CPC) Section 89A Mediation',
    descriptionEn: 'Court-annexed mediation and expedited merchant refund recovery without protracted civil litigation overhead.',
    descriptionBn: 'দীর্ঘ আইনি জটিলতা এড়িয়ে স্বল্প সময়ে মধ্যস্থতা ও অর্থ আদায়ের প্রাতিষ্ঠানিক নিষ্পত্তি।',
    deliverablesEn: [
      'Formal Mediation Hearing Settlement Brief',
      'Enforceable Merchant Resolution Agreement',
    ],
    deliverablesBn: [
      'মধ্যস্থতা শুনানির খসড়া ও পয়েন্টসমূহ',
      'আইনত বলবৎযোগ্য মীমাংসা চুক্তিপত্র',
    ],
  },
];

export function KineticActionDAG({
  locale = 'en',
  caseId,
  className,
}: {
  locale?: string;
  caseId?: string;
  className?: string;
}) {
  const isBangla = locale === 'bn';
  const [selectedNodeId, setSelectedNodeId] = useState<string>('node-notice');
  const [simulatingUnresponsive, setSimulatingUnresponsive] = useState(false);

  const activeNode =
    DEFAULT_NODES.find((n) => n.id === selectedNodeId) || DEFAULT_NODES[1];

  return (
    <div
      className={cn(
        'rounded-2xl border border-border/80 bg-surface/95 backdrop-blur-md p-4 sm:p-6 shadow-sm overflow-hidden',
        className
      )}
    >
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-5 border-b border-border/60">
        <div>
          <div className="flex items-center gap-2">
            <span className="p-1 rounded-md bg-primary/10 text-primary border border-primary/20">
              <Zap className="w-4 h-4" />
            </span>
            <h3 className="text-sm sm:text-base font-bold text-foreground">
              {isBangla
                ? 'কাইনেটিক অ্যাকশন ডিপেন্ডেন্সি ড্যাগ (DAG)'
                : 'Kinetic Procedural Action DAG'}
            </h3>
            <Badge variant="brand" className="text-[10px] uppercase font-mono">
              Live Directed Graph
            </Badge>
          </div>
          <p className="text-xs text-muted-foreground mt-1">
            {isBangla
              ? 'এজেন্টদের দ্বারা পরিচালিত আইনি প্রক্রিয়ার ধারাবাহিক আন্তঃসংযোগ ও সক্রিয় গতিপথ'
              : 'Autonomous dependency graph orchestrating prerequisite gates, notices, and statutory escalation'}
          </p>
        </div>

        {/* What-If Simulation Toggle */}
        <div className="flex items-center gap-2 bg-elevated/70 border border-border/70 p-1.5 rounded-lg text-xs self-start sm:self-center">
          <span className="text-[11px] font-semibold text-muted-foreground pl-1">
            {isBangla ? 'মার্চেন্ট সাড়া না দিলে?' : 'If Merchant Ignores Notice:'}
          </span>
          <button
            type="button"
            onClick={() => setSimulatingUnresponsive(!simulatingUnresponsive)}
            className={cn(
              'px-2.5 py-1 rounded text-[11px] font-bold transition-all',
              simulatingUnresponsive
                ? 'bg-amber-500 text-white shadow-xs'
                : 'bg-surface hover:bg-elevated text-foreground border border-border/80'
            )}
          >
            {simulatingUnresponsive
              ? (isBangla ? '⚡ জরুরি DNCRP সক্রিয়' : '⚡ DNCRP Armed')
              : (isBangla ? 'সিমুলেট করুন' : 'Simulate')}
          </button>
        </div>
      </div>

      {/* Visual Kinetic Node Pipeline */}
      <div className="relative pt-6 pb-4">
        {/* Animated Flow Track (SVG Beam on Desktop) */}
        <div className="hidden lg:block absolute top-[44px] left-[7%] right-[7%] h-[3px] bg-border/60 z-0 overflow-hidden rounded-full">
          <div
            className={cn(
              'h-full bg-gradient-to-r from-emerald-500 via-primary to-amber-500 transition-all duration-700',
              simulatingUnresponsive ? 'w-[78%]' : 'w-[42%]'
            )}
            style={{
              backgroundSize: '200% 100%',
              animation: 'moveBeam 2.5s linear infinite',
            }}
          />
        </div>

        {/* 4 Connected Nodes Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 relative z-10">
          {DEFAULT_NODES.map((node, idx) => {
            const isSelected = node.id === activeNode.id;
            const isArmedSim = simulatingUnresponsive && node.id === 'node-dncrp';

            let statusColor = 'border-border/80 bg-surface';
            let iconBadge = <Clock className="w-3.5 h-3.5 text-muted-foreground" />;

            if (node.status === 'completed') {
              statusColor = 'border-emerald-500/40 bg-emerald-500/5 hover:border-emerald-500';
              iconBadge = <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" />;
            } else if (node.status === 'active' || isArmedSim) {
              statusColor = 'border-primary ring-2 ring-primary/20 bg-primary/5 hover:border-primary';
              iconBadge = <Zap className="w-3.5 h-3.5 text-primary animate-pulse" />;
            } else if (node.status === 'armed') {
              statusColor = 'border-amber-500/40 bg-amber-500/5 hover:border-amber-500';
              iconBadge = <ShieldAlert className="w-3.5 h-3.5 text-amber-500" />;
            }

            return (
              <div
                key={node.id}
                onClick={() => setSelectedNodeId(node.id)}
                className={cn(
                  'cursor-pointer rounded-xl border p-3.5 transition-all duration-200 relative group flex flex-col justify-between',
                  statusColor,
                  isSelected && 'ring-2 ring-primary shadow-md'
                )}
              >
                {/* Top Badge & Number */}
                <div className="flex items-center justify-between gap-1 mb-2">
                  <div className="flex items-center gap-1.5">
                    <span className="w-5 h-5 rounded-full bg-elevated border border-border/80 font-mono text-[10px] font-bold flex items-center justify-center text-muted-foreground">
                      {node.stageNum}
                    </span>
                    <span className="text-[10px] font-semibold text-muted-foreground uppercase tracking-wider">
                      {isBangla ? node.categoryBn : node.categoryEn}
                    </span>
                  </div>
                  {iconBadge}
                </div>

                {/* Node Title */}
                <h4 className="text-xs sm:text-sm font-bold text-foreground mb-1 leading-snug group-hover:text-primary transition-colors">
                  {isBangla ? node.titleBn : node.titleEn}
                </h4>

                {/* Node Timeline */}
                <div className="text-[10px] font-mono text-muted-foreground flex items-center gap-1 mt-2 pt-2 border-t border-border/40">
                  <span>{isBangla ? node.timelineBn : node.timelineEn}</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Selected Node Detailed Inspector */}
      <div className="mt-4 p-4 rounded-xl bg-elevated/50 border border-border/80 text-xs animate-fadeIn">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-border/40">
          <div className="flex items-center gap-2">
            <Scale className="w-4 h-4 text-primary" />
            <span className="font-bold text-foreground text-xs sm:text-sm">
              {isBangla ? activeNode.titleBn : activeNode.titleEn}
            </span>
            <Badge variant="brand" className="text-[10px] font-mono">
              Stage {activeNode.stageNum}
            </Badge>
          </div>
          <div className="text-[11px] text-muted-foreground font-mono bg-surface px-2 py-0.5 rounded border border-border/60">
            {activeNode.statutoryBasis}
          </div>
        </div>

        <p className="text-xs text-muted-foreground leading-relaxed mt-3">
          {isBangla ? activeNode.descriptionBn : activeNode.descriptionEn}
        </p>

        {/* Key Deliverables Produced */}
        <div className="mt-3.5 pt-3 border-t border-border/40">
          <span className="text-[11px] font-bold text-foreground flex items-center gap-1.5 mb-2">
            <FileText className="w-3.5 h-3.5 text-primary" />
            <span>{isBangla ? 'উৎপাদিত ফলাফল ও নথিসমূহ:' : 'Autonomous Graph Deliverables:'}</span>
          </span>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {(isBangla ? activeNode.deliverablesBn : activeNode.deliverablesEn).map((item, i) => (
              <div
                key={i}
                className="flex items-center gap-2 p-2 rounded-md bg-surface border border-border/60 text-[11px] text-muted-foreground font-medium"
              >
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500 shrink-0" />
                <span>{item}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

