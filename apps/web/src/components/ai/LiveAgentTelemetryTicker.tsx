'use client';

import React, { useState, useEffect } from 'react';
import {
  Activity,
  Scan,
  Scale,
  Radar,
  FileCheck2,
  Terminal,
  ChevronRight,
  ShieldAlert,
  Sparkles,
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface TelemetryPulse {
  id: string;
  agent: string;
  agentBn: string;
  icon: React.ElementType;
  color: string;
  metric: string;
  messageEn: string;
  messageBn: string;
  routeHint?: string;
}

const TELEMETRY_STREAM: TelemetryPulse[] = [
  {
    id: 'forensic-1',
    agent: 'Forensic VLM',
    agentBn: 'ফরেনসিক ভিএলএম',
    icon: Scan,
    color: 'text-emerald-500',
    metric: '99.8% match',
    messageEn: 'bKash TrxID BL9X882KZP cross-checked with Steadfast courier payload',
    messageBn: 'বিকাশ TrxID ও স্টেডফাস্ট কুরিয়ার স্লিপের ডিজিটাল সত্যতা নিশ্চিত',
  },
  {
    id: 'statute-1',
    agent: 'Statutory Watcher',
    agentBn: 'তামাদি আইন পর্যবেক্ষক',
    icon: Scale,
    color: 'text-sky-500',
    metric: 's.45 Active',
    messageEn: 'Consumer Rights Act 2009: 30-day filing limitation gate active',
    messageBn: 'ভোক্তা অধিকার আইন ২০০৯: ৩০ দিনের তামাদি সময়সীমা সক্রিয়ভাবে নজরদারিতে',
  },
  {
    id: 'scam-1',
    agent: 'Scam Radar Network',
    agentBn: 'মার্চেন্ট স্ক্যাম রাডার',
    icon: Radar,
    color: 'text-amber-500',
    metric: '18 reports',
    messageEn: 'Unresolved return complaints logged for rogue Facebook merchants in Mirpur',
    messageBn: 'ফেসবুক পেইজ মার্চেন্টদের অমীমাংসিত অভিযোগ ক্লাস্টার শনাক্ত',
  },
  {
    id: 'draft-1',
    agent: 'Autonomous Draftsman',
    agentBn: 'অটোনোমাস ড্রাফটসম্যান',
    icon: FileCheck2,
    color: 'text-indigo-400',
    metric: '3 notice styles',
    messageEn: '72-Hour Pre-Action Demand Notice auto-grounded with Section 45 statutory citations',
    messageBn: 'ধারা ৪৫ সংযুক্ত ৭২-ঘণ্টার প্রি-অ্যাকশন আইনি নোটিশ খসড়া প্রস্তুত',
  },
];

export function LiveAgentTelemetryTicker({
  locale = 'en',
  onOpenPalette,
}: {
  locale?: string;
  onOpenPalette?: () => void;
}) {
  const isBangla = locale === 'bn';
  const [index, setIndex] = useState(0);
  const [fade, setFade] = useState(true);

  useEffect(() => {
    const timer = setInterval(() => {
      setFade(false);
      setTimeout(() => {
        setIndex((prev) => (prev + 1) % TELEMETRY_STREAM.length);
        setFade(true);
      }, 250);
    }, 4500);

    return () => clearInterval(timer);
  }, []);

  const current = TELEMETRY_STREAM[index];
  const Icon = current.icon;

  return (
    <div className="w-full bg-elevated/70 border-b border-border/60 py-1.5 px-4 md:px-8 text-xs select-none backdrop-blur-xs transition-colors">
      <div className="max-w-7xl mx-auto flex items-center justify-between gap-3">
        {/* Left: Swarm active pulse & rotating ticker */}
        <div className="flex items-center gap-2.5 min-w-0">
          <div className="flex items-center gap-1.5 shrink-0 bg-surface/80 border border-border/60 px-2 py-0.5 rounded-full">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
            </span>
            <span className="text-[10px] font-mono font-bold uppercase tracking-wider text-muted-foreground">
              {isBangla ? 'এজেন্ট সোয়ার্ম' : 'Swarm Live'}
            </span>
          </div>

          <div
            className={cn(
              'flex items-center gap-2 min-w-0 transition-opacity duration-200',
              fade ? 'opacity-100' : 'opacity-0'
            )}
          >
            <span
              className={cn(
                'flex items-center gap-1 text-[11px] font-bold shrink-0',
                current.color
              )}
            >
              <Icon className="w-3.5 h-3.5" />
              <span>{isBangla ? current.agentBn : current.agent}</span>
            </span>

            <span className="text-muted-foreground/40 hidden sm:inline">•</span>

            <span className="text-[11px] text-muted-foreground truncate">
              {isBangla ? current.messageBn : current.messageEn}
            </span>

            <span className="hidden md:inline-flex text-[10px] font-mono text-muted-foreground/80 bg-surface/60 border border-border/40 px-1.5 py-0.2 rounded shrink-0">
              {current.metric}
            </span>
          </div>
        </div>

        {/* Right: Agent Palette Trigger (⌘K / Ctrl+K) */}
        <div className="shrink-0 flex items-center gap-2">
          <button
            type="button"
            onClick={() => {
              if (onOpenPalette) {
                onOpenPalette();
              } else if (typeof window !== 'undefined') {
                window.dispatchEvent(new CustomEvent('claimcraft:open-palette'));
              }
            }}
            className="flex items-center gap-1.5 text-[11px] font-medium text-muted-foreground hover:text-foreground bg-surface/80 hover:bg-surface border border-border/70 hover:border-border rounded-md px-2 py-0.5 transition-all shadow-2xs group"
            title="Open AI Command Palette (Ctrl+K or ⌘K)"
          >
            <Sparkles className="w-3 h-3 text-amber-500 group-hover:rotate-12 transition-transform" />
            <span className="hidden sm:inline">
              {isBangla ? 'এজেন্ট অ্যাকশনস' : 'Agent Actions'}
            </span>
            <kbd className="hidden sm:inline-flex items-center gap-0.5 font-mono text-[9px] bg-elevated px-1 py-0.2 rounded border border-border/70 text-muted-foreground">
              <span>⌘</span>K
            </kbd>
          </button>
        </div>
      </div>
    </div>
  );
}

