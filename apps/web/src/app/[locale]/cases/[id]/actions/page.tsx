import { getTranslations } from 'next-intl/server';
import { ExternalLink, Copy } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card';
import { ActionDraftViewer } from '@/components/cases/ActionDraftViewer';

export default async function CaseActionsPage({
  params,
}: {
  params: Promise<{ locale: string; id: string }>;
}) {
  const { locale, id } = await params;
  const t = await getTranslations({ locale, namespace: 'actions' });

  const isBangla = locale === 'bn';

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold tracking-tight text-foreground">{t('title')}</h2>
        <p className="text-xs text-muted-foreground mt-1">{t('subtitle')}</p>
      </div>

      {/* 1. Interactive Draft Request Viewer with Unsubmitted State & Copy (T26) */}
      <ActionDraftViewer caseId={id} initialLocale={locale} />

      {/* 2. Official Portal Field Maps (Section 5.3 & 14.3) */}
      <Card className="border border-border bg-surface">
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
            className="text-brand hover:underline text-xs font-semibold inline-flex items-center gap-1"
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
              <p className="text-xs font-bold font-mono text-foreground">৳ 5,500.00 BDT</p>
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
