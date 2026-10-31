import { getTranslations } from 'next-intl/server';
import Link from 'next/link';
import { ArrowLeft, Check, Edit3, HelpCircle, X, Shield, AlertTriangle } from 'lucide-react';
import { Header } from '@/components/layout/Header';
import { Button } from '@/components/ui/Button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';

export default async function FactReviewPage({
  params,
}: {
  params: Promise<{ locale: string; id: string }>;
}) {
  const { locale, id } = await params;
  const t = await getTranslations({ locale, namespace: 'review' });
  const tNav = await getTranslations({ locale, namespace: 'nav' });

  const isBangla = locale === 'bn';

  return (
    <div className="min-h-screen flex flex-col bg-canvas text-foreground">
      <Header
        locale={locale}
        labels={{
          home: tNav('home'),
          scenarios: tNav('scenarios'),
          cases: tNav('overview'),
          startCase: 'Start',
        }}
      />

      <main className="flex-1 max-w-4xl mx-auto px-4 md:px-8 py-10 w-full space-y-6">
        <Link
          href={`/${locale}/cases/${id}`}
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-muted-foreground hover:text-foreground mb-4"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>{isBangla ? 'কেস ওভারভিউতে ফিরে যান' : 'Back to Case Overview'}</span>
        </Link>

        <div>
          <Badge variant="brand" className="mb-2">User Control Center</Badge>
          <h1 className="text-2xl md:text-3xl font-extrabold tracking-tight text-foreground">
            {t('title')}
          </h1>
          <p className="text-xs md:text-sm text-muted-foreground mt-1">
            {t('subtitle')}
          </p>
        </div>

        {/* Fact Card 1: Contradictory Amount */}
        <Card className="border-2 border-amber-500/40 bg-surface">
          <CardHeader className="pb-3 flex flex-row items-start justify-between">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <Badge variant="warning">{isBangla ? 'দ্বন্দ্বমূলক তথ্য' : 'Contradiction Detected'}</Badge>
                <span className="text-[11px] font-mono text-muted-foreground">Assertion #F-001</span>
              </div>
              <CardTitle className="text-lg font-bold">
                {isBangla ? 'মোট দাবিকৃত টাকার পরিমাণ' : 'Total Disputed Claim Amount'}
              </CardTitle>
            </div>
          </CardHeader>
          <CardContent className="space-y-4 text-xs">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 p-3.5 rounded-lg bg-elevated/40 border border-border">
              <div>
                <span className="text-muted-foreground block text-[10px] uppercase font-bold">
                  {isBangla ? 'আপনার বর্ণনায় পাওয়া গেছে:' : 'From Your Narrative:'}
                </span>
                <span className="text-base font-bold text-foreground">৳ 5,500.00 BDT</span>
              </div>
              <div>
                <span className="text-muted-foreground block text-[10px] uppercase font-bold">
                  {isBangla ? 'সংযুক্ত রসিদ #১ অনুযায়ী:' : 'From Receipt #1 (bKash):'}
                </span>
                <span className="text-base font-bold text-amber-600 dark:text-amber-400">৳ 5,000.00 BDT</span>
              </div>
            </div>

            {/* User Veto & Correction Controls (Section 5.3) */}
            <div className="flex flex-wrap gap-2 pt-1">
              <Button size="sm" variant="primary" className="gap-1.5 text-xs">
                <Check className="w-3.5 h-3.5" />
                <span>{isBangla ? '৫,৫০০ টাকাই সঠিক (রসিদ ২টি)' : 'Keep ৳5,500 (Two Memos)'}</span>
              </Button>
              <Button size="sm" variant="outline" className="gap-1.5 text-xs">
                <Edit3 className="w-3.5 h-3.5" />
                <span>{isBangla ? 'সংশোধন করে ৫,০০০ করুন' : 'Correct to ৳5,000'}</span>
              </Button>
              <Button size="sm" variant="ghost" className="gap-1.5 text-xs text-muted-foreground">
                <HelpCircle className="w-3.5 h-3.5" />
                <span>{t('unknown_btn')}</span>
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Fact Card 2: Merchant Identity */}
        <Card>
          <CardHeader className="pb-3 flex flex-row items-start justify-between">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <Badge variant="success">{isBangla ? 'নিশ্চিতকৃত' : 'Confirmed'}</Badge>
                <span className="text-[11px] font-mono text-muted-foreground">Assertion #F-002</span>
              </div>
              <CardTitle className="text-base font-bold">
                {isBangla ? 'বিক্রেতার নাম ও ফেসবুক পেজ' : 'Seller / Merchant Identity'}
              </CardTitle>
            </div>
          </CardHeader>
          <CardContent className="space-y-3 text-xs">
            <div className="p-3 rounded-lg bg-elevated/40 border border-border">
              <span className="font-semibold text-foreground text-sm block">Gadget Zone BD</span>
              <span className="text-muted-foreground text-[11px]">
                Source: bKash Statement Trx 9K41MZ98P1
              </span>
            </div>
          </CardContent>
        </Card>
      </main>
    </div>
  );
}
