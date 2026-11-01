'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  FileText,
  Layers,
  Compass,
  CheckCircle,
  Clock,
  ChevronRight,
  ShieldAlert,
} from 'lucide-react';

interface CaseProgressStepperProps {
  caseId: string;
  locale: string;
  merchantName?: string | null;
}

export function CaseProgressStepper({
  caseId,
  locale,
  merchantName,
}: CaseProgressStepperProps) {
  const pathname = usePathname();
  const isBangla = locale === 'bn';

  const steps = [
    {
      id: 'overview',
      num: 1,
      title: isBangla ? '১. সারসংক্ষেপ' : '1. Overview',
      subtitle: isBangla ? 'কী ঘটেছে' : 'Case incident',
      href: `/${locale}/cases/${caseId}`,
      icon: FileText,
      exact: true,
    },
    {
      id: 'evidence',
      num: 2,
      title: isBangla ? '২. প্রমাণাদি ভল্ট' : '2. Evidence Vault',
      subtitle: isBangla ? 'রসিদ ও চ্যাট' : 'Receipts & chats',
      href: `/${locale}/cases/${caseId}/evidence`,
      icon: Layers,
    },
    {
      id: 'paths',
      num: 3,
      title: isBangla ? '৩. আইনি পথ' : '3. Legal Routes',
      subtitle: isBangla ? 'প্রযোজ্য ধারা' : 'Viable pathways',
      href: `/${locale}/cases/${caseId}/paths`,
      icon: Compass,
    },
    {
      id: 'actions',
      num: 4,
      title: isBangla ? '৪. পদক্ষেপ ও খসড়া' : '4. Action Studio',
      subtitle: isBangla ? 'অভিযোগপত্র' : 'DNCRP Petition',
      href: `/${locale}/cases/${caseId}/actions`,
      icon: CheckCircle,
    },
    {
      id: 'activity',
      num: 5,
      title: isBangla ? '৫. ফলো-আপ' : '5. Follow-Up',
      subtitle: isBangla ? 'সময়সীমা ট্র্যাকিং' : '30-day timeline',
      href: `/${locale}/cases/${caseId}/activity`,
      icon: Clock,
    },
  ];

  const getIsActive = (step: typeof steps[0]) => {
    if (step.exact) {
      return pathname === step.href;
    }
    return pathname?.startsWith(step.href);
  };

  return (
    <div className="w-full bg-surface border border-border/80 rounded-2xl p-3 sm:p-4 shadow-2xs mb-6">
      <div className="flex items-center justify-between mb-3 px-1 text-xs">
        <span className="font-semibold text-foreground flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-primary animate-pulse" />
          <span>{isBangla ? 'আইনি প্রতিকার ধাপসমূহ (Guided Resolution Pipeline):' : 'Case Resolution Pipeline:'}</span>
        </span>
        <span className="text-muted-foreground text-[11px] font-medium hidden sm:inline-block">
          {isBangla ? 'ধাপে ধাপে অনুসরণ করে সহজে প্রতিকার পান' : 'Step-by-step guidance towards formal recovery'}
        </span>
      </div>

      <nav aria-label="Case Progress Pipeline" className="grid grid-cols-2 sm:grid-cols-5 gap-2 sm:gap-2">
        {steps.map((step, idx) => {
          const isActive = getIsActive(step);
          const Icon = step.icon;

          return (
            <Link
              key={step.id}
              href={step.href}
              className={`flex items-center gap-2.5 p-2.5 rounded-xl border transition-all text-left group ${
                isActive
                  ? 'border-primary bg-[var(--brand-soft)] shadow-2xs text-primary'
                  : 'border-border/70 bg-elevated/40 hover:bg-elevated hover:border-border text-muted-foreground hover:text-foreground'
              }`}
            >
              <div
                className={`w-7 h-7 rounded-lg flex items-center justify-center shrink-0 font-bold text-xs ${
                  isActive
                    ? 'bg-primary text-primary-foreground shadow-2xs'
                    : 'bg-surface border border-border text-foreground group-hover:border-primary/40'
                }`}
              >
                <Icon className="w-3.5 h-3.5" />
              </div>
              <div className="min-w-0 flex-1">
                <span className={`block text-xs font-bold truncate ${isActive ? 'text-primary' : 'text-foreground'}`}>
                  {step.title}
                </span>
                <span className="block text-[10px] text-muted-foreground truncate">
                  {step.subtitle}
                </span>
              </div>
            </Link>
          );
        })}
      </nav>
    </div>
  );
}
