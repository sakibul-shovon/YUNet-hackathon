import { EvidenceVaultClient } from '@/components/cases/EvidenceVaultClient';

export default async function CaseEvidencePage({
  params,
}: {
  params: Promise<{ locale: string; id: string }>;
}) {
  const { locale, id } = await params;

  return (
    <EvidenceVaultClient
      caseId={id}
      locale={locale}
      initialItems={[]}
      initialReconciliation={null}
    />
  );
}
