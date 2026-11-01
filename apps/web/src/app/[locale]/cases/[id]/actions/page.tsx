import { getTranslations } from 'next-intl/server';

import { ActionStudioClient } from '@/components/actions/ActionStudioClient';
import { ActionDraftViewer } from '@/components/cases/ActionDraftViewer';

export default async function CaseActionsPage({
  params,
}: {
  params: Promise<{ locale: string; id: string }>;
}) {
  const { locale, id } = await params;
  const t = await getTranslations({ locale, namespace: 'actions' });

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold tracking-tight text-foreground">{t('title')}</h2>
        <p className="text-xs text-muted-foreground mt-1">{t('subtitle')}</p>
      </div>

      {/* 1. Complete Action Studio (P09.1 - P09.7) */}
      <ActionStudioClient caseId={id} locale={locale} />

      {/* 2. Interactive Letter Draft Request Viewer (T26) */}
      <div className="pt-6 border-t border-border">
        <h3 className="text-base font-bold text-foreground mb-4">
          {t('formal_notice_title')}
        </h3>
        <ActionDraftViewer caseId={id} initialLocale={locale} />
      </div>
    </div>
  );
}
