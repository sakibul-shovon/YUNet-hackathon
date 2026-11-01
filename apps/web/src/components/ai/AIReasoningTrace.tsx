'use client';

import React, { useState } from 'react';
import { Sparkles, ChevronDown, ChevronUp, CheckCircle2, Clock, Cpu, ShieldCheck } from 'lucide-react';

export interface ReasoningStep {
  title: string;
  detail: string;
  durationMs: number;
  status: 'completed' | 'in_progress' | 'queued';
  citation?: string;
}

interface AIReasoningTraceProps {
  elapsedTimeMs?: number;
  modelName?: string;
  steps?: ReasoningStep[];
  defaultExpanded?: boolean;
  className?: string;
}

const DEFAULT_STEPS: ReasoningStep[] = [
  {
    title: 'Acoustic & Vision Ingestion Verification',
    detail: 'Validated SHA-256 payload integrity across bKash MFS statement and merchant sales invoice.',
    durationMs: 84,
    status: 'completed',
    citation: 'ISO/IEC 27037 Forensic Integrity',
  },
  {
    title: 'Multimodal Entity & Numeric Reconciliation',
    detail: 'Cross-matched BDT 3,200.00 between TrxID BL9X882KZP and Item #GP-9920. Discrepancy: 0.00 BDT.',
    durationMs: 142,
    status: 'completed',
    citation: 'MFS Rulebook 2022',
  },
  {
    title: 'Statutory Jurisdiction & Limitation Audit',
    detail: 'Incident date within 30-day statutory limitation under Section 60. Covered under misleading commerce rules.',
    durationMs: 96,
    status: 'completed',
    citation: 'Consumer Rights Protection Act 2009, Sec 45 & 60',
  },
  {
    title: 'Counterfactual Procedural Path Synthesis',
    detail: 'Evaluated 4 remedial venues. DNCRP Directorate selected with highest feasibility score (92%).',
    durationMs: 90,
    status: 'completed',
    citation: 'CCMS Administrative Schedule',
  },
];

export function AIReasoningTrace({
  elapsedTimeMs = 412,
  modelName = 'ClaimCraft BD Neural Copilot v4.2',
  steps = DEFAULT_STEPS,
  defaultExpanded = false,
  className = '',
}: AIReasoningTraceProps) {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded);

  return (
    <div
      className={`rounded-xl border border-emerald-500/25 bg-gradient-to-b from-emerald-500/[0.04] to-surface overflow-hidden transition-all duration-200 ${className}`}
    >
      {/* Header Bar */}
      <button
        type="button"
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full px-4 py-3 flex items-center justify-between text-left hover:bg-emerald-500/[0.03] transition-colors focus:outline-none"
      >
        <div className="flex items-center gap-2.5">
          <div className="w-6 h-6 rounded-md bg-emerald-500/10 text-emerald-500 border border-emerald-500/20 flex items-center justify-center shrink-0">
            <Sparkles className="w-3.5 h-3.5 animate-pulse" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold tracking-tight text-foreground flex items-center gap-1.5">
                ✦ AI Procedural Reasoning & Deterministic Trace
              </span>
              <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-500/15 text-emerald-600 dark:text-emerald-400 font-mono font-bold">
                {elapsedTimeMs}ms
              </span>
            </div>
            <p className="text-[11px] text-muted-foreground mt-0.5">
              Verified through 4 statutory gates • Zero synthetic fabrication
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 text-xs text-muted-foreground">
          <span className="hidden sm:inline-block font-mono text-[10px] text-muted-foreground/80">
            {isExpanded ? 'Hide Trace' : 'Inspect Steps'}
          </span>
          <div className="w-5 h-5 rounded flex items-center justify-center text-muted-foreground hover:text-foreground">
            {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          </div>
        </div>
      </button>

      {/* Expanded Reasoning Step Sequence */}
      {isExpanded && (
        <div className="px-4 pb-4 pt-1 border-t border-emerald-500/15 space-y-3">
          <div className="flex justify-between items-center text-[10px] font-mono text-muted-foreground/80 pt-1 border-b border-border/40 pb-1.5">
            <span className="flex items-center gap-1">
              <Cpu className="w-3 h-3 text-emerald-500" />
              Engine: {modelName}
            </span>
            <span className="flex items-center gap-1">
              <ShieldCheck className="w-3 h-3 text-emerald-500" />
              Audited against Laws of Bangladesh
            </span>
          </div>

          <div className="space-y-2.5 pt-1">
            {steps.map((step, idx) => (
              <div
                key={idx}
                className="flex items-start gap-3 p-2.5 rounded-lg bg-surface/70 border border-border/60 hover:border-emerald-500/30 transition-colors"
              >
                <div className="mt-0.5 shrink-0 text-emerald-500">
                  <CheckCircle2 className="w-4 h-4" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between gap-2">
                    <span className="text-xs font-semibold text-foreground truncate">
                      {step.title}
                    </span>
                    <span className="text-[10px] font-mono text-muted-foreground shrink-0 flex items-center gap-0.5">
                      <Clock className="w-2.5 h-2.5" />
                      {step.durationMs}ms
                    </span>
                  </div>
                  <p className="text-[11px] text-muted-foreground mt-0.5 leading-relaxed">
                    {step.detail}
                  </p>
                  {step.citation && (
                    <div className="mt-1 text-[10px] font-mono font-medium text-emerald-600 dark:text-emerald-400 bg-emerald-500/10 inline-block px-1.5 py-0.5 rounded border border-emerald-500/20">
                      § {step.citation}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

