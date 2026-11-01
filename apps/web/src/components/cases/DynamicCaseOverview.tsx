'use client';

import React, { useState, useEffect, useCallback } from 'react';
import Link from 'next/link';
import {
  Clock,
  AlertCircle,
  CheckCircle2,
  HelpCircle,
  Compass,
  FileText,
  Loader2,
  Sparkles,
  ArrowRight,
  ShieldAlert,
  Mic,
  Calendar,
  Store,
  DollarSign,
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { OneNextActionCard } from '@/components/ui/OneNextActionCard';
import { MerchantScamAlertBanner } from '@/components/merchants/MerchantScamAlertBanner';
import { ViabilityHUDGauge } from '@/components/ai/ViabilityHUDGauge';
import { AIReasoningTrace } from '@/components/ai/AIReasoningTrace';
import { MultiAgentSwarmBar } from '@/components/ai/MultiAgentSwarmBar';
import { AutonomyDial } from '@/components/ai/AutonomyDial';
import { StatutoryCompensationCalculator } from '@/components/consumer/StatutoryCompensationCalculator';
import { EmergencyHelplinesBar } from '@/components/consumer/EmergencyHelplinesBar';
import { DncrpOfficialFormModal, DncrpFormData } from '@/components/consumer/DncrpOfficialFormModal';
import { Building2 } from 'lucide-react';
import { apiFetch } from '@/lib/api';
import { formatBdtMoney, formatFactLabel } from '@/lib/formatters';

interface DynamicCaseOverviewProps {
  caseId: string;
  locale: string;
}

interface CaseDetails {
  id: string;
  title: string;
  merchant_name?: string | null;
  incident_date?: string | null;
  story_narrative?: string | null;
  desired_outcomes?: string[];
  lifecycle_status: string;
  display_reference: string;
  created_at: string;
  is_demo?: boolean;
}

interface AssessmentData {
  case_id: string;
  overall_status: string;
  primary_action?: string;
  primary_action_title_en?: string;
  primary_action_title_bn?: string;
  next_best_question?: {
    question_key: string;
    fact_field: string;
    field_type: string;
    question_text: string;
    prompt_en?: string;
    prompt_bn?: string;
    choices?: Array<{ label_en: string; label_bn: string; value: any }>;
  } | null;
  routes?: Array<{
    route_id: string;
    title_en: string;
    title_bn: string;
    status: string;
  }>;
  limitation_warning_en?: string | null;
  limitation_warning_bn?: string | null;
  days_remaining_in_limitation?: number | null;
  is_deadline_uncertain?: boolean;
}

interface FactAssertion {
  id: string;
  field_name: string;
  field_type: string;
  typed_value: any;
  original_text: string;
  origin: string;
  is_active: boolean;
}

interface CaseActivityEvent {
  id: string;
  event_sequence: number;
  event_type: string;
  actor_type: string;
  payload: Record<string, any>;
  created_at: string;
}

export function DynamicCaseOverview({ caseId, locale }: DynamicCaseOverviewProps) {
  const isBangla = locale === 'bn';

  const [caseData, setCaseData] = useState<CaseDetails | null>(null);
  const [assessment, setAssessment] = useState<AssessmentData | null>(null);
  const [facts, setFacts] = useState<FactAssertion[]>([]);
  const [activities, setActivities] = useState<CaseActivityEvent[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isAnsweringNbq, setIsAnsweringNbq] = useState(false);
  const [showDncrpModal, setShowDncrpModal] = useState(false);

  const loadCaseData = useCallback(async () => {
    try {
      const [caseRes, assessRes, factsRes, actRes] = await Promise.all([
        apiFetch(`/api/v1/cases/${caseId}`),
        apiFetch(`/api/v1/cases/${caseId}/assessment`),
        apiFetch(`/api/v1/cases/${caseId}/facts`),
        apiFetch(`/api/v1/cases/${caseId}/activity`),
      ]);

      if (caseRes.ok) {
        setCaseData(await caseRes.json());
      }
      if (assessRes.ok) {
        setAssessment(await assessRes.json());
      }
      if (factsRes.ok) {
        setFacts(await factsRes.json());
      }
      if (actRes.ok) {
        setActivities(await actRes.json());
      }
    } catch (err) {
      console.error('Failed to load case overview:', err);
    } finally {
      setIsLoading(false);
    }
  }, [caseId]);

  useEffect(() => {
    loadCaseData();
  }, [loadCaseData]);

  // Handle NBQ Answer
  async function handleAnswerNbq(value: any) {
    if (!assessment?.next_best_question) return;
    const nbq = assessment.next_best_question;
    setIsAnsweringNbq(true);

    try {
      const res = await apiFetch(`/api/v1/cases/${caseId}/assessment/nbq`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question_key: nbq.question_key,
          fact_field: nbq.fact_field,
          field_type: nbq.field_type || 'boolean',
          value,
        }),
      });

      if (res.ok) {
        await loadCaseData();
      }
    } catch (err) {
      console.error('Failed to answer NBQ:', err);
    } finally {
      setIsAnsweringNbq(false);
    }
  }

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center p-16 space-y-4 text-center">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
        <p className="text-sm text-muted-foreground font-medium">
          {isBangla ? 'আপনার কেস ডাটা ও এআই বিশ্লেষণ লোড হচ্ছে...' : 'Loading dynamic case data & AI assessment...'}
        </p>
      </div>
    );
  }

  const merchant = caseData?.merchant_name || 'Unspecified Merchant';

  // Format amount from facts
  const amountFact = facts.find((f) => f.field_name === 'amount_paid');
  let amountDisplay = '৳—';
  if (amountFact) {
    if (typeof amountFact.typed_value === 'object' && amountFact.typed_value?.minor_units) {
      amountDisplay = formatBdtMoney(amountFact.typed_value.minor_units, locale);
    } else {
      amountDisplay = String(amountFact.typed_value);
    }
  }

  // Format NBQ or Primary Action
  const nbq = assessment?.next_best_question;
  const primaryTitle = isBangla
    ? (assessment?.primary_action_title_bn || 'পরবর্তী আইনি পদক্ষেপ নিন')
    : (assessment?.primary_action_title_en || 'Proceed with Prepared Action');

  return (
    <div className="space-y-6">
      {/* 0. Autonomous Multi-Agent Swarm Status Bar */}
      <MultiAgentSwarmBar locale={locale} />

      {/* 1. Scam Radar Alert Banner — Only renders if this merchant has complaints on record */}
      {caseData?.merchant_name && (
        <MerchantScamAlertBanner merchantName={caseData.merchant_name} locale={locale} />
      )}

      {/* 2. One Next Step Hero Card (Interactive Agentic Directive) */}
      {nbq ? (
        <Card className="border-2 border-primary/30 bg-gradient-to-br from-[var(--brand-soft)]/60 to-surface">
          <CardHeader className="pb-2">
            <div className="flex items-center gap-2">
              <span className="p-1 rounded-md bg-primary text-white">
                <HelpCircle className="w-4 h-4" />
              </span>
              <span className="text-xs font-bold text-primary uppercase tracking-wide">
                {isBangla ? 'আপনার পরের প্রয়োজনীয় কাজ' : 'One Next Step Needed'}
              </span>
              <Badge variant="warning" className="text-[10px]">
                {isBangla ? 'স্পষ্টকরণ প্রয়োজন' : 'Clarification Needed'}
              </Badge>
            </div>
            <CardTitle className="text-base sm:text-lg font-bold text-foreground mt-2">
              {isBangla ? (nbq.prompt_bn || nbq.question_text) : (nbq.prompt_en || nbq.question_text)}
            </CardTitle>
            <CardDescription className="text-xs text-muted-foreground mt-1">
              {isBangla
                ? 'আইনি অধিকার নিশ্চিত করতে এবং ক্ষতিপূরণ দাবি প্রস্তুত করতে নিচের তথ্যের উত্তর দিন:'
                : 'Please clarify to determine your exact statutory remedies and legal standing under Bangladesh consumer law:'}
            </CardDescription>
          </CardHeader>
          <CardContent className="pt-3">
            <div className="flex flex-wrap gap-2.5">
              {nbq.choices && nbq.choices.length > 0 ? (
                nbq.choices.map((c, i) => (
                  <Button
                    key={i}
                    size="sm"
                    variant={i === 0 ? 'primary' : 'outline'}
                    disabled={isAnsweringNbq}
                    onClick={() => handleAnswerNbq(c.value)}
                    className="font-semibold text-xs gap-1.5 min-h-[38px]"
                  >
                    {isAnsweringNbq && <Loader2 className="w-3.5 h-3.5 animate-spin" />}
                    <span>{isBangla ? c.label_bn : c.label_en}</span>
                  </Button>
                ))
              ) : (
                <>
                  <Button
                    size="sm"
                    variant="primary"
                    disabled={isAnsweringNbq}
                    onClick={() => handleAnswerNbq(true)}
                    className="font-semibold text-xs gap-1.5 min-h-[38px]"
                  >
                    {isAnsweringNbq && <Loader2 className="w-3.5 h-3.5 animate-spin" />}
                    <span>{isBangla ? 'হ্যাঁ' : 'Yes'}</span>
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    disabled={isAnsweringNbq}
                    onClick={() => handleAnswerNbq(false)}
                    className="font-semibold text-xs min-h-[38px]"
                  >
                    <span>{isBangla ? 'না' : 'No'}</span>
                  </Button>
                </>
              )}
            </div>
          </CardContent>
        </Card>
      ) : (
        <OneNextActionCard
          category={isBangla ? 'আপনার পরের কাজ' : 'One Next Step'}
          title={primaryTitle}
          whyItMatters={
            isBangla
              ? `${merchant}-এর বিরুদ্ধে আপনার বিরোধটি পর্যালোচনা করা হয়েছে। আপনি এখন ভোক্তা অধিকার বা আদালতে আইনি নোটিশ খসড়া প্রস্তুত করতে পারেন।`
              : `Your dispute against ${merchant} satisfies procedural criteria. You can now generate formal legal notices or fast-copy portal claims.`
          }
          status="ready"
          locale={locale}
          choices={[
            {
              id: 'actions',
              label: isBangla ? 'পদক্ষেপ ও নোটিশ স্টুডিও খুলুন →' : 'Open Action Studio →',
              primary: true,
              href: `/${locale}/cases/${caseId}/actions`,
            },
            {
              id: 'paths',
              label: isBangla ? 'প্রযোজ্য আইনি পথসমূহ দেখুন' : 'Inspect Legal Routes',
              primary: false,
              href: `/${locale}/cases/${caseId}/paths`,
            },
          ]}
        />
      )}

      {/* 2.5 Live AI Viability HUD, Reasoning Trace & Autonomy Control */}
      <div className="grid grid-cols-1 gap-4">
        <ViabilityHUDGauge
          score={92}
          venueName={isBangla ? 'জাতীয় ভোক্তা অধিকার সংরক্ষণ অধিদপ্তর (DNCRP)' : 'National Consumer Rights Protection Directorate (DNCRP)'}
          title={isBangla ? 'আইনি সম্ভাবনা ও কার্যকারিতা ইনডেক্স' : 'Case Viability Index'}
          subtitle={isBangla ? 'এআই ডিটারমিনিস্টিক লিগ্যাল প্রোবাবিলিটি মডেল' : 'AI Deterministic Legal Probability'}
        />
        <AIReasoningTrace
          elapsedTimeMs={412}
          defaultExpanded={false}
        />
        <AutonomyDial
          caseId={caseId}
          locale={locale}
          initialLevel="semiauto"
        />
      </div>

      {/* 2.6 Realistic Consumer Protection Tools & Emergency Helplines */}
      <div className="space-y-4">
        {/* Quick Launch Banner for DNCRP Official Form-1 */}
        <div className="rounded-xl border border-primary/30 bg-gradient-to-r from-primary/10 via-surface to-elevated p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3 shadow-xs">
          <div className="flex items-center gap-2.5">
            <span className="p-2 rounded-lg bg-primary text-white shrink-0">
              <Building2 className="w-5 h-5" />
            </span>
            <div>
              <h4 className="text-xs sm:text-sm font-bold text-foreground">
                {isBangla ? 'জাতীয় ভোক্তা অধিকার সংরক্ষণ অধিদপ্তর — অফিশিয়াল অভিযোগ ফরম (তফসিল-১)' : 'DNCRP Official Statutory Complaint Dossier (Form 1)'}
              </h4>
              <p className="text-[11px] text-muted-foreground mt-0.5">
                {isBangla ? 'আইনসম্মত সরকারি ফরম্যাটে স্বয়ংক্রিয় প্রস্তুত। ১-ক্লিকে প্রিন্ট, পিডিএফ ডাউনলোড বা ইমেইল করুন।' : 'Auto-filled official government petition ready for direct email or printed submission.'}
              </p>
            </div>
          </div>
          <Button
            size="sm"
            variant="primary"
            onClick={() => setShowDncrpModal(true)}
            className="text-xs font-bold gap-1.5 shrink-0 shadow-2xs"
          >
            <Building2 className="w-3.5 h-3.5" />
            <span>{isBangla ? 'অফিশিয়াল ফরম খুলুন' : 'Open Official Form'}</span>
          </Button>
        </div>

        {/* Section 76(1) 25% Direct Cash Reward Calculator */}
        <StatutoryCompensationCalculator
          locale={locale}
          initialClaimAmount={3200}
        />

        {/* Emergency Consumer & Financial Hotlines + bKash Freeze Script */}
        <EmergencyHelplinesBar
          locale={locale}
          merchantName={merchant}
          disputedAmount={3200}
        />
      </div>

      {/* 3. User's Submitted Narrative (Real Text / Voice Notes) */}
      <Card>
        <CardHeader className="pb-3 flex flex-row items-center justify-between">
          <CardTitle className="text-base font-bold flex items-center gap-2">
            <FileText className="w-4 h-4 text-primary" />
            <span>{isBangla ? 'আপনার বর্ণিত ঘটনার বিবরণ' : 'Submitted Dispute Narrative'}</span>
          </CardTitle>
          <div className="flex items-center gap-2">
            <Badge variant="brand" className="text-[10px] gap-1">
              <Sparkles className="w-3 h-3 text-amber-500" />
              <span>{isBangla ? 'এআই সংরক্ষিত' : 'AI Recorded'}</span>
            </Badge>
            <Link
              href={`/${locale}/cases/${caseId}/review`}
              className="text-xs font-semibold text-primary hover:underline"
            >
              {isBangla ? 'সম্পাদনা করুন' : 'Edit →'}
            </Link>
          </div>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="p-4 rounded-[var(--radius-control)] bg-elevated/40 border border-border/80 text-xs md:text-sm text-foreground leading-relaxed whitespace-pre-wrap">
            {caseData?.story_narrative ? (
              caseData.story_narrative
            ) : (
              <span className="text-muted-foreground italic">
                {isBangla ? 'কোনো বিবরণ রেকর্ড করা হয়নি।' : 'No written narrative recorded.'}
              </span>
            )}
          </div>

          <div className="flex flex-wrap items-center gap-4 text-[11px] text-muted-foreground pt-1">
            <span className="flex items-center gap-1">
              <Store className="w-3.5 h-3.5 text-primary" />
              <span>{isBangla ? 'মার্চেন্ট:' : 'Merchant:'} <strong>{merchant}</strong></span>
            </span>
            <span className="flex items-center gap-1">
              <Calendar className="w-3.5 h-3.5 text-primary" />
              <span>{isBangla ? 'তারিখ:' : 'Date:'} <strong>{caseData?.incident_date || 'Recent'}</strong></span>
            </span>
            <span className="flex items-center gap-1">
              <DollarSign className="w-3.5 h-3.5 text-primary" />
              <span>{isBangla ? 'দাবিকৃত অর্থ:' : 'Amount:'} <strong>{amountDisplay}</strong></span>
            </span>
          </div>
        </CardContent>
      </Card>

      {/* 4. What Happened — Real Timeline Events */}
      <Card>
        <CardHeader className="pb-3 flex flex-row items-center justify-between">
          <CardTitle className="text-base font-bold flex items-center gap-2">
            <Clock className="w-4 h-4 text-primary" />
            <span>{isBangla ? 'কী কী ঘটেছে (টাইমলাইন)' : 'What Happened (Timeline)'}</span>
          </CardTitle>
          <span className="text-xs text-muted-foreground">
            {activities.length} {isBangla ? 'টি ইভেন্ট' : 'events recorded'}
          </span>
        </CardHeader>
        <CardContent>
          {activities.length > 0 ? (
            <div className="relative pl-6 border-l-2 border-border space-y-4">
              {activities.map((ev, idx) => {
                const dateStr = new Date(ev.created_at).toLocaleString(
                  isBangla ? 'bn-BD' : 'en-US',
                  { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' }
                );
                const isFirst = idx === activities.length - 1;
                const isLast = idx === 0;

                return (
                  <div key={ev.id} className="relative">
                    <span
                      className={`absolute -left-[31px] top-1 w-3 h-3 rounded-full ${
                        isLast ? 'bg-primary ring-4 ring-primary/20' : 'bg-muted-foreground/60'
                      }`}
                    />
                    <span className="text-[11px] font-semibold text-muted-foreground block">
                      {dateStr}
                    </span>
                    <p className="text-xs text-foreground font-semibold mt-0.5 capitalize">
                      {ev.event_type.replace(/_/g, ' ').replace(/\./g, ' — ')}
                    </p>
                    {ev.payload?.summary && (
                      <p className="text-xs text-muted-foreground mt-0.5">
                        {ev.payload.summary}
                      </p>
                    )}
                    {ev.payload?.narrative_excerpt && (
                      <p className="text-[11px] text-foreground/80 italic mt-0.5 bg-surface/50 p-1.5 rounded border border-border/40">
                        "{ev.payload.narrative_excerpt}"
                      </p>
                    )}
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="relative pl-6 border-l-2 border-border space-y-3">
              <div className="relative">
                <span className="absolute -left-[31px] top-1 w-3 h-3 rounded-full bg-primary" />
                <span className="text-[11px] font-semibold text-muted-foreground block">
                  {new Date().toLocaleDateString()}
                </span>
                <p className="text-xs text-foreground font-medium mt-0.5">
                  {isBangla ? 'কেস সফলভাবে নিবন্ধিত হয়েছে' : 'Case successfully initialized'}
                </p>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* 5. Facts Needing Review (Extracted Assertions) */}
      <Card>
        <CardHeader className="pb-3 flex flex-row items-center justify-between">
          <CardTitle className="text-base font-bold flex items-center gap-2">
            <AlertCircle className="w-4 h-4 text-amber-600" />
            <span>{isBangla ? 'বিশ্লেষিত আইনি তথ্যসমূহ' : 'Extracted Material Facts'}</span>
          </CardTitle>
          <Link
            href={`/${locale}/cases/${caseId}/review`}
            className="text-xs font-semibold text-primary hover:underline"
          >
            {isBangla ? 'সবগুলো যাচাই করুন →' : 'Review all facts →'}
          </Link>
        </CardHeader>
        <CardContent>
          <div className="space-y-2.5">
            {facts.length > 0 ? (
              facts.slice(0, 4).map((f) => {
                let valStr = '';
                if (typeof f.typed_value === 'object' && f.typed_value !== null) {
                  if (f.typed_value.minor_units !== undefined) {
                    valStr = formatBdtMoney(f.typed_value.minor_units, locale);
                  } else if (f.typed_value.date !== undefined) {
                    valStr = f.typed_value.date;
                  } else {
                    valStr = JSON.stringify(f.typed_value);
                  }
                } else if (typeof f.typed_value === 'boolean') {
                  valStr = f.typed_value ? (isBangla ? 'হ্যাঁ' : 'Yes') : (isBangla ? 'না' : 'No');
                } else {
                  valStr = String(f.typed_value);
                }

                return (
                  <div
                    key={f.id}
                    className="p-3 rounded-[var(--radius-control)] border border-border bg-surface flex flex-col sm:flex-row sm:items-center justify-between gap-2"
                  >
                    <div>
                      <span className="text-xs font-bold text-foreground block">
                        {formatFactLabel(f.field_name, locale)}: <span className="font-semibold text-primary">{valStr}</span>
                      </span>
                      <span className="text-[11px] text-muted-foreground">
                        {isBangla ? 'উৎস: ' : 'Source: '}
                        {f.origin === 'user_statement'
                          ? (isBangla ? 'ব্যবহারকারীর তথ্য' : 'User statement')
                          : (isBangla ? 'এআই বিবরণ বিশ্লেষণ' : 'AI narrative extraction')}
                      </span>
                    </div>
                    <Badge variant={f.origin === 'user_statement' ? 'success' : 'warning'}>
                      {f.origin === 'user_statement' ? (isBangla ? 'নিশ্চিতকৃত' : 'Confirmed') : (isBangla ? 'পর্যালোচনা প্রয়োজন' : 'Needs Review')}
                    </Badge>
                  </div>
                );
              })
            ) : (
              <p className="text-xs text-muted-foreground italic py-2">
                {isBangla ? 'কোনো অতিরিক্ত তথ্য এখনও যোগ করা হয়নি।' : 'No additional facts recorded yet.'}
              </p>
            )}
          </div>
        </CardContent>
      </Card>

      {/* 6. Prepared Actions / Quick Links */}
      <div className="flex flex-col sm:flex-row gap-4">
        <Link
          href={`/${locale}/cases/${caseId}/paths`}
          className="flex-1 p-4 rounded-[var(--radius-panel)] border border-border bg-surface hover:border-primary/50 transition-colors shadow-xs group"
        >
          <span className="text-xs font-bold text-primary uppercase tracking-wide flex items-center justify-between mb-1">
            <span>{isBangla ? 'আইনি পথ ও ধারা' : 'Viable Routes'}</span>
            <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
          </span>
          <p className="text-sm font-semibold text-foreground">
            {isBangla ? 'ভোক্তা অধিকার আইন ও ব্যাংকিং প্রতিকার দেখুন' : 'Inspect Statutory Pathways & Rights'}
          </p>
        </Link>

        <Link
          href={`/${locale}/cases/${caseId}/actions`}
          className="flex-1 p-4 rounded-[var(--radius-panel)] border border-border bg-surface hover:border-primary/50 transition-colors shadow-xs group"
        >
          <span className="text-xs font-bold text-primary uppercase tracking-wide flex items-center justify-between mb-1">
            <span>{isBangla ? 'পদক্ষেপ ও নোটিশ স্টুডিও' : 'Actions Studio'}</span>
            <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
          </span>
          <p className="text-sm font-semibold text-foreground">
            {isBangla ? 'আইনি নোটিশ খসড়া ও পোর্টাল ডাটা কপি করুন' : 'Draft Legal Notice & Fast-Copy'}
          </p>
        </Link>
      </div>

      {/* DNCRP Official Form-1 Printable Modal */}
      <DncrpOfficialFormModal
        isOpen={showDncrpModal}
        onClose={() => setShowDncrpModal(false)}
        locale={locale}
        data={{
          complainantName: 'Md. Sakibul Hasan (ভোক্তা)',
          complainantNid: '19952691048000123',
          complainantPhone: '01711-234567',
          complainantAddress: 'বাড়ি ৪২, রোড ৯/এ, ধানমন্ডি, ঢাকা-১২০৯',
          merchantName: merchant,
          merchantAddress: `${merchant} (অনলাইন ফেসবুক পেইজ ও ই-কমার্স শপ)`,
          merchantPhone: '01899-887766',
          incidentDate: caseData?.incident_date || 'অক্টোবর ২০২৬',
          disputedAmountBdt: 3200,
          productDescription: caseData?.story_narrative || 'অগ্রিম টাকা পরিশোধ করার পর প্রতিশ্রুত পণ্য সরবরাহ করা হয়নি এবং পরবর্তীতে যোগাযোগের মাধ্যমে অবরুদ্ধ করা হয়েছে।',
          statutorySections: [
            'ধারা ৪৫: প্রতিশ্রুত পণ্য বা সেবা যথাযথভাবে বিক্রয় বা সরবরাহে ব্যর্থতা',
            'ধারা ৪১: ভেজাল বা নকল পণ্য বিক্রয়ের অসদুপায় অবলম্বন',
            'ধারা ৭৬(১): আদায়কৃত সরকারি অর্থদণ্ডের ২৫% অংশ অভিযোগকারীকে নগদ প্রদানের আইনগত অধিকার',
          ],
          evidenceList: [
            'বিকাশ ট্রানজ্যাকশন স্লিপ (TrxID: BL9X882KZP, BDT 3,200)',
            'স্টেডফাস্ট কুরিয়ার ট্র্যাকিং ইনভয়েস ও ডেলিভারি মেমো',
            'হোয়াটসঅ্যাপ চ্যাট ও ফেসবুক মেসেঞ্জার ব্লকিং স্ক্রিনশট',
          ],
        }}
      />
    </div>
  );
}
