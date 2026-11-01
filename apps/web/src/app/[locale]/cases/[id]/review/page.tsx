import { getTranslations } from 'next-intl/server';
import Link from 'next/link';
import { ArrowLeft } from 'lucide-react';
import { Header } from '@/components/layout/Header';
import { Badge } from '@/components/ui/Badge';
import { FactReviewClient } from '@/components/cases/FactReviewClient';

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
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-muted-foreground hover:text-foreground mb-2"
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

        {/* Interactive Fact Review & Desired Remedy Component */}
        <FactReviewClient caseId={id} locale={locale} />
      </main>
    </div>
  );
}
