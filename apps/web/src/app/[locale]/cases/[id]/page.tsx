import { DynamicCaseOverview } from '@/components/cases/DynamicCaseOverview';

export default async function CaseOverviewPage({
  params,
}: {
  params: Promise<{ locale: string; id: string }>;
}) {
  const { locale, id } = await params;

  return <DynamicCaseOverview caseId={id} locale={locale} />;
}
