import { getTranslations } from 'next-intl/server';
import Link from 'next/link';
import { ArrowLeft, ArrowRight, Shield, CheckCircle2 } from 'lucide-react';
import { Header } from '@/components/layout/Header';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';

export default async function HowItWorksPage({ params }: { params: Promise<{ locale: string }> }) {
  const { locale } = await params;
  const t = await getTranslations({ locale, namespace: 'landing' });
  const tNav = await getTranslations({ locale, namespace: 'nav' });

  const headerLabels = {
    home: tNav('home'),
    scenarios: tNav('scenarios'),
    cases: tNav('overview'),
    startCase: t('start_cta'),
  };

  const isBangla = locale === 'bn';

  return (
    <div className="min-h-screen flex flex-col bg-canvas text-foreground">
      <Header locale={locale} labels={headerLabels} />

      <main className="flex-1 max-w-4xl mx-auto px-4 md:px-8 py-12 w-full">
        <Link
          href={`/${locale}`}
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-muted-foreground hover:text-foreground mb-6"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>{isBangla ? 'হোমে ফিরে যান' : 'Back to home'}</span>
        </Link>

        <h1 className="text-3xl md:text-4xl font-extrabold tracking-tight mb-4">
          {isBangla ? 'এবার কি? (EbarKi) যেভাবে কাজ করে' : 'How EbarKi Works'}
        </h1>
        <p className="text-muted-foreground text-base mb-10 leading-relaxed">
          {isBangla
            ? 'ভোক্তা বিরোধে বিভ্রান্তিকর পরিস্থিতি থেকে সুনির্দিষ্ট পদক্ষেপ গ্রহণের একটি স্বচ্ছ ৪-ধাপের প্রক্রিয়া।'
            : 'A transparent, four-step process turning confusing consumer disputes into actionable, evidence-backed steps.'}
        </p>

        <div className="space-y-6">
          <Card>
            <CardHeader className="flex flex-row items-center gap-4">
              <div className="w-9 h-9 rounded-full bg-primary text-primary-foreground font-bold flex items-center justify-center shrink-0">
                1
              </div>
              <CardTitle className="text-lg">
                {isBangla ? '১. বিরোধের বিবরণ ও প্রমাণাদি প্রদান' : '1. Multimodal Intake & Evidence'}
              </CardTitle>
            </CardHeader>
            <CardContent className="text-sm text-muted-foreground space-y-2">
              <p>
                {isBangla
                  ? 'আপনি আপনার মাতৃভাষায় (বাংলা, ইংরেজি বা বাংলিশ) ঘটনাটি বর্ণনা করতে পারেন। বিকাশ, নগদ বা ব্যাংক রসিদ, ফেসবুক মেসেঞ্জার চ্যাট স্ক্রিনশট এবং রসিদের ছবি আপলোড করতে পারবেন।'
                  : 'Narrate what happened in Bengali, English, or Banglish voice/text. Upload receipts (bKash/Nagad/bank memos), photos, or chat screenshots into encrypted private storage.'}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center gap-4">
              <div className="w-9 h-9 rounded-full bg-primary text-primary-foreground font-bold flex items-center justify-center shrink-0">
                2
              </div>
              <CardTitle className="text-lg">
                {isBangla ? '২. তথ্য যাচাই ও পর্যালোচনা' : '2. Fact Review & User Veto'}
              </CardTitle>
            </CardHeader>
            <CardContent className="text-sm text-muted-foreground space-y-2">
              <p>
                {isBangla
                  ? 'আমাদের এআই মডেল রসিদ বা বক্তব্য থেকে তারিখ, টাকার পরিমাণ এবং বিক্রেতার নাম প্রস্তাব করে। কোনো তথ্যই আপনার নিশ্চিতকরণ বা সংশোধন ছাড়া চূড়ান্ত বলে গণ্য হবে না।'
                  : 'AI proposes key entities (dates, transaction sums, seller details) mapped directly to evidence bounding boxes. You have complete control to confirm, correct, or mark items unknown.'}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center gap-4">
              <div className="w-9 h-9 rounded-full bg-primary text-primary-foreground font-bold flex items-center justify-center shrink-0">
                3
              </div>
              <CardTitle className="text-lg">
                {isBangla ? '৩. আইনি ও প্রাতিষ্ঠানিক পথ অনুধাবন' : '3. Statutory Path Evaluation'}
              </CardTitle>
            </CardHeader>
            <CardContent className="text-sm text-muted-foreground space-y-2">
              <p>
                {isBangla
                  ? 'জাতীয় ভোক্তা অধিকার সংরক্ষণ অধিদপ্তর (DNCRP), বাংলাদেশ ব্যাংক, বিটিআরসি ইত্যাদির আইন অনুযায়ী আপনার বিরোধটির জন্য কোন কোন উপায় বিদ্যমান তা স্পষ্টভাবে দেখুন।'
                  : 'The deterministic AST rule engine evaluates applicable paths (DNCRP Consumer Protection Act 2009, Bangladesh Bank PSD guidelines, BTRC consumer clauses) with clear rationale.'}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center gap-4">
              <div className="w-9 h-9 rounded-full bg-primary text-primary-foreground font-bold flex items-center justify-center shrink-0">
                4
              </div>
              <CardTitle className="text-lg">
                {isBangla ? '৪. পদক্ষেপ ও ফলো-আপ' : '4. Action & Follow-Up'}
              </CardTitle>
            </CardHeader>
            <CardContent className="text-sm text-muted-foreground space-y-2">
              <p>
                {isBangla
                  ? 'সঠিক নোটিশ বা অভিযোগপত্র ডাউনলোড করুন, সরকারি পোর্টালে জমা দেওয়ার প্রয়োজনীয় তথ্য কপি করুন এবং বিক্রেতার উত্তরের ভিত্তিতে পরবর্তী করণীয় জানুন।'
                  : 'Download official complaint PDFs, copy portal-ready text fields, and record subsequent seller responses to trigger living case reassessment.'}
              </p>
            </CardContent>
          </Card>
        </div>

        <div className="mt-12 text-center">
          <Link
            href={`/${locale}/cases/new`}
            className="inline-flex items-center gap-2 px-6 py-3 rounded-[var(--radius-control)] bg-primary text-primary-foreground font-semibold hover:opacity-90 transition-opacity"
          >
            <span>{t('start_cta')}</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      </main>
    </div>
  );
}

