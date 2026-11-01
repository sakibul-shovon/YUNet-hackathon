import { getTranslations } from 'next-intl/server';

import { LivingCaseActivityClient } from '@/components/cases/LivingCaseActivityClient';

export default async function CaseActivityPage({
  params,
}: {
  params: Promise<{ locale: string; id: string }>;
}) {
  const { locale, id } = await params;
  const t = await getTranslations({ locale, namespace: 'activity' });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold tracking-tight text-foreground">{t('title')}</h2>
        <p className="text-xs text-muted-foreground mt-1">{t('subtitle')}</p>
      </div>

      {/* Living Case Milestones, Reminders, and Decision Diff Client (P10.1 - P10.5) */}
      <LivingCaseActivityClient caseId={id} locale={locale} />
    </div>
  );
}
