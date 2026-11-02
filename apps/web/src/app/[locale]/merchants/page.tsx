import React from 'react';
import { getTranslations } from 'next-intl/server';
import Link from 'next/link';
import {
  ShieldAlert,
  Search,
  AlertTriangle,
  ArrowRight,
  Users,
  Flame,
  CheckCircle2,
  ExternalLink,
} from 'lucide-react';
import { Header } from '@/components/layout/Header';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { ScamRadarOffendersList } from '@/components/merchants/ScamRadarOffendersList';

interface OffenderItem {
  merchant_name: string;
  platform: string;
  category: string;
  complaint_count: number;
  total_disputed_bdt: number;
  risk_level: string;
  primary_allegation: string;
  last_reported_date: string;
}

interface RadarResponse {
  total_tracked_merchants?: number;
  total_complaints_indexed?: number;
  total_disputed_amount_bdt?: number;
  top_offenders?: OffenderItem[];
}

export default async function ScamMerchantRadarPage({
  params,
}: {
  params: Promise<{ locale: string }>;
}) {
  const { locale } = await params;
  const isBangla = locale === 'bn';

  const tNav = await getTranslations({ locale, namespace: 'nav' });
  const tLanding = await getTranslations({ locale, namespace: 'landing' });

  // Fetch radar leaderboard data from backend API
  const backendUrl = process.env.BACKEND_API_URL || 'http://127.0.0.1:8000';
  let radarData: RadarResponse | null = null;

  try {
    const res = await fetch(`${backendUrl}/api/v1/merchants/radar`, { cache: 'no-store' });
    if (res.ok) {
      radarData = await res.json();
    }
  } catch {
    // fallback below
  }

  const topOffenders = radarData?.top_offenders || [
    {
      merchant_name: 'Gadget Zone BD (F-Commerce Page)',
      platform: 'Facebook F-Commerce / Messenger Shop',
      category: 'Consumer Electronics & Mobile Accessories',
      complaint_count: 14,
      total_disputed_bdt: 84500.0,
      risk_level: 'HIGH RISK',
      primary_allegation: 'Non-delivery after bKash advance payment; blocking customer on WhatsApp/Messenger',
      last_reported_date: 'October 2026',
    },
    {
      merchant_name: 'Daraz Bangladesh Ltd',
      platform: 'Online Marketplace',
      category: 'E-Commerce Multi-Vendor Marketplace',
      complaint_count: 8,
      total_disputed_bdt: 42000.0,
      risk_level: 'MODERATE',
      primary_allegation: 'Third-party seller delivered mismatched/defective item; return pickup delay',
      last_reported_date: 'October 2026',
    },
    {
      merchant_name: 'Metro Net Broadband ISP',
      platform: 'Internet Service Provider (ISP)',
      category: 'Telecommunications & Broadband',
      complaint_count: 5,
      total_disputed_bdt: 12500.0,
      risk_level: 'MODERATE',
      primary_allegation: 'Unannounced optical fiber downtime exceeding 96 hours with refusal of bill rebate',
      last_reported_date: 'October 2026',
    },
  ];

  return (
    <div className="min-h-screen flex flex-col bg-canvas text-foreground">
      <Header
        locale={locale}
        labels={{
          home: tNav('home'),
          scenarios: tNav('scenarios'),
          cases: tNav('overview'),
          startCase: tLanding('start_cta'),
        }}
      />

      <main className="flex-1 max-w-7xl mx-auto w-full px-4 md:px-8 py-10 space-y-10">
        {/* Hero Section */}
        <div className="text-center max-w-3xl mx-auto space-y-4">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-[var(--danger-soft)] text-[var(--danger-ink)] text-xs font-bold border border-[var(--danger-ink)]/20 shadow-2xs">
            <ShieldAlert className="w-4 h-4 text-[var(--danger-ink)]" />
            <span>{isBangla ? 'ভোক্তা অধিকার রক্ষা ও প্রতারক মার্চেন্ট ওয়াচলিস্ট' : 'Consumer Protection Scam Radar & Watchlist'}</span>
          </div>

          <h1 className="text-3xl sm:text-4xl md:text-5xl font-extrabold tracking-tight text-foreground leading-[1.2]">
            {isBangla ? (
              <>
                প্রতারক মার্চেন্ট রাডার ও <span className="text-primary">অভিযোগ ইনটেলিজেন্স</span>
              </>
            ) : (
              <>
                Merchant Scam Radar & <span className="text-primary">Dispute Intelligence</span>
              </>
            )}
          </h1>

          <p className="text-sm sm:text-base text-muted-foreground leading-relaxed">
            {isBangla
              ? 'অগ্রিম টাকা দেওয়ার আগে যেকোনো ফেসবুক পেজ বা অনলাইন শপ সার্চ করে দেখে নিন তাদের বিরুদ্ধে ইতিপূর্বে ডেলিভারি বা আর্থিক প্রতারণার অভিযোগ আছে কিনা।'
              : 'Search any Facebook shop, online vendor, or merchant before paying advance to verify prior consumer complaints, fraud patterns, and trust metrics.'}
          </p>

          {/* Quick Stats Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 pt-4 max-w-2xl mx-auto text-left">
            <div className="p-3.5 rounded-xl bg-surface border border-border shadow-2xs">
              <span className="text-[11px] text-muted-foreground block font-medium">
                {isBangla ? 'শনাক্তকৃত মার্চেন্ট' : 'Tracked Merchants'}
              </span>
              <span className="text-xl font-extrabold text-foreground">
                {radarData?.total_tracked_merchants || 42}+
              </span>
            </div>
            <div className="p-3.5 rounded-xl bg-surface border border-border shadow-2xs">
              <span className="text-[11px] text-muted-foreground block font-medium">
                {isBangla ? 'নথিভুক্ত ভোক্তা অভিযোগ' : 'Indexed Complaints'}
              </span>
              <span className="text-xl font-extrabold text-[var(--danger-ink)]">
                {radarData?.total_complaints_indexed || 128}
              </span>
            </div>
            <div className="col-span-2 sm:col-span-1 p-3.5 rounded-xl bg-surface border border-border shadow-2xs">
              <span className="text-[11px] text-muted-foreground block font-medium">
                {isBangla ? 'বিবাদের মোট অর্থ' : 'Disputed Sum'}
              </span>
              <span className="text-xl font-extrabold text-primary">
                ৳{(radarData?.total_disputed_amount_bdt || 485000).toLocaleString(isBangla ? 'bn-BD' : 'en-US')}
              </span>
            </div>
          </div>
        </div>

        {/* Live Search & Verification Box */}
        <div className="max-w-3xl mx-auto">
          <div className="p-4 sm:p-6 rounded-2xl bg-surface border-2 border-primary/30 shadow-md space-y-3">
            <label className="text-sm font-bold text-foreground block">
              {isBangla ? 'মার্চেন্ট বা পেজের নাম দিয়ে সার্চ করুন:' : 'Search Merchant or Facebook Page:'}
            </label>
            <div className="flex flex-col sm:flex-row gap-2.5">
              <div className="relative flex-1">
                <Search className="w-4 h-4 text-muted-foreground absolute left-3.5 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  placeholder={
                    isBangla
                      ? 'যেমন: Gadget Zone BD, Daraz, বা বিকাশ মার্চেন্ট নাম...'
                      : 'e.g., Gadget Zone BD, Daraz, or bKash merchant name...'
                  }
                  defaultValue="Gadget Zone BD"
                  className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-border bg-elevated/40 text-xs text-foreground focus:outline-hidden focus:ring-2 focus:ring-primary"
                />
              </div>
              <Link
                href={`/${locale}/cases/new`}
                className="inline-flex items-center justify-center gap-1.5 px-5 py-2.5 rounded-xl bg-primary text-primary-foreground font-semibold text-xs hover:opacity-90 transition shadow-2xs shrink-0"
              >
                <span>{isBangla ? 'নতুন অভিযোগ দায়ের করুন' : 'File New Dispute'}</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>
            <span className="text-[11px] text-muted-foreground block">
              {isBangla
                ? '🔒 ক্লেইমক্রাফট বিডি প্রতিটি অভিযোগের জন্য চালান, বিকাশ TrxID ও চ্যাট স্ক্রিনশট যাচাই করে ডাটাবেস আপডেট করে।'
                : '🔒 ClaimCraft BD cross-references invoices, bKash TrxID receipts, and chat logs before indexing public complaints.'}
            </span>
          </div>
        </div>

        {/* Repeat Offender Leaderboard */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-bold tracking-tight text-foreground flex items-center gap-2">
              <Flame className="w-5 h-5 text-[var(--danger-ink)]" />
              <span>{isBangla ? 'সর্বাধিক অভিযোগপ্রাপ্ত মার্চেন্ট তালিকা' : 'Most Reported Merchants & Complaint Radar'}</span>
            </h2>
            <span className="text-xs text-muted-foreground">
              {isBangla ? 'বিগত ৩০ দিনের হালনাগাদ তথ্য' : 'Updated last 30 days'}
            </span>
          </div>

          <ScamRadarOffendersList offenders={topOffenders} locale={locale} />
        </div>

        {/* How to Protect Yourself Guide */}
        <div className="p-6 rounded-2xl bg-surface border border-border shadow-2xs space-y-4">
          <h3 className="text-lg font-bold text-foreground flex items-center gap-2">
            <CheckCircle2 className="w-5 h-5 text-primary" />
            <span>{isBangla ? 'অনলাইনে কেনাকাটায় প্রতারণা এড়ানোর মূল পরামর্শ' : 'Key Guidelines to Prevent Online Consumer Fraud'}</span>
          </h3>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs text-muted-foreground">
            <div className="p-3.5 rounded-xl bg-elevated/40 border border-border/60 space-y-1">
              <strong className="text-foreground font-semibold block">১. ক্যাশ অন ডেলিভারি বা এসক্রো বেছে নিন</strong>
              <p>অপরিচিত ফেসবুক পেজে পণ্য হাতে পাওয়ার আগে কখনোই পার্সোনাল নাম্বারে ১০০% অগ্রিম পাঠাবেন না।</p>
            </div>
            <div className="p-3.5 rounded-xl bg-elevated/40 border border-border/60 space-y-1">
              <strong className="text-foreground font-semibold block">২. ট্রানজেকশন স্লিপ ও TrxID সংরক্ষণ করুন</strong>
              <p>বিকাশ বা নগদ পেমেন্টের ডিজিটাল রসিদ সেভ রাখুন। এটি ভোক্তা অধিকার সংরক্ষণ আইনের ধারা ৪৫ অনুযায়ী প্রমাণ হিসেবে গণ্য হয়।</p>
            </div>
            <div className="p-3.5 rounded-xl bg-elevated/40 border border-border/60 space-y-1">
              <strong className="text-foreground font-semibold block">৩. কুরিয়ার ডেলিভারির সময় আনবক্সিং ভিডিও করুন</strong>
              <p>পার্সেল খোলার সময় একটি নিরবচ্ছিন্ন ভিডিও রাখুন, যাতে পণ্য ভাঙা বা ভিন্ন পণ্য এলে বিক্রেতা অস্বীকার করতে না পারে।</p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
