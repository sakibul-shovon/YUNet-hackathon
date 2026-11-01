'use client';

import React, { useState, useEffect, useCallback } from 'react';
import Link from 'next/link';
import {
  Sparkles,
  Cpu,
  CheckCircle2,
  XCircle,
  HelpCircle,
  AlertTriangle,
  ArrowRight,
  ShieldAlert,
  ChevronDown,
  ChevronUp,
  Scale,
  ExternalLink,
} from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { WhatIfDrawer } from '@/components/paths/WhatIfDrawer';
import { ProcessingDetailsDrawer } from '@/components/cases/ProcessingDetailsDrawer';
import { apiFetch } from '@/lib/api';

interface ConditionTraceItem {
  node_type: string;
  fact: string | null;
  inspected_value: unknown;
  outcome: 'TRUE' | 'FALSE' | 'UNKNOWN';
  details: string | null;
}

interface RouteItem {
  route_id: string;
  rule_id: string;
  issue_type: string;
  status: 'supported' | 'needs_facts' | 'excluded' | 'not_supported' | 'source_caution';
  reasons: string[];
  allowed_actions: string[];
  source_dependencies: string[];
  statutory_citations: string[];
  supported_remedies: string[];
  unsupported_remedies: string[];
  unsupported_remedy_warnings: string[];
  condition_trace: ConditionTraceItem[];
}

interface NextBestQuestion {
  question_key: string;
  fact_field: string;
  prompt_en: string;
  prompt_bn: string;
  question_type: string;
  priority: string;
  relevance_rationale: string;
}

interface ProceduralAssessment {
  case_id: string;
  overall_status: string;
  primary_action: string;
  primary_action_title_en: string;
  primary_action_title_bn: string;
  secondary_actions: Array<{ action_id: string; title_en: string; title_bn: string }>;
  routes: RouteItem[];
  next_best_question: NextBestQuestion | null;
  limitation_warning_en: string | null;
  limitation_warning_bn: string | null;
  days_remaining_in_limitation: number | null;
  is_deadline_uncertain: boolean;
}

interface WhyWhyNotTraceViewProps {
  caseId: string;
  locale: string;
}

export function WhyWhyNotTraceView({ caseId, locale }: WhyWhyNotTraceViewProps) {
  const isBangla = locale === 'bn';

  const [assessment, setAssessment] = useState<ProceduralAssessment | null>(null);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Expanded trace drawers per route
  const [expandedRoutes, setExpandedRoutes] = useState<Record<string, boolean>>({});

  // Modals
  const [isWhatIfOpen, setIsWhatIfOpen] = useState(false);
  const [isProcessingOpen, setIsProcessingOpen] = useState(false);

  const fetchAssessment = useCallback(async () => {
    setLoading(true);
    setErrorMsg(null);
    try {
      const res = await apiFetch(`/api/v1/cases/${caseId}/assessment`);
      if (!res.ok) throw new Error('Failed to load procedural assessment.');
      const data = await res.json();
      setAssessment(data);
    } catch (err: unknown) {
      setErrorMsg(err instanceof Error ? err.message : 'Error fetching assessment');
    } finally {
      setLoading(false);
    }
  }, [caseId]);

  useEffect(() => {
    fetchAssessment();
  }, [fetchAssessment]);

  const toggleTrace = (routeId: string) => {
    setExpandedRoutes((prev) => ({ ...prev, [routeId]: !prev[routeId] }));
  };

  const handleAnswerNBQ = async (answerValue: boolean) => {
    if (!assessment?.next_best_question) return;
    try {
      const q = assessment.next_best_question;
      const res = await apiFetch(`/api/v1/cases/${caseId}/nbq/answer`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question_key: q.question_key,
          fact_field: q.fact_field,
          value: answerValue,
          field_type: 'boolean',
        }),
      });
      if (!res.ok) throw new Error('Failed to submit answer.');
      const updated = await res.json();
      setAssessment(updated);
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : 'Submission failed');
    }
  };

  const handleSkipNBQ = async () => {
    if (!assessment?.next_best_question) return;
    try {
      const q = assessment.next_best_question;
      const res = await apiFetch(`/api/v1/cases/${caseId}/nbq/skip`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question_key: q.question_key,
          fact_field: q.fact_field,
        }),
      });
      if (!res.ok) throw new Error('Failed to skip question.');
      const updated = await res.json();
      setAssessment(updated);
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : 'Skip failed');
    }
  };

  if (loading) {
    return (
      <div className="p-12 text-center text-xs text-muted-foreground animate-pulse space-y-2">
        <Scale className="w-8 h-8 text-primary mx-auto animate-bounce" />
        <p>{isBangla ? 'আইনি ও প্রক্রিয়াগত পথ মূল্যায়ন করা হচ্ছে...' : 'Evaluating statutory procedural pathways...'}</p>
      </div>
    );
  }

  if (errorMsg || !assessment) {
    return (
      <div className="p-6 rounded-xl border border-destructive/40 bg-destructive/10 text-destructive text-xs space-y-2">
        <div className="flex items-center gap-2 font-bold">
          <AlertTriangle className="w-4 h-4" />
          <span>{isBangla ? 'মূল্যায়ন লোড করা সম্ভব হয়নি' : 'Could not load assessment'}</span>
        </div>
        <p>{errorMsg}</p>
        <Button size="sm" variant="outline" onClick={fetchAssessment}>
          {isBangla ? 'পুনরায় চেষ্টা করুন' : 'Retry'}
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Top action row */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-foreground">
            {isBangla ? 'প্রযোজ্য আইনি ও প্রাতিষ্ঠানিক পথ' : 'Viable Procedural Paths'}
          </h2>
          <p className="text-xs text-muted-foreground mt-1">
            {isBangla
              ? 'সরকারি বিধিমালার ওপর ভিত্তি করে সর্বোচ্চ ৩টি কার্যকর পথ দেখানো হচ্ছে।'
              : 'Statutory routes evaluated against official regulations. Condition traces inspectable.'}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            className="gap-2 text-xs"
            onClick={() => setIsProcessingOpen(true)}
          >
            <Cpu className="w-4 h-4 text-primary" />
            <span>{isBangla ? 'প্রসেসিং প্রমাণ' : 'Processing Details'}</span>
          </Button>
          <Button
            variant="outline"
            size="sm"
            className="gap-2 text-xs border-primary text-primary hover:bg-[var(--brand-soft)]"
            onClick={() => setIsWhatIfOpen(true)}
          >
            <Sparkles className="w-4 h-4" />
            <span>{isBangla ? 'পরিস্থিতি সিমুলেশন (What-If)' : 'Simulate Changes (What-If)'}</span>
          </Button>
        </div>
      </div>

      {/* T30 Limitation Period Warning Banner */}
      {assessment.limitation_warning_en && (
        <div className="p-3.5 rounded-xl border border-[var(--warning-ink)]/30 bg-[var(--warning-soft)]/50 text-foreground text-xs flex items-start gap-2.5">
          <AlertTriangle className="w-4 h-4 text-[var(--warning-ink)] shrink-0 mt-0.5" />
          <div className="space-y-1">
            <span className="font-bold text-[var(--warning-ink)] block">
              {isBangla ? 'আইনি সময়সীমা সতর্কতা (ধারা ৬০):' : 'Statutory Limitation Warning (Section 60):'}
            </span>
            <p className="leading-relaxed">
              {isBangla ? assessment.limitation_warning_bn : assessment.limitation_warning_en}
            </p>
          </div>
        </div>
      )}

      {/* Next Best Question Card (NBQ with safety priority) */}
      {assessment.next_best_question && (
        <Card className="border-2 border-primary/40 bg-gradient-to-br from-surface to-elevated/40 shadow-xs">
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <Badge variant={assessment.next_best_question.priority === 'safety' ? 'danger' : 'brand'}>
                {assessment.next_best_question.priority === 'safety'
                  ? (isBangla ? 'জরুরি নিরাপত্তা প্রশ্ন' : 'Urgent Safety Question')
                  : (isBangla ? 'পরবর্তী স্পষ্টীকরণ প্রশ্ন' : 'Next Best Question')}
              </Badge>
              <span className="text-[11px] font-mono text-muted-foreground">
                Priority: {assessment.next_best_question.priority}
              </span>
            </div>
            <CardTitle className="text-base font-bold text-foreground mt-2">
              {isBangla ? assessment.next_best_question.prompt_bn : assessment.next_best_question.prompt_en}
            </CardTitle>
            <CardDescription className="text-xs">
              {assessment.next_best_question.relevance_rationale}
            </CardDescription>
          </CardHeader>
          <CardContent className="pt-0 flex flex-wrap items-center gap-3">
            <Button size="sm" variant="primary" onClick={() => handleAnswerNBQ(true)}>
              {isBangla ? 'হ্যাঁ (Yes)' : 'Yes'}
            </Button>
            <Button size="sm" variant="outline" onClick={() => handleAnswerNBQ(false)}>
              {isBangla ? 'না (No)' : 'No'}
            </Button>
            <button
              onClick={handleSkipNBQ}
              className="text-xs text-muted-foreground underline hover:text-foreground ml-auto"
            >
              {isBangla ? 'এখন এড়িয়ে যান (Skip)' : 'Skip for now'}
            </button>
          </CardContent>
        </Card>
      )}

      {/* Evaluated Routes List */}
      <div className="space-y-4">
        {assessment.routes.map((route, idx) => {
          const isExpanded = !!expandedRoutes[route.route_id];
          const isPrimary = idx === 0 && route.status === 'supported';

          return (
            <Card
              key={route.route_id}
              className={`transition-all ${
                isPrimary
                  ? 'border-2 border-primary/60 bg-gradient-to-br from-surface to-elevated/20 shadow-xs'
                  : 'border border-border bg-surface'
              }`}
            >
              <CardHeader className="pb-3">
                <div className="flex flex-wrap items-center justify-between gap-2 mb-1.5">
                  <div className="flex items-center gap-2">
                    <Badge
                      variant={
                        route.status === 'supported'
                          ? 'brand'
                          : route.status === 'needs_facts'
                          ? 'warning'
                          : route.status === 'excluded'
                          ? 'danger'
                          : 'neutral'
                      }
                    >
                      {route.status.toUpperCase()}
                    </Badge>
                    {isPrimary && (
                      <Badge variant="brand">
                        {isBangla ? 'সুপারিশকৃত পথ' : 'Recommended Route'}
                      </Badge>
                    )}
                  </div>
                  <span className="text-xs text-muted-foreground font-mono">{route.rule_id}</span>
                </div>

                <CardTitle className="text-lg font-bold text-foreground">
                  {route.issue_type === 'ecommerce_delivery_failure'
                    ? (isBangla ? 'ভোক্তা অধিকার সংরক্ষণ অধিদপ্তর (DNCRP) — ধারা ৪৫ ও ৭৬' : 'DNCRP CCMS: Non-Delivery Complaint (Sec 45 & 76)')
                    : route.issue_type === 'defective_goods'
                    ? (isBangla ? 'বিক্রেতার রিপ্লেসমেন্ট নোটিশ ও ভোক্তা অধিকার অভিযোগ' : 'Defective Goods Remedy: Merchant Notice & CCMS Complaint')
                    : route.issue_type === 'mfs_unauthorized_charge'
                    ? (isBangla ? 'বাংলাদেশ ব্যাংক সিআইপিসি ও এমএফএস প্রোভাইডার গ্রিভেন্স' : 'Financial Dispute: Provider Stage 1 Grievance & BB CIPC')
                    : route.issue_type === 'product_safety_hazard'
                    ? (isBangla ? 'জরুরি ভোক্তা অধিকার হটলাইন ১৬১২১ অ্যালার্ট' : 'Emergency Safety Alert: DNCRP Hotline 16121')
                    : route.issue_type}
                </CardTitle>

                {/* Statutory Citations Chips */}
                {route.statutory_citations.length > 0 && (
                  <div className="flex flex-wrap items-center gap-1.5 pt-1">
                    <span className="text-[11px] text-muted-foreground font-medium">
                      {isBangla ? 'আইনি ভিত্তি:' : 'Statutory Basis:'}
                    </span>
                    {route.statutory_citations.map((c) => (
                      <Link
                        key={c}
                        href={`/${locale}/sources`}
                        className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-mono bg-elevated border border-border/80 text-primary hover:underline"
                      >
                        <Scale className="w-3 h-3" />
                        <span>{c}</span>
                        <ExternalLink className="w-2.5 h-2.5 opacity-60" />
                      </Link>
                    ))}
                  </div>
                )}
              </CardHeader>

              <CardContent className="space-y-3 text-xs">
                {/* Unsupported remedy warnings */}
                {route.unsupported_remedy_warnings.length > 0 && (
                  <div className="p-3 rounded-lg bg-[var(--danger-soft)] text-[var(--danger-ink)] border border-[var(--danger-ink)]/20 space-y-1">
                    <span className="font-bold block flex items-center gap-1.5">
                      <ShieldAlert className="w-4 h-4 shrink-0" />
                      <span>{isBangla ? 'অসমর্থিত প্রতিকার দাবি:' : 'Unsupported Remedy Warning:'}</span>
                    </span>
                    <p className="leading-relaxed">{route.unsupported_remedy_warnings[0]}</p>
                  </div>
                )}

                {/* Reasons list */}
                <div className="p-3 rounded-lg bg-elevated/40 border border-border/60 space-y-1">
                  <span className="font-semibold text-foreground block">
                    {route.status === 'supported'
                      ? (isBangla ? 'কেন এই পথ প্রযোজ্য:' : 'Why this route applies:')
                      : (isBangla ? 'বর্তমান পথের স্থিতি:' : 'Current route status:')}
                  </span>
                  <ul className="list-disc list-inside text-muted-foreground space-y-0.5">
                    {route.reasons.map((r, i) => (
                      <li key={i}>{r}</li>
                    ))}
                  </ul>
                </div>

                {/* Expandable Condition Trace */}
                <div className="pt-1">
                  <button
                    onClick={() => toggleTrace(route.route_id)}
                    className="flex items-center gap-1.5 text-xs font-semibold text-primary hover:underline"
                  >
                    <span>
                      {isExpanded
                        ? (isBangla ? 'শর্তসমূহের ট্রেস লুকান' : 'Hide Condition Trace')
                        : (isBangla ? 'শর্তসমূহের বিস্তারিত ট্রেস দেখুন (Why / Why-Not)' : 'Inspect Condition Trace (Why / Why-Not)')}
                    </span>
                    {isExpanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                  </button>

                  {isExpanded && (
                    <div className="mt-3 p-3 rounded-xl border border-border bg-background space-y-2 text-xs">
                      <div className="font-bold text-foreground text-[11px] uppercase tracking-wider text-muted-foreground">
                        {isBangla ? 'ক্লিনি ৩-মান যুক্ত লজিক ট্রেস (Kleene 3-Valued Trace):' : 'Kleene 3-Valued Evaluation Trace:'}
                      </div>
                      <div className="space-y-1.5 divide-y divide-border/40">
                        {route.condition_trace.map((item, cIdx) => (
                          <div key={cIdx} className="pt-1.5 first:pt-0 flex items-start justify-between gap-2">
                            <div className="flex items-start gap-2">
                              {item.outcome === 'TRUE' ? (
                                <CheckCircle2 className="w-4 h-4 text-primary shrink-0 mt-0.5" />
                              ) : item.outcome === 'FALSE' ? (
                                <XCircle className="w-4 h-4 text-destructive shrink-0 mt-0.5" />
                              ) : (
                                <HelpCircle className="w-4 h-4 text-[var(--warning-ink)] shrink-0 mt-0.5" />
                              )}
                              <div>
                                <span className="font-mono text-foreground font-semibold">{item.fact || item.node_type}</span>
                                {item.details && (
                                  <span className="text-muted-foreground ml-1.5 text-[11px]">({item.details})</span>
                                )}
                                <div className="text-[11px] text-muted-foreground font-mono">
                                  Inspected: {item.inspected_value === null ? 'null (unknown)' : String(item.inspected_value)}
                                </div>
                              </div>
                            </div>
                            <Badge
                              variant={
                                item.outcome === 'TRUE'
                                  ? 'brand'
                                  : item.outcome === 'FALSE'
                                  ? 'danger'
                                  : 'warning'
                              }
                            >
                              {item.outcome}
                            </Badge>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>

                {/* Action button */}
                <div className="pt-2">
                  <Link
                    href={`/${locale}/cases/${caseId}/actions`}
                    className="inline-flex items-center gap-2 px-4 py-2 rounded-[var(--radius-control)] bg-primary text-primary-foreground font-semibold text-xs hover:opacity-90"
                  >
                    <span>
                      {route.status === 'supported'
                        ? (isBangla ? 'এই পথে অগ্রসর হোন' : 'Proceed with this Path')
                        : (isBangla ? 'অ্যাকশন গাইড দেখুন' : 'View Action Guidance')}
                    </span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </Link>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Modals */}
      <WhatIfDrawer
        isOpen={isWhatIfOpen}
        onClose={() => setIsWhatIfOpen(false)}
        caseId={caseId}
        locale={locale}
        onApplied={fetchAssessment}
      />

      <ProcessingDetailsDrawer
        isOpen={isProcessingOpen}
        onClose={() => setIsProcessingOpen(false)}
        caseId={caseId}
        locale={locale}
      />
    </div>
  );
}
