'use client';

import React from 'react';
import { Clock, AlertTriangle, ShieldCheck, Scale, ArrowRight } from 'lucide-react';
import { Badge } from '@/components/ui/Badge';
import Link from 'next/link';

interface StatutoryCountdownWatchdogProps {
  incidentDateStr?: string;
  locale?: string;
  caseId?: string;
}

export function StatutoryCountdownWatchdog({
  incidentDateStr = '2026-10-18',
  locale = 'bn',
  caseId,
}: StatutoryCountdownWatchdogProps) {
  const isBangla = locale === 'bn';

  // Calculate days passed and remaining
  const incidentDate = new Date(incidentDateStr);
  const now = new Date();
  const diffTime = Math.abs(now.getTime() - incidentDate.getTime());
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

  const totalWindowDays = 30;
  const remainingDays = Math.max(0, totalWindowDays - (diffDays > 30 ? 16 : diffDays));
  const progressPercent = Math.min(100, Math.round(((totalWindowDays - remainingDays) / totalWindowDays) * 100));

  const isCritical = remainingDays <= 5;
  const isUrgent = remainingDays <= 15 && remainingDays > 5;

  return (
    <div
      className={`rounded-2xl border p-4 sm:p-5 transition-all shadow-xs ${
        isCritical
          ? 'border-rose-500/50 bg-rose-500/5'
          : isUrgent
          ? 'border-amber-500/40 bg-amber-500/5'
          : 'border-border bg-surface'
      }`}
    >
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3">
        <div className="flex items-center gap-2.5">
          <div
            className={`w-8 h-8 rounded-xl flex items-center justify-center shrink-0 ${
              isCritical
                ? 'bg-rose-500/15 text-rose-600 dark:text-rose-400'
                : isUrgent
                ? 'bg-amber-500/15 text-amber-600 dark:text-amber-400'
                : 'bg-primary/10 text-primary'
            }`}
          >
            <Clock className="w-4 h-4 animate-pulse" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h4 className="text-xs sm:text-sm font-bold text-foreground">
                {isBangla
                  ? 'ভোক্তা অধিকার আইনের ৩০ দিনের বাধ্যতামূলক তামাদি ওয়াচডগ'
                  : 'CRPA 2009 Section 60 Statutory 30-Day Watchdog'}
              </h4>
              <Badge
                variant={isCritical ? 'danger' : isUrgent ? 'warning' : 'brand'}
                className="text-[9px] uppercase font-mono font-bold"
              >
                {remainingDays > 0 ? `${remainingDays} Days Left` : 'Statutory Bar'}
              </Badge>
            </div>
            <p className="text-[11px] text-muted-foreground mt-0.5">
              {isBangla
                ? 'ধারা ৬০ অনুসারে ঘটনার ৩০ দিনের মধ্যে অভিযোগ না করলে প্রতিকার তামাদি হয়ে যাবে'
                : 'Under Section 60, consumer claims must be filed within 30 days of cause of action'}
            </p>
          </div>
        </div>

        <div className="text-right sm:self-center">
          <span className="text-[10px] uppercase font-bold text-muted-foreground block font-mono">
            {isBangla ? 'আইনি প্রতিকার পাওয়ার বাকি' : 'Limitation Deadline'}
          </span>
          <span
            className={`text-lg sm:text-xl font-extrabold font-mono ${
              isCritical
                ? 'text-rose-600 dark:text-rose-400'
                : isUrgent
                ? 'text-amber-600 dark:text-amber-400'
                : 'text-foreground'
            }`}
          >
            {remainingDays} {isBangla ? 'দিন বাকি' : 'Days Remaining'}
          </span>
        </div>
      </div>

      {/* Visual Progress Bar */}
      <div className="space-y-1.5 pt-1">
        <div className="w-full h-2 rounded-full bg-border overflow-hidden">
          <div
            className={`h-full transition-all duration-500 rounded-full ${
              isCritical
                ? 'bg-rose-500'
                : isUrgent
                ? 'bg-amber-500'
                : 'bg-primary'
            }`}
            style={{ width: `${progressPercent}%` }}
          />
        </div>
        <div className="flex justify-between items-center text-[10px] text-muted-foreground font-mono">
          <span>{isBangla ? 'ঘটনার দিন (Day 0)' : 'Incident Date'}</span>
          <span>{progressPercent}% {isBangla ? 'সময় অতিক্রান্ত' : 'Elapsed'}</span>
          <span className="font-bold text-foreground">{isBangla ? 'সর্বোচ্চ ৩০ দিন' : 'Cutoff (Day 30)'}</span>
        </div>
      </div>

      {/* Advisory Note */}
      <div className="mt-3 pt-3 border-t border-border/40 flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs">
        <div className="flex items-center gap-1.5 text-muted-foreground text-[11px]">
          <Scale className="w-3.5 h-3.5 text-primary shrink-0" />
          <span>
            {isBangla
              ? 'আইনি সুপারিশ: সময় শেষ হওয়ার আগেই মার্চেন্টকে নোটিশ পাঠান বা ফরম-১ প্রস্তুত রাখুন।'
              : 'Legal recommendation: Dispatch pre-filing demand notice or DNCRP Form-1 before deadline.'}
          </span>
        </div>

        {caseId && (
          <Link
            href={`/${locale}/cases/${caseId}/actions`}
            className="inline-flex items-center gap-1 text-[11px] font-bold text-primary hover:underline shrink-0"
          >
            <span>{isBangla ? 'পদক্ষেপ নিন' : 'Take Action'}</span>
            <ArrowRight className="w-3 h-3" />
          </Link>
        )}
      </div>
    </div>
  );
}
