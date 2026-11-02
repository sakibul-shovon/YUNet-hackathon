'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { AlertTriangle, ShieldAlert, Users, ExternalLink, ChevronRight, CheckCircle2 } from 'lucide-react';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { apiFetch } from '@/lib/api';
import { CollectiveClassActionModal } from '@/components/merchants/CollectiveClassActionModal';

interface MerchantIntelligenceData {
  merchant_name: string;
  risk_level: string;
  complaint_count: number;
  total_disputed_bdt: number;
  common_patterns: string[];
  victim_count: number;
  is_known_offender: boolean;
  platform: string;
  recommended_action: string;
}

interface MerchantScamAlertBannerProps {
  merchantName?: string | null;
  locale: string;
}

export function MerchantScamAlertBanner({
  merchantName,
  locale,
}: MerchantScamAlertBannerProps) {
  const isBangla = locale === 'bn';
  const [intel, setIntel] = useState<MerchantIntelligenceData | null>(null);
  const [joinedGroup, setJoinedGroup] = useState(false);
  const [showClassActionModal, setShowClassActionModal] = useState(false);

  useEffect(() => {
    if (!merchantName) return;

    apiFetch(`/api/v1/merchants/intelligence?query=${encodeURIComponent(merchantName)}`)
      .then((res) => (res.ok ? res.json() : null))
      .then((data) => {
        if (data && data.complaint_count > 0) {
          setIntel(data);
        }
      })
      .catch(() => {});
  }, [merchantName]);

  if (!intel || intel.complaint_count === 0) return null;

  return (
    <div className="w-full rounded-2xl border-2 border-[var(--warning-ink)]/40 bg-gradient-to-br from-[var(--warning-soft)]/90 to-surface p-4 sm:p-5 shadow-xs mb-6 text-xs text-foreground">
      <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
        <div className="space-y-2 flex-1">
          <div className="flex flex-wrap items-center gap-2">
            <span className="p-1 rounded-md bg-[var(--warning-ink)] text-white flex items-center justify-center">
              <ShieldAlert className="w-4 h-4" />
            </span>
            <span className="font-bold text-sm text-[var(--warning-ink)] uppercase tracking-wide">
              {isBangla ? 'মার্চেন্ট ডিসপিউট ও ফ্রড রাডার সতর্কতা' : 'Merchant Scam Radar & Intelligence Alert'}
            </span>
            <Badge variant="danger" className="text-[10px]">
              {intel.risk_level}
            </Badge>
            <span className="font-mono text-[11px] text-muted-foreground font-semibold">
              {intel.complaint_count} {isBangla ? 'টি পূর্ববর্তী অভিযোগ' : 'Prior Complaints'}
            </span>
          </div>

          <p className="text-foreground leading-relaxed">
            {isBangla ? (
              <>
                <strong className="font-bold text-foreground">{intel.merchant_name}</strong>-এর বিরুদ্ধে ইতিপূর্বে{' '}
                <strong className="text-[var(--warning-ink)]">{intel.complaint_count}টি ভোক্তা বিরোধ</strong> নথিভুক্ত হয়েছে (সর্বমোট{' '}
                <strong className="text-foreground">৳{intel.total_disputed_bdt.toLocaleString('bn-BD')}</strong> টাকার দাবি তদন্তাধীন)।
              </>
            ) : (
              <>
                <strong className="font-bold text-foreground">{intel.merchant_name}</strong> has{' '}
                <strong className="text-[var(--warning-ink)]">{intel.complaint_count} prior consumer disputes</strong> on record (Total{' '}
                <strong className="text-foreground">৳{intel.total_disputed_bdt.toLocaleString('en-US')} BDT</strong> disputed).
              </>
            )}
          </p>

          {intel.common_patterns.length > 0 && (
            <div className="bg-surface/80 rounded-xl p-3 border border-border/60 space-y-1">
              <span className="text-[11px] font-bold text-muted-foreground uppercase tracking-wide block">
                {isBangla ? 'শনাক্তকৃত প্রতারণার ধরন (Common Patterns):' : 'Identified Grievance Patterns:'}
              </span>
              <ul className="list-disc list-inside text-muted-foreground space-y-0.5">
                {intel.common_patterns.slice(0, 2).map((pat, i) => (
                  <li key={i}>{pat}</li>
                ))}
              </ul>
            </div>
          )}
        </div>

        <div className="flex flex-col sm:items-end gap-2 shrink-0">
          <Link
            href={`/${locale}/merchants`}
            className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-surface border border-border font-semibold text-xs text-foreground hover:bg-elevated transition shadow-2xs"
          >
            <span>{isBangla ? 'মার্চেন্ট সতর্কতা রাডার দেখুন' : 'View Scam Radar'}</span>
            <ExternalLink className="w-3.5 h-3.5 text-muted-foreground" />
          </Link>

          {intel.victim_count > 0 && (
            <Button
              size="sm"
              variant={joinedGroup ? 'outline' : 'primary'}
              className="gap-1.5 text-xs font-bold"
              onClick={() => setShowClassActionModal(true)}
            >
              {joinedGroup ? (
                <>
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" />
                  <span>{isBangla ? 'যৌথ আবেদনে যুক্ত আছেন' : 'Joined Group Report'}</span>
                </>
              ) : (
                <>
                  <Users className="w-3.5 h-3.5" />
                  <span>
                    {isBangla
                      ? `যৌথ পদক্ষেপে যোগ দিন (${intel.victim_count} জন ভুক্তভোগী)`
                      : `Join Joint Action (${intel.victim_count} victims)`}
                  </span>
                </>
              )}
            </Button>
          )}
        </div>
      </div>

      {showClassActionModal && (
        <CollectiveClassActionModal
          isOpen={showClassActionModal}
          onClose={() => {
            setShowClassActionModal(false);
            setJoinedGroup(true);
          }}
          merchantName={intel.merchant_name}
          platform={intel.platform || 'Digital Marketplace'}
          complaintCount={intel.victim_count || intel.complaint_count || 12}
          totalDisputedBdt={intel.total_disputed_bdt || 48000}
          locale={locale}
        />
      )}
    </div>
  );
}
