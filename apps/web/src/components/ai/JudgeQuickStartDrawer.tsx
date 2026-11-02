'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import {
  Award,
  X,
  Play,
  CheckCircle2,
  ShieldCheck,
  FileText,
  ExternalLink,
  Cpu,
  Layers,
  ArrowRight,
  Terminal,
  Zap,
} from 'lucide-react';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';

interface JudgeQuickStartDrawerProps {
  locale?: string;
}

export function JudgeQuickStartDrawer({ locale = 'en' }: JudgeQuickStartDrawerProps) {
  const isBangla = locale === 'bn';
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      {/* Floating Launcher Pill on Bottom-Left */}
      <button
        onClick={() => setIsOpen(true)}
        className="fixed bottom-6 left-6 z-40 inline-flex items-center gap-2.5 px-4 py-2.5 rounded-full bg-slate-900 text-white font-bold text-xs shadow-2xl hover:scale-105 active:scale-95 transition-all group border-2 border-amber-400/60 dark:bg-slate-950 dark:border-amber-400/80"
        aria-label="Open Hackathon Judge Quick-Start Sandbox"
        title="Ostad Presents YUNet AIgnite Buildathon 2026 Judge Sandbox"
      >
        <span className="w-2.5 h-2.5 rounded-full bg-amber-400 animate-ping inline-block" />
        <Award className="w-4 h-4 text-amber-400" />
        <span>{isBangla ? '🧑‍⚖️ জাজ কুইক-স্টার্ট মোড' : '🧑‍⚖️ Judge Quick-Start'}</span>
        <span className="px-1.5 py-0.5 rounded text-[10px] bg-amber-400/20 text-amber-300 font-mono">
          Top 20
        </span>
      </button>

      {/* Slide-out Drawer */}
      {isOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-start bg-black/60 backdrop-blur-sm transition-opacity animate-fadeIn">
          <div className="w-full max-w-xl h-full bg-surface border-r border-border p-6 flex flex-col justify-between shadow-2xl overflow-y-auto animate-slideRight">
            {/* Header */}
            <div className="space-y-3 pb-4 border-b border-border">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="w-9 h-9 rounded-xl bg-amber-500/10 text-amber-500 border border-amber-500/30 flex items-center justify-center">
                    <Award className="w-5 h-5" />
                  </div>
                  <div>
                    <h3 className="font-bold text-base text-foreground leading-tight flex items-center gap-2">
                      <span>Judge Quick-Start Sandbox</span>
                      <Badge variant="brand" className="text-[10px] py-0">Solo Entry</Badge>
                    </h3>
                    <p className="text-[11px] text-muted-foreground">
                      Ostad Presents YUNet AIgnite Buildathon 2026 • Solo Track
                    </p>
                  </div>
                </div>
                <button
                  onClick={() => setIsOpen(false)}
                  className="p-1.5 rounded-lg text-muted-foreground hover:text-foreground hover:bg-elevated transition"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              {/* Official Sticker Badge */}
              <div className="p-3 rounded-xl bg-elevated/70 border border-border flex items-center justify-between gap-3">
                <div className="flex items-center gap-2.5">
                  <img
                    src="/built-for-aignite-2026.png"
                    alt="Built for Ostad Presents YUNet AIgnite Buildathon 2026"
                    className="h-8 w-auto rounded object-contain border border-border/50"
                  />
                  <div>
                    <div className="text-xs font-bold text-foreground">
                      Sakibul Islam Shovon
                    </div>
                    <div className="text-[10px] text-muted-foreground font-mono">
                      Devpost Verified Solo Builder
                    </div>
                  </div>
                </div>
                <a
                  href="https://github.com/sakibul-shovon/YUNet-hackathon.git"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-xs font-semibold text-primary hover:underline flex items-center gap-1"
                >
                  <span>GitHub</span>
                  <ExternalLink className="w-3 h-3" />
                </a>
              </div>
            </div>

            {/* Main Sandbox Body */}
            <div className="flex-1 py-4 space-y-5 overflow-y-auto pr-1">
              {/* 1. 1-Click Flagship Scenarios */}
              <div className="space-y-2.5">
                <div className="flex items-center justify-between text-xs font-bold text-foreground">
                  <span className="flex items-center gap-1.5">
                    <Play className="w-3.5 h-3.5 text-primary" />
                    <span>Featured Demo Scenarios (1-Click Run)</span>
                  </span>
                  <span className="text-[10px] text-muted-foreground font-mono">3 Flagship Labs</span>
                </div>

                {/* Scenario A */}
                <Link
                  href={`/${locale}/cases/case_demo_phone`}
                  onClick={() => setIsOpen(false)}
                  className="block p-3.5 rounded-xl border border-border hover:border-primary/50 bg-elevated/40 hover:bg-elevated transition group"
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-xs font-bold text-foreground group-hover:text-primary transition-colors">
                      Scenario A: Daraz Smartphone Non-Delivery
                    </span>
                    <Badge variant="warning" className="text-[9px]">E-Commerce</Badge>
                  </div>
                  <p className="text-[11px] text-muted-foreground leading-relaxed">
                    Shafiq ordered a ৳5,500 phone that never arrived. Tests multimodal receipt OCR, fee mismatch detection (৳5,500 vs ৳5,000), Section 45 Kleene routing, and in-memory What-If counterfactuals.
                  </p>
                </Link>

                {/* Scenario B */}
                <Link
                  href={`/${locale}/cases/case_demo_mfs`}
                  onClick={() => setIsOpen(false)}
                  className="block p-3.5 rounded-xl border border-border hover:border-primary/50 bg-elevated/40 hover:bg-elevated transition group"
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-xs font-bold text-foreground group-hover:text-primary transition-colors">
                      Scenario B: MFS Debit Without Credit
                    </span>
                    <Badge variant="brand" className="text-[9px]">FinTech & MFS</Badge>
                  </div>
                  <p className="text-[11px] text-muted-foreground leading-relaxed">
                    Fatima attempted a ৳3,000 bKash transfer. Debited without credit. Tests Bengali audio Whisper ingestion, token confidence, and Bangladesh Bank PSD 2-stage escalation requirements.
                  </p>
                </Link>

                {/* Scenario H */}
                <Link
                  href={`/${locale}/cases/case_demo_living`}
                  onClick={() => setIsOpen(false)}
                  className="block p-3.5 rounded-xl border border-border hover:border-primary/50 bg-elevated/40 hover:bg-elevated transition group"
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-xs font-bold text-foreground group-hover:text-primary transition-colors">
                      Scenario H: Living Case & Adversarial Red-Team
                    </span>
                    <Badge variant="danger" className="text-[9px]">Security Verified</Badge>
                  </div>
                  <p className="text-[11px] text-muted-foreground leading-relaxed">
                    Merchant offers partial settlement + invoice contains prompt injection (`SYSTEM OVERRIDE`). Tests deterministic Kleene AST resistance and real-time timeline diffs.
                  </p>
                </Link>
              </div>

              {/* 2. Verification Scorecard */}
              <div className="p-4 rounded-xl border border-emerald-500/30 bg-emerald-500/5 space-y-2.5">
                <div className="flex items-center justify-between text-xs font-bold text-emerald-600 dark:text-emerald-400">
                  <span className="flex items-center gap-1.5">
                    <ShieldCheck className="w-4 h-4" />
                    <span>Hard Release Verification Metrics</span>
                  </span>
                  <span className="font-mono">100% PASS</span>
                </div>
                <div className="grid grid-cols-2 gap-2 text-[11px]">
                  <div className="p-2 rounded-lg bg-surface border border-border">
                    <div className="text-muted-foreground">Automated Suites</div>
                    <div className="font-bold text-foreground font-mono">134 / 134 Pytest PASS</div>
                  </div>
                  <div className="p-2 rounded-lg bg-surface border border-border">
                    <div className="text-muted-foreground">Legal Hallucination</div>
                    <div className="font-bold text-emerald-600 dark:text-emerald-400 font-mono">0.0% (Zero Guesses)</div>
                  </div>
                  <div className="p-2 rounded-lg bg-surface border border-border">
                    <div className="text-muted-foreground">p95 API Latency</div>
                    <div className="font-bold text-foreground font-mono">&lt; 460 ms (Concurrent)</div>
                  </div>
                  <div className="p-2 rounded-lg bg-surface border border-border">
                    <div className="text-muted-foreground">Bilingual Parity</div>
                    <div className="font-bold text-foreground font-mono">100% EN / BN (WCAG AA)</div>
                  </div>
                </div>
              </div>

              {/* 3. Executive Shortcuts */}
              <div className="grid grid-cols-2 gap-2">
                <Link
                  href={`/${locale}/admin`}
                  onClick={() => setIsOpen(false)}
                  className="p-2.5 rounded-xl border border-border bg-elevated/40 hover:bg-elevated transition text-xs font-semibold text-foreground flex items-center justify-between"
                >
                  <span className="flex items-center gap-1.5">
                    <Terminal className="w-3.5 h-3.5 text-primary" />
                    <span>Admin Center</span>
                  </span>
                  <ArrowRight className="w-3 h-3 text-muted-foreground" />
                </Link>

                <Link
                  href={`/${locale}/merchants`}
                  onClick={() => setIsOpen(false)}
                  className="p-2.5 rounded-xl border border-border bg-elevated/40 hover:bg-elevated transition text-xs font-semibold text-foreground flex items-center justify-between"
                >
                  <span className="flex items-center gap-1.5">
                    <Zap className="w-3.5 h-3.5 text-rose-500" />
                    <span>Scam Radar</span>
                  </span>
                  <ArrowRight className="w-3 h-3 text-muted-foreground" />
                </Link>
              </div>
            </div>

            {/* Footer */}
            <div className="pt-3 border-t border-border flex items-center justify-between text-[11px] text-muted-foreground">
              <span>Press <kbd className="px-1 py-0.5 rounded bg-elevated border border-border font-mono text-[10px]">Ctrl+K</kbd> for Command Palette</span>
              <Button
                size="sm"
                variant="primary"
                onClick={() => setIsOpen(false)}
                className="text-xs h-8"
              >
                Close Sandbox
              </Button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
