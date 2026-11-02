'use client';

import React, { useState, useEffect, useMemo } from 'react';
import Link from 'next/link';
import {
  Plus,
  ArrowRight,
  FolderOpen,
  Search,
  Filter,
  Clock,
  AlertTriangle,
  CheckCircle2,
  DollarSign,
  Building2,
  Scale,
  FileText,
  ShieldAlert,
  PhoneCall,
  UserCheck,
  Edit3,
  Save,
  MessageSquare,
  Sparkles,
  ExternalLink,
  ChevronDown,
  ChevronUp,
  Receipt,
  TrendingUp,
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { DncrpOfficialFormModal, DncrpFormData } from '@/components/consumer/DncrpOfficialFormModal';
import { apiFetch } from '@/lib/api';
import { formatBdtMoney } from '@/lib/formatters';

export interface DashboardCase {
  id: string;
  title: string;
  display_reference: string;
  lifecycle_status: string;
  incident_date?: string | null;
  merchant_name?: string | null;
  story_narrative?: string | null;
  created_at: string;
  is_demo?: boolean;
}

interface UserProfile {
  full_name: string;
  phone: string;
  nid: string;
  address: string;
}

export function ConsumerDashboardClient({
  initialCases,
  locale,
}: {
  initialCases: DashboardCase[];
  locale: string;
}) {
  const isBangla = locale === 'bn';

  const [cases, setCases] = useState<DashboardCase[]>(initialCases);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<'all' | 'active' | 'resolved'>('all');
  const [showProfileDrawer, setShowProfileDrawer] = useState(false);
  const [profileSavedToast, setProfileSavedToast] = useState(false);

  // User Profile state
  const [userProfile, setUserProfile] = useState<UserProfile>({
    full_name: '',
    phone: '',
    nid: '',
    address: '',
  });

  // DNCRP Modal State
  const [selectedCaseForModal, setSelectedCaseForModal] = useState<DashboardCase | null>(null);

  // 1. Sync User Profile from LocalStorage
  useEffect(() => {
    if (typeof window !== 'undefined') {
      try {
        const saved = localStorage.getItem('claimcraft_user_profile');
        if (saved) {
          const parsed = JSON.parse(saved);
          setUserProfile({
            full_name: parsed.full_name || '',
            phone: parsed.phone || '',
            nid: parsed.nid || '',
            address: parsed.address || '',
          });
        }
      } catch (err) {
        console.error('Failed to load profile from storage:', err);
      }
    }
  }, []);

  // 2. Fetch fresh guest cases from API to merge with SSR cases
  useEffect(() => {
    async function refreshCases() {
      try {
        const res = await apiFetch('/api/v1/cases?limit=30');
        if (res.ok) {
          const data = await res.json();
          if (Array.isArray(data.items) && data.items.length > 0) {
            setCases((prev) => {
              const map = new Map<string, DashboardCase>();
              data.items.forEach((c: DashboardCase) => map.set(c.id, c));
              prev.forEach((c) => {
                if (!map.has(c.id)) map.set(c.id, c);
              });
              return Array.from(map.values());
            });
          }
        }
      } catch {
        // offline or guest session fallback
      }
    }
    refreshCases();
  }, []);

  // Save profile to localStorage
  const handleSaveProfile = (e: React.FormEvent) => {
    e.preventDefault();
    if (typeof window !== 'undefined') {
      try {
        localStorage.setItem('claimcraft_user_profile', JSON.stringify(userProfile));
        setProfileSavedToast(true);
        setTimeout(() => setProfileSavedToast(false), 3000);
      } catch (err) {
        console.error('Failed to save profile:', err);
      }
    }
  };

  // Helper: extract numeric amount from narrative or fallback
  const getDisputedAmount = (c: DashboardCase): number => {
    if (c.story_narrative) {
      const match =
        c.story_narrative.match(/(?:৳|BDT|টাকা)\s*([0-9,]+)/i) ||
        c.story_narrative.match(/([0-9,]+)\s*(?:৳|BDT|টাকা)/i);
      if (match) {
        const parsed = parseFloat(match[1].replace(/,/g, ''));
        if (!isNaN(parsed) && parsed > 0) return parsed;
      }
    }
    return 2500;
  };

  // Financial Recovery Scorecard Analytics
  const analytics = useMemo(() => {
    let totalDisputed = 0;
    let totalRecovered = 0;
    let activeDisputes = 0;

    cases.forEach((c) => {
      const amount = getDisputedAmount(c);
      totalDisputed += amount;
      const isResolved =
        c.lifecycle_status.toLowerCase().includes('settled') ||
        c.lifecycle_status.toLowerCase().includes('resolved') ||
        c.lifecycle_status.toLowerCase().includes('closed');

      if (isResolved) {
        totalRecovered += amount;
      } else {
        activeDisputes += 1;
      }
    });

    // 25% fine reward estimate (CRPA 2009 Section 76(1))
    // Standard DNCRP administrative fine typically ranges from 10k to 50k BDT
    const potentialGovtReward = Math.round(totalDisputed * 0.25);

    return {
      totalDisputed,
      totalRecovered,
      activeDisputes,
      potentialGovtReward,
    };
  }, [cases]);

  // Check for statutory 30-day deadline alerts
  const urgentWatchdogCases = useMemo(() => {
    return cases
      .map((c) => {
        const dateStr = c.incident_date || c.created_at;
        const incidentDate = new Date(dateStr);
        const now = new Date();
        const diffMs = now.getTime() - incidentDate.getTime();
        const daysPassed = Math.max(0, Math.floor(diffMs / (1000 * 60 * 60 * 24)));
        const daysRemaining = 30 - daysPassed;
        const isResolved =
          c.lifecycle_status.toLowerCase().includes('settled') ||
          c.lifecycle_status.toLowerCase().includes('resolved');

        return {
          caseItem: c,
          daysPassed,
          daysRemaining,
          isUrgent: !isResolved && daysRemaining <= 15,
        };
      })
      .filter((item) => item.isUrgent);
  }, [cases]);

  // Filtered cases
  const filteredCases = useMemo(() => {
    return cases.filter((c) => {
      const isResolved =
        c.lifecycle_status.toLowerCase().includes('settled') ||
        c.lifecycle_status.toLowerCase().includes('resolved');

      if (statusFilter === 'active' && isResolved) return false;
      if (statusFilter === 'resolved' && !isResolved) return false;

      if (!searchQuery.trim()) return true;

      const q = searchQuery.toLowerCase();
      const matchTitle = (c.title || '').toLowerCase().includes(q);
      const matchMerchant = (c.merchant_name || '').toLowerCase().includes(q);
      const matchRef = (c.display_reference || '').toLowerCase().includes(q);
      return matchTitle || matchMerchant || matchRef;
    });
  }, [cases, statusFilter, searchQuery]);

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* 1. Dashboard Hero Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-2 border-b border-border/80">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="p-1.5 rounded-lg bg-primary text-white shadow-2xs">
              <Scale className="w-5 h-5" />
            </span>
            <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-foreground">
              {isBangla ? 'ভোক্তা অধিকার সমাধান ড্যাশবোর্ড' : 'Consumer Resolution Dashboard'}
            </h1>
          </div>
          <p className="text-xs sm:text-sm text-muted-foreground">
            {isBangla
              ? 'আপনার আটকে থাকা টাকার হিসাব, আইনি সময়সীমা ও স্বয়ংক্রিয় প্রতিকার ব্যবস্থা'
              : 'Live financial recovery scorecard, statutory watchdog timers, and prepared legal actions.'}
          </p>
        </div>

        <div className="flex items-center gap-2.5">
          <Button
            size="sm"
            variant="outline"
            onClick={() => setShowProfileDrawer(!showProfileDrawer)}
            className="text-xs font-semibold gap-1.5 h-9"
          >
            <UserCheck className="w-3.5 h-3.5 text-primary" />
            <span>{isBangla ? 'ভোক্তা প্রোফাইল ও এনআইডি' : 'Profile & NID'}</span>
            {showProfileDrawer ? (
              <ChevronUp className="w-3.5 h-3.5" />
            ) : (
              <ChevronDown className="w-3.5 h-3.5" />
            )}
          </Button>

          <Link
            href={`/${locale}/cases/new`}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-[var(--radius-control)] bg-primary text-primary-foreground font-bold text-xs hover:opacity-90 shadow-xs transition"
          >
            <Plus className="w-4 h-4" />
            <span>{isBangla ? 'নতুন অভিযোগ দায়ের' : 'File New Dispute'}</span>
          </Link>
        </div>
      </div>

      {/* 2. Complainant Profile & NID Drawer (Collapsible) */}
      {showProfileDrawer && (
        <Card className="border-2 border-primary/40 bg-gradient-to-r from-primary/[0.04] via-surface to-elevated shadow-md animate-scaleUp">
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <UserCheck className="w-4 h-4 text-primary" />
                <CardTitle className="text-sm font-bold text-foreground">
                  {isBangla
                    ? 'আপনার স্থায়ী ভোক্তা তথ্য ও স্মার্ট এনআইডি ভল্ট'
                    : 'Personal Complainant Profile & NID Vault'}
                </CardTitle>
              </div>
              <Badge variant="brand" className="text-[10px]">
                {isBangla ? 'সকল আইনি ফরমে অটো-ফিল' : 'Auto-syncs to All Legal Petitions'}
              </Badge>
            </div>
            <CardDescription className="text-xs text-muted-foreground">
              {isBangla
                ? 'এখানে আপনার তথ্য একবার সংরক্ষণ করুন। ভোক্তা অধিকারের অফিশিয়াল ফরম, আইনি নোটিশ ও নথিতে স্বয়ংক্রিয়ভাবে আপনার নাম বসে যাবে।'
                : 'Save your profile credentials once. Every generated DNCRP petition, PDF dossier, and demand notice will auto-populate with your real info.'}
            </CardDescription>
          </CardHeader>
          <CardContent className="pt-2">
            <form onSubmit={handleSaveProfile} className="space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3 text-xs">
                <div>
                  <label className="text-[11px] font-bold text-foreground block mb-1">
                    {isBangla ? 'অভিযোগকারীর পুরো নাম *' : 'Full Name *'}
                  </label>
                  <input
                    type="text"
                    required
                    placeholder={isBangla ? 'যেমন: মোঃ রাশেদুল ইসলাম' : 'e.g. Md. Rashedul Islam'}
                    value={userProfile.full_name}
                    onChange={(e) =>
                      setUserProfile({ ...userProfile, full_name: e.target.value })
                    }
                    className="w-full p-2 rounded-lg border border-border bg-surface text-xs text-foreground focus:ring-1 focus:ring-primary"
                  />
                </div>
                <div>
                  <label className="text-[11px] font-bold text-foreground block mb-1">
                    {isBangla ? 'মোবাইল নম্বর (যোগাযোগ) *' : 'Phone Number *'}
                  </label>
                  <input
                    type="text"
                    required
                    placeholder="017XXXXXXXX"
                    value={userProfile.phone}
                    onChange={(e) => setUserProfile({ ...userProfile, phone: e.target.value })}
                    className="w-full p-2 rounded-lg border border-border bg-surface text-xs text-foreground focus:ring-1 focus:ring-primary"
                  />
                </div>
                <div>
                  <label className="text-[11px] font-bold text-foreground block mb-1">
                    {isBangla ? 'জাতীয় পরিচয়পত্র (NID নম্বর)' : 'National ID (NID No)'}
                  </label>
                  <input
                    type="text"
                    placeholder="1995XXXXXXXXXXXX"
                    value={userProfile.nid}
                    onChange={(e) => setUserProfile({ ...userProfile, nid: e.target.value })}
                    className="w-full p-2 rounded-lg border border-border bg-surface text-xs text-foreground focus:ring-1 focus:ring-primary"
                  />
                </div>
                <div>
                  <label className="text-[11px] font-bold text-foreground block mb-1">
                    {isBangla ? 'স্থায়ী / বর্তমান ঠিকানা' : 'Permanent Address'}
                  </label>
                  <input
                    type="text"
                    placeholder={isBangla ? 'বাড়ি, রোড, থানা, জেলা' : 'House, Road, Thana, District'}
                    value={userProfile.address}
                    onChange={(e) => setUserProfile({ ...userProfile, address: e.target.value })}
                    className="w-full p-2 rounded-lg border border-border bg-surface text-xs text-foreground focus:ring-1 focus:ring-primary"
                  />
                </div>
              </div>

              <div className="flex items-center justify-between pt-2">
                <span className="text-[11px] text-muted-foreground italic">
                  {userProfile.full_name
                    ? (isBangla ? `সক্রিয় ব্যবহারকারী: ${userProfile.full_name}` : `Active Complainant: ${userProfile.full_name}`)
                    : (isBangla ? 'প্রোফাইল পূরণ করা হয়নি' : 'Profile not set yet')}
                </span>

                <div className="flex items-center gap-2">
                  {profileSavedToast && (
                    <span className="text-xs font-bold text-emerald-600 dark:text-emerald-400 flex items-center gap-1">
                      <CheckCircle2 className="w-3.5 h-3.5" />
                      <span>{isBangla ? 'সফলভাবে সংরক্ষিত!' : 'Profile Saved!'}</span>
                    </span>
                  )}
                  <Button type="submit" size="sm" variant="primary" className="text-xs font-bold gap-1.5 h-8">
                    <Save className="w-3.5 h-3.5" />
                    <span>{isBangla ? 'তথ্য সংরক্ষণ করুন' : 'Save Profile'}</span>
                  </Button>
                </div>
              </div>
            </form>
          </CardContent>
        </Card>
      )}

      {/* 3. Financial Recovery Scorecard (4 Key KPIs) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* KPI 1: Total Disputed Money */}
        <Card className="border border-border/80 bg-surface shadow-xs hover:border-primary/40 transition">
          <CardContent className="p-4 flex items-center justify-between">
            <div>
              <p className="text-[11px] font-bold text-muted-foreground uppercase tracking-wider mb-1">
                {isBangla ? 'দাবিকৃত মোট টাকা' : 'Total Money at Stake'}
              </p>
              <h3 className="text-xl sm:text-2xl font-black text-foreground">
                ৳{analytics.totalDisputed.toLocaleString(isBangla ? 'bn-BD' : 'en-US')}
              </h3>
              <span className="text-[10px] text-muted-foreground mt-0.5 block">
                {isBangla ? `${cases.length}টি অভিযোগ অন্তর্ভুক্ত` : `Across ${cases.length} consumer claims`}
              </span>
            </div>
            <div className="p-3 rounded-xl bg-primary/10 text-primary border border-primary/20 shrink-0">
              <Receipt className="w-6 h-6" />
            </div>
          </CardContent>
        </Card>

        {/* KPI 2: Successfully Recovered */}
        <Card className="border border-border/80 bg-surface shadow-xs hover:border-emerald-500/40 transition">
          <CardContent className="p-4 flex items-center justify-between">
            <div>
              <p className="text-[11px] font-bold text-emerald-600 dark:text-emerald-400 uppercase tracking-wider mb-1">
                {isBangla ? 'পুনরুদ্ধারকৃত অর্থ' : 'Recovered Funds'}
              </p>
              <h3 className="text-xl sm:text-2xl font-black text-emerald-600 dark:text-emerald-400">
                ৳{analytics.totalRecovered.toLocaleString(isBangla ? 'bn-BD' : 'en-US')}
              </h3>
              <span className="text-[10px] text-muted-foreground mt-0.5 block">
                {isBangla ? 'রিফান্ড ও আপোষ মীমাংসা' : 'Direct refunds & settlements'}
              </span>
            </div>
            <div className="p-3 rounded-xl bg-emerald-500/10 text-emerald-500 border border-emerald-500/20 shrink-0">
              <CheckCircle2 className="w-6 h-6" />
            </div>
          </CardContent>
        </Card>

        {/* KPI 3: Active Ongoing Disputes */}
        <Card className="border border-border/80 bg-surface shadow-xs hover:border-amber-500/40 transition">
          <CardContent className="p-4 flex items-center justify-between">
            <div>
              <p className="text-[11px] font-bold text-amber-600 dark:text-amber-400 uppercase tracking-wider mb-1">
                {isBangla ? 'চলমান বিরোধ' : 'Active Disputes'}
              </p>
              <h3 className="text-xl sm:text-2xl font-black text-foreground">
                {analytics.activeDisputes.toLocaleString(isBangla ? 'bn-BD' : 'en-US')}
              </h3>
              <span className="text-[10px] text-muted-foreground mt-0.5 block">
                {isBangla ? 'আইনি প্রক্রিয়াধীন' : 'Awaiting merchant/portal action'}
              </span>
            </div>
            <div className="p-3 rounded-xl bg-amber-500/10 text-amber-500 border border-amber-500/20 shrink-0">
              <Clock className="w-6 h-6" />
            </div>
          </CardContent>
        </Card>

        {/* KPI 4: Section 76(1) Potential Bounty */}
        <Card className="border border-border/80 bg-surface shadow-xs hover:border-purple-500/40 transition">
          <CardContent className="p-4 flex items-center justify-between">
            <div>
              <p className="text-[11px] font-bold text-purple-600 dark:text-purple-400 uppercase tracking-wider mb-1">
                {isBangla ? '২৫% সরকারি প্রণোদনা' : '25% Fine Reward'}
              </p>
              <h3 className="text-xl sm:text-2xl font-black text-purple-600 dark:text-purple-400">
                ৳{analytics.potentialGovtReward.toLocaleString(isBangla ? 'bn-BD' : 'en-US')}
              </h3>
              <span className="text-[10px] text-muted-foreground mt-0.5 block">
                {isBangla ? 'ধারা ৭৬(১) আইনগত অধিকার' : 'Statutory CRPA Section 76(1)'}
              </span>
            </div>
            <div className="p-3 rounded-xl bg-purple-500/10 text-purple-500 border border-purple-500/20 shrink-0">
              <TrendingUp className="w-6 h-6" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* 4. Statutory 30-Day Watchdog Urgent Alert Center (If any case has <15 days remaining) */}
      {urgentWatchdogCases.length > 0 && (
        <div className="rounded-2xl border-2 border-amber-500/50 bg-gradient-to-r from-amber-500/15 via-surface to-elevated p-4 sm:p-5 shadow-sm space-y-3">
          <div className="flex items-center gap-2.5">
            <span className="p-2 rounded-lg bg-amber-500 text-slate-950 font-bold shrink-0">
              <AlertTriangle className="w-5 h-5 animate-bounce" />
            </span>
            <div>
              <h3 className="text-sm sm:text-base font-extrabold text-foreground flex items-center gap-2">
                <span>{isBangla ? 'ভোক্তা অধিকার সংরক্ষণ আইন ধারা ৬০ — জরুরি তামাদি সতর্কবার্তা' : 'CRPA 2009 Section 60 — Urgent Statutory Limitation Alert'}</span>
                <Badge variant="warning" className="text-[10px] animate-pulse">
                  {isBangla ? 'জরুরি পদক্ষেপ নিন' : 'Time Sensitive'}
                </Badge>
              </h3>
              <p className="text-xs text-muted-foreground mt-0.5">
                {isBangla
                  ? 'আইন অনুযায়ী ঘটনার ৩০ দিনের মধ্যে অভিযোগ দাখিল না করলে অধিকার তামাদি হয়ে যেতে পারে।'
                  : 'Under Bangladesh law, formal complaints must be lodged within 30 days of the incident to preserve legal remedies.'}
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-1">
            {urgentWatchdogCases.slice(0, 2).map(({ caseItem, daysRemaining }) => (
              <div
                key={caseItem.id}
                className="p-3 rounded-xl border border-border/80 bg-surface/90 flex items-center justify-between gap-3 text-xs"
              >
                <div>
                  <span className="font-bold text-foreground block truncate max-w-[220px]">
                    {caseItem.title}
                  </span>
                  <span className="text-[11px] text-amber-600 dark:text-amber-400 font-mono font-bold mt-0.5 block">
                    {isBangla
                      ? `⏳ আর মাত্র ${daysRemaining} দিন বাকি`
                      : `⏳ Only ${daysRemaining} days remaining`}
                  </span>
                </div>
                <div className="flex items-center gap-1.5 shrink-0">
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => setSelectedCaseForModal(caseItem)}
                    className="text-[11px] h-7 px-2 font-semibold"
                  >
                    <Building2 className="w-3 h-3 text-primary mr-1" />
                    <span>{isBangla ? 'অফিশিয়াল ফরম' : 'Official Form'}</span>
                  </Button>
                  <Link
                    href={`/${locale}/cases/${caseItem.id}`}
                    className="p-1.5 rounded-lg bg-primary text-white hover:opacity-90 transition"
                  >
                    <ArrowRight className="w-3.5 h-3.5" />
                  </Link>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 5. Filter & Search Controls */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
        {/* Status Filter Pills */}
        <div className="flex items-center gap-1 p-1 rounded-xl bg-elevated border border-border self-start">
          <button
            type="button"
            onClick={() => setStatusFilter('all')}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
              statusFilter === 'all'
                ? 'bg-surface text-foreground shadow-xs border border-border'
                : 'text-muted-foreground hover:text-foreground'
            }`}
          >
            {isBangla ? `সকল (${cases.length})` : `All (${cases.length})`}
          </button>
          <button
            type="button"
            onClick={() => setStatusFilter('active')}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
              statusFilter === 'active'
                ? 'bg-surface text-foreground shadow-xs border border-border'
                : 'text-muted-foreground hover:text-foreground'
            }`}
          >
            {isBangla ? `চলমান (${analytics.activeDisputes})` : `Active (${analytics.activeDisputes})`}
          </button>
          <button
            type="button"
            onClick={() => setStatusFilter('resolved')}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
              statusFilter === 'resolved'
                ? 'bg-surface text-foreground shadow-xs border border-border'
                : 'text-muted-foreground hover:text-foreground'
            }`}
          >
            {isBangla ? `মীমাংসিত (${cases.length - analytics.activeDisputes})` : `Resolved (${cases.length - analytics.activeDisputes})`}
          </button>
        </div>

        {/* Search Input */}
        <div className="relative w-full sm:w-72">
          <Search className="w-3.5 h-3.5 text-muted-foreground absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none" />
          <input
            type="text"
            placeholder={isBangla ? 'মার্চেন্ট বা শিরোনাম দিয়ে খুঁজুন...' : 'Search claims or merchants...'}
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-3 py-1.5 rounded-xl border border-border bg-surface text-xs text-foreground placeholder:text-muted-foreground focus:ring-1 focus:ring-primary"
          />
        </div>
      </div>

      {/* 6. Case Cards with 4-Stage Lifecycle Stepper */}
      <div className="space-y-4">
        {filteredCases.length === 0 ? (
          <div className="text-center p-12 border border-dashed border-border rounded-2xl bg-surface/50">
            <FolderOpen className="w-10 h-10 text-muted-foreground mx-auto mb-3 opacity-50" />
            <h3 className="text-sm font-bold text-foreground">
              {isBangla ? 'কোনো অভিযোগ খুঁজে পাওয়া যায়নি' : 'No cases found'}
            </h3>
            <p className="text-xs text-muted-foreground mt-1 max-w-sm mx-auto">
              {isBangla
                ? 'আপনার সার্চ ফিল্টারে কোনো রেকর্ড পাওয়া যায়নি অথবা এখনো কোনো বিরোধ দাখিল করা হয়নি।'
                : 'No dispute claims matched your active filters. Click below to file a new consumer complaint.'}
            </p>
            <Link
              href={`/${locale}/cases/new`}
              className="inline-flex items-center gap-1.5 px-4 py-2 mt-4 rounded-xl bg-primary text-white text-xs font-bold hover:opacity-90 transition"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>{isBangla ? 'প্রথম অভিযোগ দাখিল করুন' : 'File First Claim'}</span>
            </Link>
          </div>
        ) : (
          filteredCases.map((c) => {
            const amount = getDisputedAmount(c);
            const isSettled =
              c.lifecycle_status.toLowerCase().includes('settled') ||
              c.lifecycle_status.toLowerCase().includes('resolved');

            // Determine active step index: 1, 2, 3, or 4
            let stepIndex = 1;
            if (isSettled) {
              stepIndex = 4;
            } else if (c.lifecycle_status.toLowerCase().includes('action') || c.lifecycle_status.toLowerCase().includes('prepared')) {
              stepIndex = 3;
            } else if (c.lifecycle_status.toLowerCase().includes('fact') || c.lifecycle_status.toLowerCase().includes('assessed')) {
              stepIndex = 2;
            }

            return (
              <Card
                key={c.id}
                className="hover:border-primary/50 transition-all shadow-xs bg-surface overflow-hidden group"
              >
                <CardHeader className="pb-3 border-b border-border/60">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <span className="font-mono text-[11px] font-bold text-primary bg-primary/10 px-2 py-0.5 rounded-md">
                          {c.display_reference}
                        </span>
                        <Badge
                          variant={isSettled ? 'success' : 'brand'}
                          className="text-[10px] font-mono uppercase"
                        >
                          {c.lifecycle_status}
                        </Badge>
                        {c.is_demo && (
                          <Badge variant="neutral" className="text-[10px]">
                            DEMO
                          </Badge>
                        )}
                      </div>
                      <Link href={`/${locale}/cases/${c.id}`} className="block">
                        <CardTitle className="text-base font-bold text-foreground group-hover:text-primary transition-colors cursor-pointer">
                          {c.title}
                        </CardTitle>
                      </Link>
                    </div>

                    <div className="text-left sm:text-right shrink-0">
                      <span className="text-xs font-bold text-muted-foreground block">
                        {isBangla ? 'দাবিকৃত অর্থ:' : 'Disputed Sum:'}
                      </span>
                      <span className="text-base sm:text-lg font-black text-foreground">
                        ৳{amount.toLocaleString(isBangla ? 'bn-BD' : 'en-US')}
                      </span>
                    </div>
                  </div>
                </CardHeader>

                <CardContent className="pt-4 space-y-4">
                  {/* Visual 4-Stage Lifecycle Rail */}
                  <div className="p-3 rounded-xl bg-elevated/40 border border-border/80">
                    <div className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground mb-2 flex items-center justify-between">
                      <span>{isBangla ? 'বিরোধ নিষ্পত্তি অগ্রগতি (৪টি পর্যায়)' : 'Resolution Lifecycle Pipeline'}</span>
                      <span className="font-mono text-primary font-semibold">
                        {isBangla ? `ধাপ ${stepIndex}/৪` : `Step ${stepIndex}/4`}
                      </span>
                    </div>

                    <div className="grid grid-cols-4 gap-1.5 relative">
                      {/* Step 1: Evidence */}
                      <div className="space-y-1">
                        <div
                          className={`h-1.5 rounded-full ${
                            stepIndex >= 1 ? 'bg-primary' : 'bg-border'
                          }`}
                        />
                        <span
                          className={`text-[10px] block font-semibold truncate ${
                            stepIndex >= 1 ? 'text-foreground' : 'text-muted-foreground'
                          }`}
                        >
                          {isBangla ? '১. প্রমাণপত্র' : '1. Evidence'}
                        </span>
                      </div>

                      {/* Step 2: Notice */}
                      <div className="space-y-1">
                        <div
                          className={`h-1.5 rounded-full ${
                            stepIndex >= 2 ? 'bg-primary' : 'bg-border'
                          }`}
                        />
                        <span
                          className={`text-[10px] block font-semibold truncate ${
                            stepIndex >= 2 ? 'text-foreground' : 'text-muted-foreground'
                          }`}
                        >
                          {isBangla ? '২. লিগ্যাল নোটিশ' : '2. Legal Notice'}
                        </span>
                      </div>

                      {/* Step 3: DNCRP Docket */}
                      <div className="space-y-1">
                        <div
                          className={`h-1.5 rounded-full ${
                            stepIndex >= 3 ? 'bg-primary' : 'bg-border'
                          }`}
                        />
                        <span
                          className={`text-[10px] block font-semibold truncate ${
                            stepIndex >= 3 ? 'text-foreground' : 'text-muted-foreground'
                          }`}
                        >
                          {isBangla ? '৩. ভোক্তা অধিকার' : '3. DNCRP Form'}
                        </span>
                      </div>

                      {/* Step 4: Resolution */}
                      <div className="space-y-1">
                        <div
                          className={`h-1.5 rounded-full ${
                            stepIndex >= 4 ? 'bg-emerald-500' : 'bg-border'
                          }`}
                        />
                        <span
                          className={`text-[10px] block font-semibold truncate ${
                            stepIndex >= 4
                              ? 'text-emerald-600 dark:text-emerald-400 font-bold'
                              : 'text-muted-foreground'
                          }`}
                        >
                          {isBangla ? '৪. সমাধান' : '4. Resolved'}
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Merchant & Action Toolbar */}
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pt-1">
                    <div className="text-xs text-muted-foreground flex items-center gap-2">
                      <span className="font-semibold text-foreground">
                        {c.merchant_name || (isBangla ? 'অনির্দিষ্ট মার্চেন্ট' : 'Retail Merchant')}
                      </span>
                      <span>•</span>
                      <span>{new Date(c.created_at).toLocaleDateString(locale === 'bn' ? 'bn-BD' : 'en-US')}</span>
                    </div>

                    <div className="flex flex-wrap items-center gap-2">
                      {/* DNCRP 1-Click Modal Trigger */}
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => setSelectedCaseForModal(c)}
                        className="text-xs gap-1.5 h-8 font-semibold"
                      >
                        <Building2 className="w-3.5 h-3.5 text-primary" />
                        <span>{isBangla ? 'অফিশিয়াল ফরম' : 'DNCRP Form'}</span>
                      </Button>

                      {/* Notice Studio */}
                      <Link
                        href={`/${locale}/cases/${c.id}/actions`}
                        className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-border bg-surface hover:bg-elevated text-xs font-semibold text-foreground transition h-8"
                      >
                        <MessageSquare className="w-3.5 h-3.5 text-emerald-500" />
                        <span>{isBangla ? 'নোটিশ স্টুডিও' : 'Notice Studio'}</span>
                      </Link>

                      {/* View Case Details */}
                      <Link
                        href={`/${locale}/cases/${c.id}`}
                        className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg bg-primary text-primary-foreground text-xs font-bold hover:opacity-90 transition h-8 shadow-2xs"
                      >
                        <span>{isBangla ? 'কেস ভিউ' : 'View Claim'}</span>
                        <ArrowRight className="w-3.5 h-3.5" />
                      </Link>
                    </div>
                  </div>
                </CardContent>
              </Card>
            );
          })
        )}
      </div>

      {/* 7. Quick Resolution Toolkit & Emergency Helplines Hub */}
      <div className="rounded-2xl border border-border bg-elevated/40 p-5 space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <PhoneCall className="w-4 h-4 text-primary" />
            <h4 className="text-sm font-bold text-foreground">
              {isBangla ? 'ভোক্তা অধিকার দ্রুত সহায়তা ও টুলকিট' : 'Consumer Resolution Quick Tools'}
            </h4>
          </div>
          <Badge variant="neutral" className="text-[10px] font-mono">
            {isBangla ? '২৪/৭ নাগরিক সেবা' : 'Citizen Assistance'}
          </Badge>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 text-xs">
          {/* Hotline 16121 */}
          <a
            href="tel:16121"
            className="p-3 rounded-xl border border-border bg-surface hover:border-primary/40 transition flex items-center gap-3 group"
          >
            <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-600 shrink-0">
              <PhoneCall className="w-4 h-4" />
            </div>
            <div>
              <span className="font-bold text-foreground block group-hover:text-primary transition">
                16121
              </span>
              <span className="text-[11px] text-muted-foreground block">
                {isBangla ? 'ভোক্তা অধিকার হটলাইন' : 'DNCRP National Hotline'}
              </span>
            </div>
          </a>

          {/* Scam Radar */}
          <Link
            href={`/${locale}/merchants`}
            className="p-3 rounded-xl border border-border bg-surface hover:border-primary/40 transition flex items-center gap-3 group"
          >
            <div className="p-2 rounded-lg bg-red-500/10 text-red-600 shrink-0">
              <ShieldAlert className="w-4 h-4" />
            </div>
            <div>
              <span className="font-bold text-foreground block group-hover:text-primary transition">
                {isBangla ? 'মার্চেন্ট স্ক্যাম রাডার' : 'Merchant Scam Radar'}
              </span>
              <span className="text-[11px] text-muted-foreground block">
                {isBangla ? 'অনলাইন পেজ যাচাই' : 'Check scam reports'}
              </span>
            </div>
          </Link>

          {/* Laws of Bangladesh */}
          <a
            href="http://bdlaws.minlaw.gov.bd/act-1033.html"
            target="_blank"
            rel="noopener noreferrer"
            className="p-3 rounded-xl border border-border bg-surface hover:border-primary/40 transition flex items-center gap-3 group"
          >
            <div className="p-2 rounded-lg bg-blue-500/10 text-blue-600 shrink-0">
              <Scale className="w-4 h-4" />
            </div>
            <div>
              <span className="font-bold text-foreground block group-hover:text-primary transition">
                {isBangla ? 'আইন ২০০৯ গেজেট' : 'CRPA 2009 Statute'}
              </span>
              <span className="text-[11px] text-muted-foreground block">
                {isBangla ? 'বাংলাদেশ গেজেট পোর্টাল' : 'Ministry of Law Gazette'}
              </span>
            </div>
          </a>

          {/* New Claim Direct */}
          <Link
            href={`/${locale}/cases/new`}
            className="p-3 rounded-xl border border-primary/30 bg-primary/5 hover:bg-primary/10 transition flex items-center gap-3 group"
          >
            <div className="p-2 rounded-lg bg-primary text-white shrink-0">
              <Plus className="w-4 h-4" />
            </div>
            <div>
              <span className="font-bold text-primary block">
                {isBangla ? 'নতুন বিরোধ দাখিল' : 'Start New Dispute'}
              </span>
              <span className="text-[11px] text-muted-foreground block">
                {isBangla ? 'এআই কোপাইলট দিয়ে' : 'Guided by AI Copilot'}
              </span>
            </div>
          </Link>
        </div>
      </div>

      {/* 8. Dedicated DNCRP Schedule-1 Official Modal (Triggered by Any Card) */}
      {selectedCaseForModal && (
        <DncrpOfficialFormModal
          isOpen={!!selectedCaseForModal}
          onClose={() => setSelectedCaseForModal(null)}
          locale={locale}
          data={{
            complainantName:
              userProfile.full_name ||
              (isBangla ? 'সম্মানিত ভোক্তা (সম্পাদনা করুন)' : 'Disputed Consumer (Click Edit)'),
            complainantNid: userProfile.nid || '',
            complainantPhone: userProfile.phone || '',
            complainantAddress:
              userProfile.address ||
              (isBangla ? 'ঠিকানা অনির্ধারিত (সম্পাদনা করুন)' : 'Address not specified (Click Edit)'),
            merchantName:
              selectedCaseForModal.merchant_name || (isBangla ? 'অনির্দিষ্ট মার্চেন্ট' : 'Online Merchant'),
            merchantAddress: `${selectedCaseForModal.merchant_name || 'অনলাইন শপ'} (${isBangla ? 'অনলাইন ফেসবুক পেজ ও ই-কমার্স' : 'E-Commerce Platform'})`,
            merchantPhone: '01XXXXXXXXX',
            incidentDate:
              selectedCaseForModal.incident_date ||
              (isBangla ? 'অক্টোবর ২০২৬' : 'October 2026'),
            disputedAmountBdt: getDisputedAmount(selectedCaseForModal),
            productDescription:
              selectedCaseForModal.story_narrative ||
              (isBangla
                ? 'অনলাইনে পণ্য ক্রয়ের জন্য অগ্রিম টাকা পরিশোধের পর প্রতিশ্রুত পণ্য সরবরাহ করা হয়নি।'
                : 'Failure to deliver ordered goods after receiving advance payment.'),
            statutorySections: [
              isBangla
                ? 'ভোক্তা-অধিকার সংরক্ষণ আইন ২০০৯: ধারা ৪৫ (প্রতিশ্রুত পণ্য বা সেবা যথাযথভাবে বিক্রয় বা সরবরাহে ব্যর্থতা)'
                : 'Consumer Rights Protection Act 2009: Section 45 (Failure to deliver promised product)',
              isBangla
                ? 'ভোক্তা-অধিকার সংরক্ষণ আইন ২০০৯: ধারা ৪১ (মিথ্যা বা প্রতারণামূলক বিজ্ঞাপন বা অসদুপায়)'
                : 'Consumer Rights Protection Act 2009: Section 41 (Deceptive trade practice)',
              isBangla
                ? 'ভোক্তা-অধিকার সংরক্ষণ আইন ২০০৯: ধারা ৭৬(১) (আদায়কৃত জরিমানার ২৫% অংশ অভিযোগকারীকে নগদ প্রদান)'
                : 'Consumer Rights Protection Act 2009: Section 76(1) (Complainant right to 25% realized fine)',
            ],
            evidenceList: [
              isBangla
                ? `১. ডিজিটাল লেনদেন রসিদ ও এমএফএস স্টেটমেন্ট (${selectedCaseForModal.display_reference})`
                : `1. Digital payment statement & MFS transaction slip (${selectedCaseForModal.display_reference})`,
              isBangla
                ? '২. পণ্য অর্ডার সংক্রান্ত ডিজিটাল চালান ও কুরিয়ার ট্র্যাকিং নোট'
                : '2. Product order invoice & courier delivery tracking slip',
              isBangla
                ? '৩. বিক্রেতার সাথে চ্যাট ও যোগাযোগের প্রাসঙ্গিক স্ক্রিনশট'
                : '3. Relevant screenshots of communications with seller',
            ],
          }}
        />
      )}
    </div>
  );
}
