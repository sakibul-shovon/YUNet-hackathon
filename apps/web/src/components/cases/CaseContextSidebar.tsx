'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { Trash2, Shield, Scale, Calendar, DollarSign, Store, Tag } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { apiFetch } from '@/lib/api';
import { formatBdtMoney } from '@/lib/formatters';

interface CaseContextSidebarProps {
  caseId: string;
  locale: string;
}

interface CaseDetails {
  id: string;
  title: string;
  merchant_name?: string | null;
  incident_date?: string | null;
  desired_outcomes?: string[];
  lifecycle_status: string;
  display_reference: string;
}

interface FactAssertion {
  id: string;
  field_name: string;
  field_type: string;
  typed_value: any;
}

export function CaseContextSidebar({ caseId, locale }: CaseContextSidebarProps) {
  const isBangla = locale === 'bn';

  const [caseData, setCaseData] = useState<CaseDetails | null>(null);
  const [facts, setFacts] = useState<FactAssertion[]>([]);
  const [citations, setCitations] = useState<string[]>([]);

  useEffect(() => {
    let isMounted = true;
    Promise.all([
      apiFetch(`/api/v1/cases/${caseId}`).then((r) => (r.ok ? r.json() : null)),
      apiFetch(`/api/v1/cases/${caseId}/facts`).then((r) => (r.ok ? r.json() : [])),
      apiFetch(`/api/v1/cases/${caseId}/assessment`).then((r) => (r.ok ? r.json() : null)),
    ])
      .then(([c, f, a]) => {
        if (!isMounted) return;
        if (c) setCaseData(c);
        if (f) setFacts(f);
        if (a?.routes) {
          const allCits: string[] = [];
          for (const r of a.routes) {
            if (r.statutory_citations) {
              allCits.push(...r.statutory_citations);
            }
          }
          if (allCits.length > 0) {
            setCitations(Array.from(new Set(allCits)));
          }
        }
      })
      .catch((err) => console.error('Failed to load case sidebar info:', err));

    return () => {
      isMounted = false;
    };
  }, [caseId]);

  // Extract real merchant and amount
  const merchantName = caseData?.merchant_name || (isBangla ? 'নির্দিষ্ট নয়' : 'Not specified');
  const incidentDate = caseData?.incident_date || new Date().toISOString().split('T')[0];

  const amountFact = facts.find((f) => f.field_name === 'amount_paid');
  let amountDisplay = isBangla ? 'বিবরণ অনুযায়ী' : 'As stated in narrative';
  let rawAmount = 0;
  if (amountFact) {
    if (typeof amountFact.typed_value === 'object' && amountFact.typed_value?.minor_units) {
      rawAmount = amountFact.typed_value.minor_units;
      amountDisplay = formatBdtMoney(rawAmount, locale);
    } else {
      amountDisplay = `${amountFact.typed_value} BDT`;
    }
  }

  // Outcome label
  const outcome = caseData?.desired_outcomes?.[0] || 'full_refund';
  let outcomeBadge = isBangla ? 'সম্পূর্ণ রিফান্ড' : 'Full Refund';
  if (outcome === 'replacement') {
    outcomeBadge = isBangla ? 'পণ্য প্রতিস্থাপন' : 'Product Replacement';
  } else if (outcome === 'apology') {
    outcomeBadge = isBangla ? 'লিখিত কারণ দর্শানো' : 'Written Explanation';
  } else if (rawAmount > 0) {
    outcomeBadge = isBangla
      ? `সম্পূর্ণ রিফান্ড (${formatBdtMoney(rawAmount, locale)})`
      : `Full Refund (${formatBdtMoney(rawAmount, locale)})`;
  }

  return (
    <aside className="space-y-6">
      {/* 1. Case Summary Card */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-xs font-bold uppercase tracking-wider text-muted-foreground flex items-center gap-1.5">
            <Tag className="w-3.5 h-3.5 text-primary" />
            <span>{isBangla ? 'কেস সংক্ষিপ্ত তথ্য' : 'Case Summary'}</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="text-xs space-y-3">
          <div>
            <span className="text-muted-foreground block text-[11px]">
              {isBangla ? 'বিরোধের ধরণ:' : 'Category:'}
            </span>
            <span className="font-semibold text-foreground">
              {isBangla ? 'ই-কমার্স ও ভোক্তা অধিকার' : 'E-Commerce / Consumer Goods'}
            </span>
          </div>

          <div>
            <span className="text-muted-foreground block text-[11px]">
              {isBangla ? 'দাবিকৃত মোট অর্থ:' : 'Disputed Total:'}
            </span>
            <span className="font-bold text-foreground font-mono text-xs">
              {amountDisplay}
            </span>
          </div>

          <div>
            <span className="text-muted-foreground block text-[11px]">
              {isBangla ? 'ঘটনার তারিখ:' : 'Dispute Date:'}
            </span>
            <span className="font-semibold text-foreground font-mono text-xs">
              {incidentDate}
            </span>
          </div>

          <div>
            <span className="text-muted-foreground block text-[11px]">
              {isBangla ? 'প্রতিপক্ষ মার্চেন্ট/প্রতিষ্ঠান:' : 'Seller/Merchant:'}
            </span>
            <span className="font-semibold text-primary">
              {merchantName}
            </span>
          </div>
        </CardContent>
      </Card>

      {/* 2. Desired Remedy */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-xs font-bold uppercase tracking-wider text-muted-foreground flex items-center gap-1.5">
            <DollarSign className="w-3.5 h-3.5 text-primary" />
            <span>{isBangla ? 'প্রার্থিত প্রতিকার' : 'Desired Outcome'}</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="text-xs space-y-2">
          <Badge variant="brand" className="text-xs">
            {outcomeBadge}
          </Badge>
          <p className="text-muted-foreground text-[11px] leading-relaxed pt-1">
            {isBangla
              ? 'ভোক্তা অধিকার সংরক্ষণ আইন, ২০০৯ অনুযায়ী প্রতিশ্রুত পণ্য সরবরাহ না করা বা ক্ষতিপূরণের দাবি।'
              : 'Claiming statutory remedies and reimbursement under Bangladesh Consumer Rights Protection Act.'}
          </p>
        </CardContent>
      </Card>

      {/* 3. Statutory Legal Authorities */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-xs font-bold uppercase tracking-wider text-muted-foreground flex items-center gap-1.5">
            <Scale className="w-3.5 h-3.5 text-primary" />
            <span>{isBangla ? 'প্রযোজ্য আইনি বিধান' : 'Relevant Legal Authorities'}</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="text-xs space-y-2.5">
          {citations.length > 0 ? (
            citations.slice(0, 3).map((cit, idx) => (
              <div key={idx} className="p-2.5 rounded-md bg-elevated border border-border/80">
                <span className="font-semibold block text-foreground">
                  {cit.startsWith('crpa2009')
                    ? (isBangla ? 'জাতীয় ভোক্তা অধিকার সংরক্ষণ অধিদপ্তর (DNCRP)' : 'DNCRP Consumer Rights Act')
                    : cit.startsWith('bb_cipc')
                      ? (isBangla ? 'বাংলাদেশ ব্যাংক ও এমএফএস নিয়ন্ত্রণ' : 'Bangladesh Bank CIPC Regulations')
                      : cit.startsWith('btrc')
                        ? (isBangla ? 'বিটিআরসি টেলিযোগাযোগ আইন ও কোয়ালিটি সার্কুলার' : 'BTRC Telecom Regulation')
                        : (isBangla ? 'বাংলাদেশ সরকারি অভিযোগ নিষ্পত্তি (GRS)' : 'Cabinet Division GRS Guidelines')}
                </span>
                <span className="text-muted-foreground text-[11px] block mt-0.5 font-mono">
                  {cit.replace(':', ' • ')}
                </span>
              </div>
            ))
          ) : (
            <>
              <div className="p-2.5 rounded-md bg-elevated border border-border/80">
                <span className="font-semibold block text-foreground">
                  {isBangla ? 'জাতীয় ভোক্তা অধিকার সংরক্ষণ অধিদপ্তর (DNCRP)' : 'DNCRP (ভোক্তা অধিকার)'}
                </span>
                <span className="text-muted-foreground text-[11px] block mt-0.5">
                  {isBangla ? 'আইন নং ২৬, ২০০৯ • ধারা ৪৫, ধারা ৭৬' : 'Act No. 26 of 2009 • s.45, s.76'}
                </span>
              </div>

              <div className="p-2.5 rounded-md bg-elevated border border-border/80">
                <span className="font-semibold block text-foreground">
                  {isBangla ? 'বাংলাদেশ ব্যাংক ও এমএফএস নির্দেশিকা' : 'Bangladesh Bank MFS Circular'}
                </span>
                <span className="text-muted-foreground text-[11px] block mt-0.5">
                  {isBangla ? 'ডিজিটাল পেমেন্ট ও রিফান্ড নীতি' : 'PSD Circular 03/2021'}
                </span>
              </div>
            </>
          )}
        </CardContent>
      </Card>

      {/* 4. Data Privacy & Deletion Control */}
      <div className="p-3 rounded-[var(--radius-control)] border border-border bg-surface text-xs text-muted-foreground flex items-center justify-between">
        <span className="flex items-center gap-1.5">
          <Shield className="w-3.5 h-3.5 text-primary" />
          <span>{isBangla ? 'ব্যক্তিগত তথ্য নিয়ন্ত্রণ' : 'Case Data Controls'}</span>
        </span>
        <Link
          href={`/${locale}/settings/data`}
          className="text-red-600 hover:underline inline-flex items-center gap-1 font-semibold text-[11px]"
        >
          <Trash2 className="w-3.5 h-3.5" />
          <span>{isBangla ? 'কেস মুছুন' : 'Delete Case'}</span>
        </Link>
      </div>
    </aside>
  );
}
