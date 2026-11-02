'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { ArrowRight, Users } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { CollectiveClassActionModal } from './CollectiveClassActionModal';

export interface OffenderItem {
  merchant_name: string;
  platform: string;
  category: string;
  complaint_count: number;
  total_disputed_bdt: number;
  risk_level: string;
  primary_allegation: string;
  last_reported_date: string;
}

export function ScamRadarOffendersList({
  offenders,
  locale = 'bn',
}: {
  offenders: OffenderItem[];
  locale?: string;
}) {
  const isBangla = locale === 'bn';
  const [selectedOffender, setSelectedOffender] = useState<OffenderItem | null>(null);

  return (
    <>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {offenders.map((offender, i) => (
          <Card key={i} className="border border-border bg-surface hover:shadow-md transition-all flex flex-col justify-between">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between gap-2 mb-2">
                <Badge variant={offender.risk_level.includes('HIGH') ? 'danger' : 'warning'}>
                  {offender.risk_level}
                </Badge>
                <span className="text-xs font-mono font-bold text-[var(--danger-ink)]">
                  {offender.complaint_count} {isBangla ? 'টি অভিযোগ' : 'Complaints'}
                </span>
              </div>

              <CardTitle className="text-base font-bold text-foreground">
                {offender.merchant_name}
              </CardTitle>
              <CardDescription className="text-xs">
                {offender.platform} · {offender.category}
              </CardDescription>
            </CardHeader>

            <CardContent className="space-y-3 text-xs flex-1 flex flex-col justify-between pt-0">
              <div className="p-3 rounded-xl bg-elevated/60 border border-border/80 space-y-1">
                <span className="text-[10px] uppercase font-bold text-muted-foreground tracking-wider block">
                  {isBangla ? 'মূল অভিযোগের বিবরণ:' : 'Primary Allegation:'}
                </span>
                <p className="text-foreground/90 leading-relaxed">
                  {offender.primary_allegation}
                </p>
              </div>

              <div className="pt-2 border-t border-border flex items-center justify-between">
                <div>
                  <span className="text-[10px] text-muted-foreground block">{isBangla ? 'মোট বিরোধ:' : 'Total Disputed:'}</span>
                  <span className="font-extrabold text-foreground">
                    ৳{offender.total_disputed_bdt.toLocaleString(isBangla ? 'bn-BD' : 'en-US')}
                  </span>
                </div>

                <div className="flex items-center gap-2">
                  <button
                    type="button"
                    onClick={() => setSelectedOffender(offender)}
                    className="inline-flex items-center gap-1 text-xs font-bold text-rose-600 dark:text-rose-400 hover:underline cursor-pointer"
                    title="View & Join Collective Class Action"
                  >
                    <Users className="w-3.5 h-3.5" />
                    <span>{isBangla ? 'যৌথ পিটিশন' : 'Class Action'}</span>
                  </button>
                  <Link
                    href={`/${locale}/cases/new`}
                    className="inline-flex items-center gap-1 text-xs font-bold text-primary hover:underline"
                  >
                    <span>{isBangla ? 'অভিযোগ' : 'Dispute'}</span>
                    <ArrowRight className="w-3 h-3" />
                  </Link>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {selectedOffender && (
        <CollectiveClassActionModal
          isOpen={!!selectedOffender}
          onClose={() => setSelectedOffender(null)}
          merchantName={selectedOffender.merchant_name}
          platform={selectedOffender.platform}
          complaintCount={selectedOffender.complaint_count}
          totalDisputedBdt={selectedOffender.total_disputed_bdt}
          locale={locale}
        />
      )}
    </>
  );
}

