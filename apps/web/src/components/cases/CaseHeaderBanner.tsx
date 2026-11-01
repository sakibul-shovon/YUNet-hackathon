'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { ArrowLeft } from 'lucide-react';
import { Badge } from '@/components/ui/Badge';
import { apiFetch } from '@/lib/api';

interface CaseHeaderBannerProps {
  caseId: string;
  locale: string;
  initialTitle: string;
  initialRef: string;
  isDemo?: boolean;
  reviewLabel: string;
}

export function CaseHeaderBanner({
  caseId,
  locale,
  initialTitle,
  initialRef,
  isDemo = false,
  reviewLabel,
}: CaseHeaderBannerProps) {
  const isBangla = locale === 'bn';
  const [title, setTitle] = useState(initialTitle);
  const [ref, setRef] = useState(initialRef);
  const [isDemoCase, setIsDemoCase] = useState(isDemo);

  useEffect(() => {
    let isMounted = true;
    apiFetch(`/api/v1/cases/${caseId}`)
      .then((res) => (res.ok ? res.json() : null))
      .then((data) => {
        if (!isMounted || !data) return;
        if (data.title) setTitle(data.title);
        if (data.display_reference) setRef(data.display_reference);
        if (data.is_demo !== undefined) setIsDemoCase(data.is_demo);
      })
      .catch(() => {});

    return () => {
      isMounted = false;
    };
  }, [caseId]);

  return (
    <div className="border-b border-border bg-surface px-4 md:px-8 py-5">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="space-y-1">
          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            <Link
              href={`/${locale}/cases`}
              className="hover:text-foreground inline-flex items-center gap-1 font-semibold"
            >
              <ArrowLeft className="w-3.5 h-3.5" />
              <span>{isBangla ? 'কেস তালিকা' : 'My Cases'}</span>
            </Link>
            <span>/</span>
            <span className="font-mono text-[11px] font-bold text-foreground">#{ref}</span>
            <Badge variant="brand" className="text-[10px]">
              {isDemoCase
                ? (isBangla ? 'বাস্তবসম্মত ডেমো কেস' : 'Verified Sandbox Case')
                : (isBangla ? 'সক্রিয় বিরোধ' : 'Active Dispute')}
            </Badge>
          </div>
          <h1 className="text-xl md:text-2xl font-bold tracking-tight text-foreground">
            {title}
          </h1>
        </div>

        <div className="flex items-center gap-3">
          <Link
            href={`/${locale}/cases/${caseId}/review`}
            className="inline-flex items-center gap-1.5 text-xs font-semibold px-3 py-1.5 rounded-[var(--radius-control)] border border-primary text-primary hover:bg-[var(--brand-soft)] transition-colors min-h-[38px]"
          >
            <span>{reviewLabel}</span>
          </Link>
        </div>
      </div>
    </div>
  );
}
