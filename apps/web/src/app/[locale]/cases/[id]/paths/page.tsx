import { getTranslations } from 'next-intl/server';
import Link from 'next/link';
import { Compass, CheckCircle2, XCircle, AlertCircle, Sparkles, Scale, ArrowRight } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';

export default async function CasePathsPage({
  params,
}: {
  params: Promise<{ locale: string; id: string }>;
}) {
  const { locale, id } = await params;
  const t = await getTranslations({ locale, namespace: 'paths' });

  const isBangla = locale === 'bn';

  return (
    <div className="space-y-6">
      {/* Header & What-If Simulator Trigger */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-foreground">{t('title')}</h2>
          <p className="text-xs text-muted-foreground mt-1">{t('subtitle')}</p>
        </div>
        <Button variant="outline" size="sm" className="gap-2 border-primary text-primary hover:bg-[var(--brand-soft)]">
          <Sparkles className="w-4 h-4" />
          <span>{t('what_if_btn')}</span>
        </Button>
      </div>

      {/* Path 1: Primary Recommended Route */}
      <Card className="border-2 border-primary/60 bg-gradient-to-br from-surface to-elevated/20 shadow-xs">
        <CardHeader>
          <div className="flex items-center justify-between mb-1.5">
            <Badge variant="brand">{t('recommended_badge')}</Badge>
            <span className="text-xs text-muted-foreground font-mono">Route #DNCRP-45</span>
          </div>
          <CardTitle className="text-lg font-bold text-foreground">
            {isBangla
              ? 'ভোক্তা অধিকার সংরক্ষণ অধিদপ্তর (DNCRP) — ধারা ৪৫'
              : 'Direct Consumer Remedy: DNCRP Section 45 Notice & Complaint'}
          </CardTitle>
          <CardDescription className="text-xs">
            {isBangla
              ? 'আইনি ভিত্তি: ভোক্তা অধিকার সংরক্ষণ আইন ২০০৯ (ধারা ৪৫ ও ৭৬)'
              : 'Statutory basis: Consumer Rights Protection Act, 2009 (Sections 45 & 76)'}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4 text-xs">
          {/* Why this path */}
          <div className="p-3 rounded-[var(--radius-control)] bg-[var(--brand-soft)]/50 border border-primary/20 space-y-1">
            <span className="font-bold text-primary block flex items-center gap-1.5">
              <CheckCircle2 className="w-4 h-4" />
              <span>{t('why_path')}</span>
            </span>
            <p className="text-foreground/90 leading-relaxed">
              {isBangla
                ? 'অনলাইনে মূল্য পরিশোধ সত্ত্বেও প্রতিশ্রুত পণ্য সরবরাহ করা হয়নি এবং বিক্রেতা যোগাযোগ বিচ্ছিন্ন করেছে। ভোক্তা আইনের অধীনে এটি সুস্পষ্ট ব্যত্যয়।'
                : 'Payment was transferred for a specific consumer product, delivery was promised within 72 hours, but merchant failed to fulfill. Meets all prima facie requirements.'}
            </p>
          </div>

          {/* Missing Conditions to Satisfy */}
          <div className="p-3 rounded-[var(--radius-control)] bg-[var(--warning-soft)]/60 border border-[var(--warning-ink)]/20 space-y-1">
            <span className="font-bold text-[var(--warning-ink)] block flex items-center gap-1.5">
              <AlertCircle className="w-4 h-4" />
              <span>{t('missing_conditions')}</span>
            </span>
            <p className="text-foreground/90 leading-relaxed">
              {isBangla
                ? '১. মোট ৫,৫০০ টাকার সম্পূর্ণ প্রমাণ (দ্বিতীয় ৫০০ টাকার রসিদ) প্রয়োজন। ২. ঘটনার ৩০ দিনের মধ্যে অনলাইনে অভিযোগ দাখিল নিশ্চিত করতে হবে।'
                : '1. Reconcile remaining ৳500 receipt memo to substantiate full ৳5,500 claim. 2. Must file within statutory 30-day window from 15 Oct 2026.'}
            </p>
          </div>

          <div className="pt-2">
            <Link
              href={`/${locale}/cases/${id}/actions`}
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-[var(--radius-control)] bg-primary text-primary-foreground font-semibold text-xs hover:opacity-90"
            >
              <span>{t('continue_path_btn')}</span>
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </CardContent>
      </Card>

      {/* Path 2: Alternative Banking/MFS Route */}
      <Card className="opacity-90">
        <CardHeader>
          <div className="flex items-center justify-between mb-1.5">
            <Badge variant="neutral">{t('alternative_badge')}</Badge>
            <span className="text-xs text-muted-foreground font-mono">Route #BB-MFS</span>
          </div>
          <CardTitle className="text-base font-bold text-foreground">
            {isBangla
              ? 'বাংলাদেশ ব্যাংক ও এমএফএস চ্যানেল অভিযোগ'
              : 'MFS Provider Escalation: Bangladesh Bank PSD'}
          </CardTitle>
          <CardDescription className="text-xs">
            {isBangla
              ? 'আইনি ভিত্তি: বাংলাদেশ ব্যাংক পেমেন্ট সিস্টেমস ডিপার্টমেন্ট নির্দেশিকা'
              : 'Statutory basis: Bangladesh Bank Payment Systems Directives'}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-3 text-xs">
          <div className="p-3 rounded-[var(--radius-control)] bg-elevated border border-border space-y-1">
            <span className="font-bold text-muted-foreground block flex items-center gap-1.5">
              <XCircle className="w-4 h-4 text-muted-foreground" />
              <span>{t('why_not')}</span>
            </span>
            <p className="text-muted-foreground leading-relaxed">
              {isBangla
                ? 'বিকাশ সফলভাবে টাকা মার্চেন্ট একাউন্টে পাঠিয়েছে (লেনদেন অসফল ছিল না)। তাই এটি পেমেন্ট গেটওয়ের প্রযুক্তিগত ত্রুটি নয়, বরং বিক্রেতার পণ্য সরবরাহের বিরোধ।'
                : 'The bKash transfer executed successfully to the merchant wallet without technical network debit failure. Primary grievance lies against merchant fulfillment, not payment rail.'}
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

