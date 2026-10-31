import { getTranslations } from 'next-intl/server';
import { FileText, Copy, Download, CheckCircle2, AlertTriangle, ExternalLink, ShieldAlert } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';

export default async function CaseActionsPage({
  params,
}: {
  params: Promise<{ locale: string; id: string }>;
}) {
  const { locale, id } = await params;
  const t = await getTranslations({ locale, namespace: 'actions' });

  const isBangla = locale === 'bn';

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold tracking-tight text-foreground">{t('title')}</h2>
        <p className="text-xs text-muted-foreground mt-1">{t('subtitle')}</p>
      </div>

      {/* Explicit Unsubmitted State Notice (Section 5.3 & Section 3.3) */}
      <div className="p-4 rounded-[var(--radius-panel)] border-2 border-amber-500/40 bg-[var(--warning-soft)]/60 text-[var(--warning-ink)] flex items-start gap-3">
        <AlertTriangle className="w-5 h-5 shrink-0 mt-0.5" />
        <div className="text-xs space-y-1">
          <span className="font-bold block uppercase tracking-wide">
            {isBangla ? 'স্ট্যাটাস: প্রস্তুতকৃত, কিন্তু দাখিল করা হয়নি' : 'Status: Prepared, Not Submitted'}
          </span>
          <p className="leading-relaxed">
            {t('unsubmitted_notice')}
          </p>
        </div>
      </div>

      {/* 1. Editable Formal Complaint / Request Draft */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between pb-3">
          <div>
            <CardTitle className="text-base font-bold">{t('dnCRP_complaint_title')}</CardTitle>
            <CardDescription className="text-xs">
              {isBangla ? 'ভোক্তা অধিকার সংরক্ষণ অধিদপ্তরে প্রেরণের জন্য প্রস্তুত খসড়া' : 'Formatted for DNCRP Consumer Filing'}
            </CardDescription>
          </div>
          <Button variant="outline" size="sm" className="gap-1.5 text-xs">
            <Download className="w-3.5 h-3.5 text-primary" />
            <span>{t('export_pdf_btn')}</span>
          </Button>
        </CardHeader>
        <CardContent>
          <div className="p-4 rounded-[var(--radius-control)] border border-border bg-surface font-mono text-xs leading-relaxed text-foreground/90 whitespace-pre-wrap select-all">
{`বরাবর,
মহাপরিচালক
জাতীয় ভোক্তা অধিকার সংরক্ষণ অধিদপ্তর
১ কারওয়ান বাজার, ঢাকা-১২১৫।

বিষয়: ভোক্তা অধিকার সংরক্ষণ আইন, ২০০৯ এর ৪৫ ধারা মোতাবেক প্রতিশ্রুত পণ্য সরবরাহে ব্যর্থতার বিরুদ্ধে অভিযোগ।

মহোদয়,
বিনীত নিবেদন এই যে, আমি নিম্নস্বাক্ষরকারী একজন সাধারণ ভোক্তা। গত ১৫ অক্টোবর ২০২৬ তারিখে ফেসবুক পেজ 'Gadget Zone BD' থেকে একটি মোবাইল ফোন ৫,৫০০ টাকার বিনিময়ে ক্রয়ের চুক্তি করি এবং তাদের বিকাশ নম্বরে (TrxID: 9K41MZ98P1) টাকা পরিশোধ করি। 

বিক্রেতা ৭২ ঘণ্টার মধ্যে ডেলিভারির প্রতিশ্রুতি দেওয়া সত্ত্বেও পণ্য সরবরাহ করেনি এবং পরবর্তীতে মেসেঞ্জারে সকল যোগাযোগ বন্ধ করে দেয়। 

অতএব, মহোদয়ের সমীপে বিনীত প্রার্থনা, উক্ত ঘটনার প্রেক্ষিতে বিক্রেতার বিরুদ্ধে আইনানুগ ব্যবস্থা গ্রহণ এবং আমার পরিশোধিত ৫,৫০০ টাকা রিফান্ডের প্রয়োজনীয় নির্দেশনা প্রদানে বাধিত করবেন।

সংযুক্ত প্রমাণাদি:
১. বিকাশ পেমেন্ট স্টেটমেন্ট ও ট্রানজেকশন আইডি
২. অর্ডার চ্যাট স্ক্রিনশট ও প্রতিশ্রুত ডেলিভারি বার্তা

বিনীত,
(ভোক্তার স্বাক্ষর ও যোগাযোগের নম্বর)`}
          </div>
        </CardContent>
      </Card>

      {/* 2. Official Portal Field Maps (Section 5.3 & 14.3) */}
      <Card>
        <CardHeader className="pb-3 flex flex-row items-center justify-between">
          <div>
            <CardTitle className="text-base font-bold">{t('portal_fields_title')}</CardTitle>
            <CardDescription className="text-xs">
              {isBangla ? 'সরকারি পোর্টালে ফর্ম পূরণের সময় সহজে কপি করুন' : 'One-click copy helpers for official form submission'}
            </CardDescription>
          </div>
          <a
            href="https://dncrp.portal.gov.bd"
            target="_blank"
            rel="noreferrer"
            className="text-primary hover:underline text-xs font-semibold inline-flex items-center gap-1"
          >
            <span>dncrp.portal.gov.bd</span>
            <ExternalLink className="w-3.5 h-3.5" />
          </a>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="p-3 rounded-md border border-border bg-elevated/40 flex items-center justify-between">
            <div className="space-y-0.5">
              <span className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">
                মার্চেন্ট / প্রতিষ্ঠানের নাম (Merchant Name)
              </span>
              <p className="text-xs font-bold font-mono text-foreground">Gadget Zone BD</p>
            </div>
            <Button size="sm" variant="outline" className="text-xs gap-1.5 h-8">
              <Copy className="w-3.5 h-3.5" />
              <span>{t('copy_field_btn')}</span>
            </Button>
          </div>

          <div className="p-3 rounded-md border border-border bg-elevated/40 flex items-center justify-between">
            <div className="space-y-0.5">
              <span className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">
                দাবিকৃত আর্থিক পরিমাণ (Disputed Sum)
              </span>
              <p className="text-xs font-bold font-mono text-foreground">5500 BDT</p>
            </div>
            <Button size="sm" variant="outline" className="text-xs gap-1.5 h-8">
              <Copy className="w-3.5 h-3.5" />
              <span>{t('copy_field_btn')}</span>
            </Button>
          </div>

          <div className="p-3 rounded-md border border-border bg-elevated/40 flex items-center justify-between">
            <div className="space-y-0.5">
              <span className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">
                অভিযোগের ধারা (Statutory Section)
              </span>
              <p className="text-xs font-bold font-mono text-foreground">Section 45 (ভোক্তা অধিকার সংরক্ষণ আইন, ২০০৯)</p>
            </div>
            <Button size="sm" variant="outline" className="text-xs gap-1.5 h-8">
              <Copy className="w-3.5 h-3.5" />
              <span>{t('copy_field_btn')}</span>
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
