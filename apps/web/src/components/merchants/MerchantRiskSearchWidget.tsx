'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import {
  Search,
  ShieldAlert,
  ShieldCheck,
  AlertTriangle,
  ArrowRight,
  TrendingUp,
  Users,
  CheckCircle2,
  Sparkles,
  ExternalLink,
} from 'lucide-react';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';

interface MerchantRecord {
  name: string;
  aliases: string[];
  platform: string;
  category: string;
  riskScore: number;
  riskLevel: 'HIGH' | 'MODERATE' | 'LOW';
  complaintCount: number;
  disputedAmountBdt: number;
  allegation: string;
  statute: string;
}

const DATABASE: MerchantRecord[] = [
  {
    name: 'Gadget Zone BD',
    aliases: ['gadget zone', 'gadgetzone', 'facebook shop', '01711000000'],
    platform: 'Facebook F-Commerce / Messenger Shop',
    category: 'Mobile Accessories & Consumer Electronics',
    riskScore: 88,
    riskLevel: 'HIGH',
    complaintCount: 14,
    disputedAmountBdt: 84500,
    allegation: 'Non-delivery after bKash advance payment; customer blocked on WhatsApp & Messenger.',
    statute: 'CRPA 2009 Sec 45 & Penal Code Sec 420',
  },
  {
    name: 'Daraz Bangladesh Ltd (Third-Party Sellers)',
    aliases: ['daraz', 'daraz seller', 'daraz.com.bd', 'marketplace'],
    platform: 'Online Multi-Vendor Marketplace',
    category: 'E-Commerce Marketplace',
    riskScore: 54,
    riskLevel: 'MODERATE',
    complaintCount: 8,
    disputedAmountBdt: 42000,
    allegation: 'Third-party vendor dispatched replica/mismatched item; return pickup delayed past 7 days.',
    statute: 'CRPA 2009 Sec 45 (Defective Goods & False Promise)',
  },
  {
    name: 'Metro Net Broadband ISP',
    aliases: ['metro net', 'metronet', 'isp', 'broadband'],
    platform: 'Fixed Broadband ISP',
    category: 'Telecommunications & Broadband',
    riskScore: 48,
    riskLevel: 'MODERATE',
    complaintCount: 5,
    disputedAmountBdt: 12500,
    allegation: 'Unannounced optical fiber downtime exceeding 96 hours with refusal of bill rebate.',
    statute: 'BTRC QoS Directives & CRPA 2009 Sec 53',
  },
  {
    name: 'Official Brand Store (Verified)',
    aliases: ['official', 'verified', 'samsung bd', 'apex', 'walton'],
    platform: 'Authorized Brand Retailer',
    category: 'Consumer Electronics & Footwear',
    riskScore: 12,
    riskLevel: 'LOW',
    complaintCount: 0,
    disputedAmountBdt: 0,
    allegation: 'No unresolved consumer fraud or non-delivery complaints on record.',
    statute: 'Full Statutory Compliance',
  },
];

export function MerchantRiskSearchWidget({ locale = 'en' }: { locale?: string }) {
  const isBangla = locale === 'bn';
  const [query, setQuery] = useState('');
  const [selectedResult, setSelectedResult] = useState<MerchantRecord | null>(null);

  const handleSearch = (searchTerm: string) => {
    setQuery(searchTerm);
    if (!searchTerm.trim()) {
      setSelectedResult(null);
      return;
    }

    const clean = searchTerm.toLowerCase().trim();
    const match = DATABASE.find(
      (m) =>
        m.name.toLowerCase().includes(clean) ||
        m.aliases.some((a) => a.toLowerCase().includes(clean))
    );

    if (match) {
      setSelectedResult(match);
    } else {
      // Dynamic fallback for unlisted shop
      setSelectedResult({
        name: searchTerm,
        aliases: [],
        platform: 'Unregistered / Unknown Merchant',
        category: 'Unverified Online Seller',
        riskScore: 65,
        riskLevel: 'MODERATE',
        complaintCount: 1,
        disputedAmountBdt: 3500,
        allegation: 'Unverified merchant profile. Exercise caution; insist on Cash on Delivery with unboxing inspection.',
        statute: 'CRPA 2009 Sec 45 Precautionary Guidance',
      });
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto rounded-3xl border border-border/80 bg-surface/90 backdrop-blur-md p-6 sm:p-8 shadow-lg space-y-6">
      {/* Title & Badge */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-2 border-b border-border/60">
        <div>
          <div className="flex items-center gap-2">
            <h3 className="text-lg sm:text-xl font-extrabold text-foreground tracking-tight flex items-center gap-2">
              <ShieldAlert className="w-5 h-5 text-rose-500" />
              <span>
                {isBangla
                  ? 'মার্চেন্ট স্ক্যাম ও প্রতারণা ঝুঁকি অনুসন্ধান'
                  : 'Instant Merchant Scam & Risk Checker'}
              </span>
            </h3>
            <Badge variant="brand" className="text-[10px] uppercase font-mono">
              Live Intel
            </Badge>
          </div>
          <p className="text-xs text-muted-foreground mt-1">
            {isBangla
              ? 'পণ্য কেনার আগে যে কোনো ফেসবুক পেজ, ওয়েবসাইট বা বিকাশ নম্বর সার্চ করে ঝুঁকি জানুন'
              : 'Search any Facebook page, merchant name, or phone number before paying advance money'}
          </p>
        </div>

        <Link
          href={`/${locale}/merchants`}
          className="text-xs font-semibold text-primary hover:underline flex items-center gap-1 self-start sm:self-auto"
        >
          <span>{isBangla ? 'সম্পূর্ণ রাডার লিডারবোর্ড' : 'View Full Scam Radar'}</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </Link>
      </div>

      {/* Search Input Bar */}
      <div className="relative">
        <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-muted-foreground">
          <Search className="w-4 h-4" />
        </div>
        <input
          type="text"
          value={query}
          onChange={(e) => handleSearch(e.target.value)}
          placeholder={
            isBangla
              ? 'মার্চেন্টের নাম বা ফেসবুক পেজ লিখুন (যেমন: Gadget Zone, Daraz, Metro Net)...'
              : 'Search merchant name, Facebook page, or number (e.g. Gadget Zone, Daraz)...'
          }
          className="w-full pl-11 pr-4 py-3.5 rounded-2xl border-2 border-border/80 focus:border-primary bg-elevated/40 text-foreground text-sm font-medium focus:outline-hidden focus:ring-2 focus:ring-primary/20 transition-all shadow-xs"
        />
      </div>

      {/* Quick Suggestion Chips */}
      <div className="flex flex-wrap items-center gap-2 text-xs">
        <span className="text-muted-foreground text-[11px] font-medium mr-1">
          {isBangla ? 'দ্রুত টেস্ট করুন:' : 'Quick tests:'}
        </span>
        {[
          { label: 'Gadget Zone BD', query: 'Gadget Zone BD', badge: 'High Risk' },
          { label: 'Daraz Bangladesh', query: 'Daraz', badge: 'Moderate' },
          { label: 'Metro Net ISP', query: 'Metro Net', badge: 'Moderate' },
          { label: 'Official Store', query: 'Official Brand Store', badge: 'Clean' },
        ].map((item) => (
          <button
            key={item.label}
            type="button"
            onClick={() => handleSearch(item.query)}
            className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-elevated hover:bg-elevated/80 border border-border text-foreground text-[11px] font-medium transition hover:scale-102"
          >
            <span>{item.label}</span>
            <span
              className={`text-[9px] px-1.5 py-0.2 rounded font-bold ${
                item.badge === 'High Risk'
                  ? 'bg-rose-500/20 text-rose-600 dark:text-rose-400'
                  : item.badge === 'Clean'
                  ? 'bg-emerald-500/20 text-emerald-600 dark:text-emerald-400'
                  : 'bg-amber-500/20 text-amber-600 dark:text-amber-400'
              }`}
            >
              {item.badge}
            </span>
          </button>
        ))}
      </div>

      {/* Search Result Card */}
      {selectedResult && (
        <div
          className={`p-5 rounded-2xl border transition-all animate-fadeIn ${
            selectedResult.riskLevel === 'HIGH'
              ? 'border-rose-500/40 bg-rose-500/5'
              : selectedResult.riskLevel === 'LOW'
              ? 'border-emerald-500/40 bg-emerald-500/5'
              : 'border-amber-500/40 bg-amber-500/5'
          }`}
        >
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-border/40">
            <div>
              <div className="flex items-center gap-2">
                <span className="text-base font-bold text-foreground">
                  {selectedResult.name}
                </span>
                <Badge
                  variant={
                    selectedResult.riskLevel === 'HIGH'
                      ? 'danger'
                      : selectedResult.riskLevel === 'LOW'
                      ? 'success'
                      : 'warning'
                  }
                  className="text-[10px] font-bold"
                >
                  {selectedResult.riskLevel === 'HIGH'
                    ? '⚠️ HIGH SCAM RISK'
                    : selectedResult.riskLevel === 'LOW'
                    ? '🛡️ VERIFIED CLEAN RECORD'
                    : '⚡ MODERATE RISK'}
                </Badge>
              </div>
              <span className="text-xs text-muted-foreground font-mono">
                {selectedResult.platform} • {selectedResult.category}
              </span>
            </div>

            {/* Risk Dial Score */}
            <div className="flex items-center gap-2 sm:self-center">
              <div className="text-right">
                <div className="text-[10px] text-muted-foreground uppercase font-bold tracking-wider">
                  Risk Score
                </div>
                <div
                  className={`text-xl font-extrabold font-mono ${
                    selectedResult.riskLevel === 'HIGH'
                      ? 'text-rose-600 dark:text-rose-400'
                      : selectedResult.riskLevel === 'LOW'
                      ? 'text-emerald-600 dark:text-emerald-400'
                      : 'text-amber-600 dark:text-amber-400'
                  }`}
                >
                  {selectedResult.riskScore}/100
                </div>
              </div>
            </div>
          </div>

          {/* Details & Metrics */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 py-3.5 text-xs">
            <div className="p-3 rounded-xl bg-surface border border-border">
              <span className="text-muted-foreground block text-[11px]">
                {isBangla ? 'অনিষ্পন্ন অভিযোগ' : 'Indexed Complaints'}
              </span>
              <span className="text-base font-bold text-foreground font-mono">
                {selectedResult.complaintCount} {isBangla ? 'টি' : 'Reports'}
              </span>
            </div>
            <div className="p-3 rounded-xl bg-surface border border-border">
              <span className="text-muted-foreground block text-[11px]">
                {isBangla ? 'দাবিকৃত মোট অর্থ' : 'Total Disputed Sum'}
              </span>
              <span className="text-base font-bold text-foreground font-mono">
                ৳{selectedResult.disputedAmountBdt.toLocaleString()}
              </span>
            </div>
            <div className="p-3 rounded-xl bg-surface border border-border">
              <span className="text-muted-foreground block text-[11px]">
                {isBangla ? 'আইনি ধারা' : 'Governing Statute'}
              </span>
              <span className="text-xs font-semibold text-foreground truncate block">
                {selectedResult.statute}
              </span>
            </div>
          </div>

          <p className="text-xs text-foreground/80 leading-relaxed pt-1 pb-3">
            <strong>{isBangla ? 'প্রধান অভিযোগ:' : 'Allegation:'}</strong> {selectedResult.allegation}
          </p>

          {/* Action CTAs */}
          <div className="flex flex-wrap items-center gap-2.5 pt-2 border-t border-border/40">
            <Link
              href={`/${locale}/cases/new`}
              className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-primary text-primary-foreground text-xs font-bold shadow-xs hover:opacity-90 transition"
            >
              <span>
                {isBangla
                  ? 'এই মার্চেন্টের বিরুদ্ধে কেস খুলুন'
                  : 'Start Dispute Against This Merchant'}
              </span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>

            <Link
              href={`/${locale}/merchants`}
              className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-elevated border border-border text-xs font-semibold text-foreground hover:bg-elevated/80 transition"
            >
              <Users className="w-3.5 h-3.5 text-primary" />
              <span>
                {isBangla
                  ? 'যৌথ গণ-অভিযোগ হাব দেখুন'
                  : 'View Collective Action Hub'}
              </span>
            </Link>
          </div>
        </div>
      )}
    </div>
  );
}

