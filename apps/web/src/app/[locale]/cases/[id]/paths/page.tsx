import { WhyWhyNotTraceView } from '@/components/paths/WhyWhyNotTraceView';

export default async function CasePathsPage({
  params,
}: {
  params: Promise<{ locale: string; id: string }>;
}) {
  const { locale, id } = await params;

  return <WhyWhyNotTraceView caseId={id} locale={locale} />;
}
