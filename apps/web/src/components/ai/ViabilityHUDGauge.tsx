'use client';

import React, { useState, useEffect } from 'react';
import { ShieldCheck, AlertCircle, ArrowUpRight, TrendingUp, Sliders } from 'lucide-react';

interface ViabilityHUDGaugeProps {
  score?: number; // 0 to 100
  title?: string;
  subtitle?: string;
  venueName?: string;
  evidenceWeight?: number;
  statutoryCompliance?: number;
  interactiveScenario?: boolean;
  className?: string;
}

export function ViabilityHUDGauge({
  score = 92,
  title = 'Case Viability Index',
  subtitle = 'AI Deterministic Legal Probability',
  venueName = 'National Consumer Rights Protection Directorate (DNCRP)',
  evidenceWeight = 98,
  statutoryCompliance = 100,
  interactiveScenario = true,
  className = '',
}: ViabilityHUDGaugeProps) {
  const [currentScore, setCurrentScore] = useState(0);
  const [isCounterfactual, setIsCounterfactual] = useState(false);

  // SVG Gauge Calculations
  const radius = 54;
  const strokeWidth = 9;
  const circumference = 2 * Math.PI * radius;

  useEffect(() => {
    // Smooth entrance spring animation
    const target = isCounterfactual ? 45 : score;
    const timeout = setTimeout(() => {
      setCurrentScore(target);
    }, 150);
    return () => clearTimeout(timeout);
  }, [score, isCounterfactual]);

  const strokeDashoffset = circumference - (currentScore / 100) * circumference;

  const isHigh = currentScore >= 70;
  const isMedium = currentScore >= 50 && currentScore < 70;

  const strokeColor = isHigh ? '#10b981' : isMedium ? '#f59e0b' : '#ef4444';
  const badgeBg = isHigh
    ? 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/20'
    : 'bg-amber-500/10 text-amber-600 dark:text-amber-400 border-amber-500/20';

  return (
    <div
      className={`p-5 rounded-2xl border border-border bg-gradient-to-b from-surface to-surface/80 shadow-xs space-y-4 ${className}`}
    >
      {/* Top Header */}
      <div className="flex justify-between items-start">
        <div>
          <span className="text-[10px] font-mono uppercase tracking-widest text-emerald-500 font-bold flex items-center gap-1">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-ping inline-block" />
            LIVE AI COGNITIVE ASSESSMENT
          </span>
          <h3 className="text-base font-bold text-foreground mt-0.5">{title}</h3>
          <p className="text-xs text-muted-foreground">{subtitle}</p>
        </div>

        {interactiveScenario && (
          <button
            type="button"
            onClick={() => setIsCounterfactual(!isCounterfactual)}
            className="text-[11px] px-2.5 py-1 rounded-lg border border-border bg-surface hover:bg-elevated transition-colors text-muted-foreground hover:text-foreground flex items-center gap-1"
            title="Toggle lost payment receipt scenario"
          >
            <Sliders className="w-3 h-3 text-primary" />
            <span>{isCounterfactual ? 'Reset' : 'Simulate Lost Receipt'}</span>
          </button>
        )}
      </div>

      {/* Main Gauge & Metrics Breakdown */}
      <div className="flex flex-col sm:flex-row items-center gap-6 pt-1">
        {/* Circular HUD SVG */}
        <div className="relative w-36 h-36 flex items-center justify-center shrink-0">
          <svg className="w-full h-full transform -rotate-90">
            {/* Background track */}
            <circle
              cx="72"
              cy="72"
              r={radius}
              stroke="currentColor"
              strokeWidth={strokeWidth}
              className="text-border/40"
              fill="transparent"
            />
            {/* Animated progress arc */}
            <circle
              cx="72"
              cy="72"
              r={radius}
              stroke={strokeColor}
              strokeWidth={strokeWidth}
              strokeLinecap="round"
              strokeDasharray={circumference}
              strokeDashoffset={strokeDashoffset}
              fill="transparent"
              style={{
                transition: 'stroke-dashoffset 0.8s cubic-bezier(0.16, 1, 0.3, 1), stroke 0.5s ease',
              }}
            />
          </svg>

          {/* Central Percentage Display */}
          <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
            <span
              className="text-3xl font-extrabold tracking-tight font-mono"
              style={{ color: strokeColor }}
            >
              {currentScore}%
            </span>
            <span className="text-[9px] uppercase tracking-wider font-bold text-muted-foreground">
              {isHigh ? 'High Viability' : isMedium ? 'Moderate' : 'Low / Gaps'}
            </span>
          </div>
        </div>

        {/* Sub-Metric Factor Breakdown */}
        <div className="flex-1 w-full space-y-2.5 text-xs">
          <div className="flex justify-between items-center text-muted-foreground pb-1 border-b border-border/50 text-[11px]">
            <span>Optimal Remedial Pathway:</span>
            <span className="font-bold text-foreground text-right truncate max-w-[200px]">
              {venueName}
            </span>
          </div>

          <div className="space-y-1.5">
            <div className="flex justify-between text-[11px]">
              <span className="text-muted-foreground">Evidentiary Completeness</span>
              <span className="font-mono font-bold text-foreground">
                {isCounterfactual ? '40%' : `${evidenceWeight}%`}
              </span>
            </div>
            <div className="w-full h-1.5 rounded-full bg-border overflow-hidden">
              <div
                className="h-full bg-emerald-500 rounded-full transition-all duration-500"
                style={{ width: `${isCounterfactual ? 40 : evidenceWeight}%` }}
              />
            </div>
          </div>

          <div className="space-y-1.5">
            <div className="flex justify-between text-[11px]">
              <span className="text-muted-foreground">Statutory Deadline Adherence</span>
              <span className="font-mono font-bold text-foreground">
                {isCounterfactual ? '60%' : `${statutoryCompliance}%`}
              </span>
            </div>
            <div className="w-full h-1.5 rounded-full bg-border overflow-hidden">
              <div
                className="h-full bg-primary rounded-full transition-all duration-500"
                style={{ width: `${isCounterfactual ? 60 : statutoryCompliance}%` }}
              />
            </div>
          </div>

          {isCounterfactual && (
            <div className="p-2 rounded-lg bg-red-500/10 border border-red-500/20 text-red-500 text-[11px] flex items-center gap-1.5 animate-fadeIn">
              <AlertCircle className="w-3.5 h-3.5 shrink-0" />
              <span>
                Simulated deficit: Missing payment confirmation reduces probability by 47%.
              </span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

