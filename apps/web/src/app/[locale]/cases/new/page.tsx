import { getTranslations } from 'next-intl/server';
import Link from 'next/link';
import { ArrowLeft, Mic, Upload, Shield, Sparkles } from 'lucide-react';
import { Header } from '@/components/layout/Header';
import { Button } from '@/components/ui/Button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card';
import { Textarea } from '@/components/ui/Textarea';
import { Badge } from '@/components/ui/Badge';

export default async function IntakePage({ params }: { params: Promise<{ locale: string }> }) {
  const { locale } = await params;
  const t = await getTranslations({ locale, namespace: 'intake' });
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
          startCase: t('submit_btn'),
        }}
      />

      <main className="flex-1 max-w-3xl mx-auto px-4 md:px-8 py-10 w-full">
        <Link
          href={`/${locale}`}
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-muted-foreground hover:text-foreground mb-6"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>{isBangla ? 'ফিরে যান' : 'Back'}</span>
        </Link>

        <div className="mb-8">
          <Badge variant="brand" className="mb-2">
            Step 1 of 4: Tell Your Story
          </Badge>
          <h1 className="text-3xl font-extrabold tracking-tight text-foreground">
            {t('title')}
          </h1>
          <p className="text-muted-foreground text-sm mt-1.5 leading-relaxed">
            {t('subtitle')}
          </p>
        </div>

        <form action={`/${locale}/cases/case_demo_phone`} method="GET" className="space-y-6">
          {/* 1. Dispute Story */}
          <Card>
            <CardHeader className="pb-3 flex flex-row items-center justify-between">
              <div>
                <CardTitle className="text-base font-bold">{t('story_label')}</CardTitle>
                <CardDescription className="text-xs">
                  {isBangla ? 'বাংলা, ইংরেজি বা বাংলিশে লিখুন' : 'Write in Bangla, English or Banglish'}
                </CardDescription>
              </div>
              <Button type="button" variant="outline" size="sm" className="gap-1.5 text-xs">
                <Mic className="w-3.5 h-3.5 text-red-600" />
                <span>{isBangla ? 'ভয়েস ইনপুট' : 'Speak'}</span>
              </Button>
            </CardHeader>
            <CardContent>
              <Textarea
                rows={5}
                placeholder={t('story_placeholder')}
                defaultValue="আমি ফেসবুকের একটি পেজ থেকে ৫,৫০০ টাকায় একটি ফোন অর্ডার করেছিলাম। ১৫ অক্টোবর বিকাশে টাকা দিই, কিন্তু তারা আমাকে ব্লক করে দেয় এবং পণ্য পাঠায়নি।"
                className="text-sm font-medium"
              />
            </CardContent>
          </Card>

          {/* 2. Desired Outcome */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-base font-bold">{t('outcome_label')}</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-2.5">
                <label className="inline-flex items-center gap-2 px-3.5 py-2 rounded-[var(--radius-control)] border border-primary bg-[var(--brand-soft)] text-xs font-semibold text-primary cursor-pointer">
                  <input type="radio" name="remedy" defaultChecked className="accent-primary" />
                  <span>{t('outcome_refund')}</span>
                </label>
                <label className="inline-flex items-center gap-2 px-3.5 py-2 rounded-[var(--radius-control)] border border-border bg-surface text-xs font-semibold text-foreground cursor-pointer hover:bg-elevated">
                  <input type="radio" name="remedy" className="accent-primary" />
                  <span>{t('outcome_replacement')}</span>
                </label>
                <label className="inline-flex items-center gap-2 px-3.5 py-2 rounded-[var(--radius-control)] border border-border bg-surface text-xs font-semibold text-foreground cursor-pointer hover:bg-elevated">
                  <input type="radio" name="remedy" className="accent-primary" />
                  <span>{t('outcome_apology')}</span>
                </label>
              </div>
            </CardContent>
          </Card>

          {/* 3. Attachments */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-base font-bold">{t('attachments_label')}</CardTitle>
              <CardDescription className="text-xs">{t('attachments_hint')}</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="border-2 border-dashed border-border rounded-[var(--radius-panel)] p-6 text-center hover:bg-elevated/40 transition-colors cursor-pointer">
                <Upload className="w-8 h-8 mx-auto text-muted-foreground mb-2" />
                <p className="text-xs font-semibold text-foreground">
                  {isBangla ? 'ফাইল ড্র্যাগ করে ছাড়ুন অথবা ক্লিক করুন' : 'Drag and drop receipts/screenshots, or browse'}
                </p>
                <p className="text-[11px] text-muted-foreground mt-1">
                  JPG, PNG, PDF up to 10MB per file
                </p>
              </div>
            </CardContent>
          </Card>

          {/* Privacy Notice & Submit */}
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-2">
            <div className="flex items-center gap-2 text-xs text-muted-foreground">
              <Shield className="w-4 h-4 text-primary shrink-0" />
              <span>{t('privacy_notice')}</span>
            </div>

            <Button type="submit" size="lg" variant="primary" className="w-full sm:w-auto font-semibold">
              <span>{t('submit_btn')}</span>
            </Button>
          </div>
        </form>
      </main>
    </div>
  );
}
