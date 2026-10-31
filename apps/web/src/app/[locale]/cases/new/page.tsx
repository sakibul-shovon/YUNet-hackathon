import { getTranslations } from 'next-intl/server';
import Link from 'next/link';
import { ArrowLeft } from 'lucide-react';
import { Header } from '@/components/layout/Header';
import { Badge } from '@/components/ui/Badge';
import { IntakeForm } from '@/components/cases/IntakeForm';

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

        <IntakeForm
          locale={locale}
          labels={{
            story_label: t('story_label'),
            story_hint: isBangla ? 'বাংলা, ইংরেজি বা বাংলিশে লিখুন' : 'Write in Bangla, English or Banglish',
            story_placeholder: t('story_placeholder'),
            title_label: isBangla ? 'বিরোধের শিরোনাম' : 'Dispute Title',
            title_placeholder: isBangla ? 'যেমন: অনলাইন অর্ডারের পণ্য ডেলিভারি দেয়নি' : 'e.g. Non-delivery of ordered smartphone',
            outcome_label: t('outcome_label'),
            outcome_refund: t('outcome_refund'),
            outcome_replacement: t('outcome_replacement'),
            outcome_apology: t('outcome_apology'),
            attachments_label: t('attachments_label'),
            attachments_hint: t('attachments_hint'),
            privacy_notice: t('privacy_notice'),
            submit_btn: t('submit_btn'),
            submitting_btn: isBangla ? 'জমা দেওয়া হচ্ছে...' : 'Submitting...',
          }}
        />
      </main>
    </div>
  );
}
