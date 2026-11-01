import { getTranslations } from 'next-intl/server';
import Link from 'next/link';
import { ArrowRight, AlertCircle, FileText, CheckCircle2, Clock } from 'lucide-react';
import { OneNextActionCard } from '@/components/ui/OneNextActionCard';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';

export default async function CaseOverviewPage({
  params,
}: {
  params: Promise<{ locale: string; id: string }>;
}) {
  const { locale, id } = await params;
  const tCase = await getTranslations({ locale, namespace: 'caseView' });

  const isBangla = locale === 'bn';

  return (
    <div className="space-y-6">
      {/* 1. ONE NEXT STEP HERO CARD (Section 5.2) */}
      <OneNextActionCard
        category={isBangla ? 'আপনার পরের কাজ' : 'One Next Step'}
        title={isBangla ? 'পেমেন্টের টাকার অমিল সমাধান করুন' : 'Clarify payment amount mismatch'}
        whyItMatters={
          isBangla
            ? 'আপনার বিবরণ অনুযায়ী মোট দাবি ৫,৫০০ টাকা, কিন্তু প্রথম বিকাশ রসিদ ৫,০০০ টাকার। অবশিষ্ট ৫০০ টাকার রসিদ যোগ করুন অথবা মোট দাবির পরিমাণ সামঞ্জস্য করুন।'
            : 'You stated a total paid sum of ৳5,500, but uploaded bKash receipt #1 accounts for ৳5,000. Add second payment receipt or reconcile claim amount.'
        }
        status="clarification_needed"
        locale={locale}
        choices={[
          {
            id: 'add_receipt',
            label: isBangla ? 'দ্বিতীয় রসিদ যোগ করুন (+৳৫০০)' : 'Add second receipt (+৳500)',
            primary: true,
            href: `/${locale}/cases/${id}/evidence`,
          },
          {
            id: 'edit_amount',
            label: isBangla ? 'টাকার পরিমাণ সংশোধন করুন' : 'Correct my amount',
            primary: false,
            href: `/${locale}/cases/${id}/review`,
          },
        ]}
      />

      {/* 2. What Happened — Concise Timeline */}
      <Card>
        <CardHeader className="pb-3 flex flex-row items-center justify-between">
          <CardTitle className="text-base font-bold flex items-center gap-2">
            <Clock className="w-4 h-4 text-primary" />
            <span>{tCase('what_happened')}</span>
          </CardTitle>
          <span className="text-xs text-muted-foreground">3 events recorded</span>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="relative pl-6 border-l-2 border-border space-y-4">
            <div className="relative">
              <span className="absolute -left-[31px] top-1 w-3 h-3 rounded-full bg-primary" />
              <span className="text-xs font-semibold text-muted-foreground block">15 Oct 2026, 02:45 PM</span>
              <p className="text-xs text-foreground font-medium mt-0.5">
                {isBangla ? 'ফেসবুক পেজে ফোন অর্ডার এবং প্রথম বিকাশ পেমেন্ট (৳৫,০০০)' : 'Phone order placed via Facebook Page; bKash advance paid (৳5,000)'}
              </p>
            </div>
            <div className="relative">
              <span className="absolute -left-[31px] top-1 w-3 h-3 rounded-full bg-primary" />
              <span className="text-xs font-semibold text-muted-foreground block">15 Oct 2026, 03:10 PM</span>
              <p className="text-xs text-foreground font-medium mt-0.5">
                {isBangla ? 'ডেলিভারি চার্জের জন্য দ্বিতীয় বিকাশ পেমেন্ট (৳৫০০)' : 'Delivery fee payment sent via bKash (৳500)'}
              </p>
            </div>
            <div className="relative">
              <span className="absolute -left-[31px] top-1 w-3 h-3 rounded-full bg-amber-500" />
              <span className="text-xs font-semibold text-muted-foreground block">18 Oct 2026, 11:00 AM</span>
              <p className="text-xs text-foreground font-medium mt-0.5">
                {isBangla ? 'প্রতিশ্রুত ৭২ ঘণ্টা অতিক্রান্ত; বিক্রেতা মেসেঞ্জারে যোগাযোগ বন্ধ করেছে' : 'Promised 72h window passed; merchant blocked customer on Messenger'}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 3. Facts Needing Review — Only Material Items */}
      <Card>
        <CardHeader className="pb-3 flex flex-row items-center justify-between">
          <CardTitle className="text-base font-bold flex items-center gap-2">
            <AlertCircle className="w-4 h-4 text-amber-600" />
            <span>{tCase('material_facts')}</span>
          </CardTitle>
          <Link
            href={`/${locale}/cases/${id}/review`}
            className="text-xs font-semibold text-primary hover:underline"
          >
            {isBangla ? 'সবগুলো দেখুন' : 'Review all facts →'}
          </Link>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div className="p-3 rounded-[var(--radius-control)] border border-border bg-surface flex flex-col sm:flex-row sm:items-center justify-between gap-2">
              <div>
                <span className="text-xs font-bold text-foreground block">Disputed Payment Total: ৳5,500</span>
                <span className="text-[11px] text-muted-foreground">Source: User narrative vs Receipt mismatch</span>
              </div>
              <Badge variant="warning">{isBangla ? 'পর্যালোচনা প্রয়োজন' : 'Needs Review'}</Badge>
            </div>

            <div className="p-3 rounded-[var(--radius-control)] border border-border bg-surface flex flex-col sm:flex-row sm:items-center justify-between gap-2">
              <div>
                <span className="text-xs font-bold text-foreground block">Merchant Identity: Gadget Zone BD</span>
                <span className="text-[11px] text-muted-foreground">Source: bKash statement counterparty</span>
              </div>
              <Badge variant="success">{isBangla ? 'নিশ্চিতকৃত' : 'Confirmed'}</Badge>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 4. Prepared Actions / Quick Links */}
      <div className="flex flex-col sm:flex-row gap-4">
        <Link
          href={`/${locale}/cases/${id}/paths`}
          className="flex-1 p-4 rounded-[var(--radius-panel)] border border-border bg-surface hover:border-primary/40 transition-colors"
        >
          <span className="text-xs font-bold text-primary uppercase tracking-wide block mb-1">
            {isBangla ? 'আইনি পথ' : 'Viable Paths'}
          </span>
          <p className="text-sm font-semibold text-foreground">
            {isBangla ? 'ভোক্তা অধিকার ধারা ৪৫ যাচাই করুন' : 'Inspect DNCRP Section 45 Route'}
          </p>
        </Link>

        <Link
          href={`/${locale}/cases/${id}/actions`}
          className="flex-1 p-4 rounded-[var(--radius-panel)] border border-border bg-surface hover:border-primary/40 transition-colors"
        >
          <span className="text-xs font-bold text-primary uppercase tracking-wide block mb-1">
            {isBangla ? 'প্রস্তুতকৃত পদক্ষেপ' : 'Actions Studio'}
          </span>
          <p className="text-sm font-semibold text-foreground">
            {isBangla ? 'অভিযোগপত্র খসড়া ও পোর্টাল ডাটা' : 'Draft Notice & Portal Fast-Copy'}
          </p>
        </Link>
      </div>
    </div>
  );
}

