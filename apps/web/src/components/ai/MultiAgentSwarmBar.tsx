'use client';

import React, { useState } from 'react';
import {
  Scan,
  Scale,
  Compass,
  FileEdit,
  CheckCircle2,
  ChevronDown,
  ChevronUp,
  Cpu,
  Sparkles,
  Shield,
  Layers,
} from 'lucide-react';

export interface SwarmAgent {
  id: string;
  name: string;
  nameBn: string;
  role: string;
  roleBn: string;
  status: 'verified' | 'active' | 'ready' | 'idle';
  summary: string;
  summaryBn: string;
  metric: string;
  icon: React.ElementType;
  accentColor: string;
  details: {
    engine: string;
    runtimeMs: number;
    statutoryBasis: string;
    outputKey: string;
  };
}

const DEFAULT_AGENTS: SwarmAgent[] = [
  {
    id: 'forensic',
    name: 'Forensic VLM Agent',
    nameBn: 'ফরেনসিক এভিডেন্স এজেন্ট',
    role: 'Document & Tamper Auditor',
    roleBn: 'ডকুমেন্ট ও পেমেন্ট অডিটর',
    status: 'verified',
    summary: 'Matched ৳3,200.00 across bKash MFS TrxID BL9X882KZP and invoice',
    summaryBn: 'বিকাশ স্লিপ ও ইনভয়েসের মধ্যে ৩,২০০ টাকার ১০০% মিল পাওয়া গেছে',
    metric: '0.00 BDT Discrepancy',
    icon: Scan,
    accentColor: 'text-emerald-500 bg-emerald-500/10 border-emerald-500/20',
    details: {
      engine: 'Multimodal VLM + Tesseract OCR Grounding',
      runtimeMs: 142,
      statutoryBasis: 'ISO/IEC 27037 Digital Evidence Admissibility',
      outputKey: 'EvidenceVault Item #bkash-slip-3200 (100% Match)',
    },
  },
  {
    id: 'statute',
    name: 'Statutory Law Agent',
    nameBn: 'লিগ্যাল রিসার্চ এজেন্ট',
    role: 'Laws of BD & Limitation Auditor',
    roleBn: 'আইনি ধারা ও তামাদি যাচাইকারী',
    status: 'verified',
    summary: 'Dispute filed on day 12 of statutory 30-day window under Sec 60',
    summaryBn: 'ধারা ৬০ অনুযায়ী ৩০ দিনের মধ্যে ১২তম দিনে কেস দাখিল',
    metric: '18 Days Remaining',
    icon: Scale,
    accentColor: 'text-blue-500 bg-blue-500/10 border-blue-500/20',
    details: {
      engine: 'Laws of Bangladesh RAG Subgraph Traversal',
      runtimeMs: 96,
      statutoryBasis: 'Consumer Rights Protection Act 2009, Sec 45, 53 & 60',
      outputKey: 'Remedial Grounds: Section 45 (Misleading Trade Practice)',
    },
  },
  {
    id: 'strategist',
    name: 'Procedural Strategist',
    nameBn: 'প্রসিডিউরাল স্ট্র্যাটেজিস্ট',
    role: 'Multi-Venue Viability Engine',
    roleBn: 'আইনি পথ ও সম্ভাবনা আর্কিটেক্ট',
    status: 'verified',
    summary: 'DNCRP Directorate identified as highest ROI avenue (92% Viability)',
    summaryBn: 'ভোক্তা অধিকার অধিদপ্তরকে ৯২% সম্ভাবনাময় পথ হিসেবে নির্ধারণ',
    metric: '92% Viability Score',
    icon: Compass,
    accentColor: 'text-purple-500 bg-purple-500/10 border-purple-500/20',
    details: {
      engine: 'Deterministic AST Procedural Rule Engine',
      runtimeMs: 84,
      statutoryBasis: 'DNCRP CCMS Administrative Resolution Schedule',
      outputKey: 'Primary Route: Consumer Rights Directorate Arbitration',
    },
  },
  {
    id: 'draftsman',
    name: 'Autonomous Draftsman',
    nameBn: 'লিগ্যাল ড্রাফটিং এজেন্ট',
    role: 'Statutory Notice & Docket Generator',
    roleBn: 'নোটিশ ও ড্রাফট প্রস্তুতকারী',
    status: 'ready',
    summary: 'Bilingual Formal 7-day Demand Notice prepared for courier dispatch',
    summaryBn: '৭ দিনের আনুষ্ঠানিক আইনি ডিমান্ড নোটিশ ড্রাফট সম্পন্ন',
    metric: 'Pre-Action Staged',
    icon: FileEdit,
    accentColor: 'text-amber-500 bg-amber-500/10 border-amber-500/20',
    details: {
      engine: 'Generative Legal AST Template Synthesizer',
      runtimeMs: 90,
      statutoryBasis: 'Pre-Action Conduct Requirements (BD Civil Practice)',
      outputKey: 'Notice Document ID: DRAFT-NOTICE-GP-9920',
    },
  },
];

interface MultiAgentSwarmBarProps {
  agents?: SwarmAgent[];
  locale?: string;
  className?: string;
}

export function MultiAgentSwarmBar({
  agents = DEFAULT_AGENTS,
  locale = 'en',
  className = '',
}: MultiAgentSwarmBarProps) {
  const isBangla = locale === 'bn';
  const [selectedAgentId, setSelectedAgentId] = useState<string | null>(null);

  const selectedAgent = agents.find((a) => a.id === selectedAgentId);

  return (
    <div
      className={`rounded-2xl border border-emerald-500/25 bg-gradient-to-r from-emerald-500/[0.04] via-surface to-surface shadow-xs overflow-hidden ${className}`}
    >
      {/* Top Swarm Header */}
      <div className="px-5 py-3 border-b border-border/70 flex flex-col sm:flex-row sm:items-center justify-between gap-2 bg-surface/50">
        <div className="flex items-center gap-2.5">
          <div className="w-7 h-7 rounded-lg bg-emerald-500/10 text-emerald-500 border border-emerald-500/20 flex items-center justify-center shrink-0">
            <Layers className="w-4 h-4 animate-pulse" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold text-foreground flex items-center gap-1.5">
                ✦ {isBangla ? 'মাল্টি-এজেন্ট লিগ্যাল টিম' : 'Active Multi-Agent Swarm'}
              </span>
              <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded-full bg-emerald-500/15 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20 flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-ping inline-block" />
                4 AGENTS COLLABORATING
              </span>
            </div>
            <p className="text-[11px] text-muted-foreground">
              {isBangla
                ? 'আপনার কেসের সুরক্ষায় ৪টি বিশেষায়িত এআই এজেন্ট দলবদ্ধভাবে নিয়োজিত'
                : 'Four specialized autonomous agents synchronously advocating for your resolution'}
            </p>
          </div>
        </div>

        <span className="text-[11px] font-mono text-muted-foreground self-start sm:self-center">
          {isBangla ? 'এজেন্টে ক্লিক করে বিস্তারিত দেখুন' : 'Click agent to inspect telemetry'}
        </span>
      </div>

      {/* 4 Agent Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 divide-y sm:divide-y-0 sm:divide-x divide-border">
        {agents.map((agent) => {
          const Icon = agent.icon;
          const isSelected = selectedAgentId === agent.id;

          return (
            <button
              key={agent.id}
              type="button"
              onClick={() => setSelectedAgentId(isSelected ? null : agent.id)}
              className={`p-3.5 text-left transition-all relative flex flex-col justify-between focus:outline-none ${
                isSelected
                  ? 'bg-emerald-500/10 ring-1 ring-inset ring-emerald-500/40'
                  : 'hover:bg-surface/80 bg-surface/30'
              }`}
            >
              <div className="space-y-1.5">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div
                      className={`w-6 h-6 rounded-md flex items-center justify-center border ${agent.accentColor}`}
                    >
                      <Icon className="w-3.5 h-3.5" />
                    </div>
                    <span className="text-xs font-bold text-foreground">
                      {isBangla ? agent.nameBn : agent.name}
                    </span>
                  </div>
                  <span className="text-[10px] font-mono font-bold px-1.5 py-0.5 rounded bg-surface border border-border text-foreground">
                    {agent.metric}
                  </span>
                </div>

                <span className="text-[10px] uppercase font-mono tracking-wider text-muted-foreground block">
                  {isBangla ? agent.roleBn : agent.role}
                </span>

                <p className="text-[11px] text-muted-foreground line-clamp-2 leading-relaxed">
                  {isBangla ? agent.summaryBn : agent.summary}
                </p>
              </div>

              <div className="pt-2 flex items-center justify-between text-[10px] text-emerald-600 dark:text-emerald-400 font-semibold font-mono">
                <span className="flex items-center gap-1">
                  <CheckCircle2 className="w-3 h-3 text-emerald-500" />
                  {agent.status.toUpperCase()}
                </span>
                <span>{isSelected ? '▲ Close' : '▼ Inspect'}</span>
              </div>
            </button>
          );
        })}
      </div>

      {/* Selected Agent Telemetry Detail Drawer */}
      {selectedAgent && (
        <div className="p-4 bg-slate-950/20 dark:bg-slate-950/60 border-t border-border space-y-3 animate-fadeIn">
          <div className="flex justify-between items-center text-xs">
            <span className="font-bold text-foreground flex items-center gap-1.5">
              <Cpu className="w-3.5 h-3.5 text-emerald-500" />
              {isBangla ? selectedAgent.nameBn : selectedAgent.name} • Internal Telemetry Audit
            </span>
            <span className="font-mono text-[11px] text-muted-foreground">
              Latency: {selectedAgent.details.runtimeMs}ms
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
            <div className="p-2.5 rounded-lg bg-surface border border-border space-y-0.5">
              <span className="text-[10px] text-muted-foreground uppercase font-mono block">
                Model / Execution Engine
              </span>
              <span className="font-semibold text-foreground">{selectedAgent.details.engine}</span>
            </div>
            <div className="p-2.5 rounded-lg bg-surface border border-border space-y-0.5">
              <span className="text-[10px] text-muted-foreground uppercase font-mono block">
                Statutory Governing Law
              </span>
              <span className="font-semibold text-primary">{selectedAgent.details.statutoryBasis}</span>
            </div>
            <div className="p-2.5 rounded-lg bg-surface border border-border space-y-0.5">
              <span className="text-[10px] text-muted-foreground uppercase font-mono block">
                Certified Output Artifact
              </span>
              <span className="font-mono text-emerald-600 dark:text-emerald-400 truncate block">
                {selectedAgent.details.outputKey}
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

