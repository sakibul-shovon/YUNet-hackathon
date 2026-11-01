import { getTranslations } from 'next-intl/server';
import { EvidenceVaultClient } from '@/components/cases/EvidenceVaultClient';

export default async function CaseEvidencePage({
  params,
}: {
  params: Promise<{ locale: string; id: string }>;
}) {
  const { locale, id } = await params;
  const t = await getTranslations({ locale, namespace: 'evidence' });

  // Initial mock evidence item for visual demo if backend isn't pre-seeded
  const initialItems = [
    {
      id: 'ev-demo-01',
      case_id: id,
      original_filename: 'bKash_statement_trx9K41.png',
      declared_mime_type: 'image/png',
      detected_mime_type: 'image/png',
      byte_size: 142380,
      sha256_hash: '9f83acde9851234b4a1b029384812f0a12e34d56789abcdef0123456789abcde',
      status: 'accepted',
      is_quarantined: false,
      created_at: new Date().toISOString(),
    },
  ];

  const initialReconciliation = {
    case_id: id,
    narrated_amount_minor_units: 500000,
    linked_evidence_total_minor_units: 500000,
    discrepancy_minor_units: 0,
    is_reconciled: true,
    status: 'reconciled',
    reconciled_items: [
      {
        evidence_id: 'ev-demo-01',
        filename: 'bKash_statement_trx9K41.png',
        amount_minor_units: 500000,
        is_duplicate: false,
        is_linked: true,
      },
    ],
    unlinked_items: [],
    prompt_en: 'All amounts reconciled (BDT 5,000.00).',
    prompt_bn: 'টাকার পরিমাণ সম্পূর্ণভাবে মিলে গেছে (৳৫,০০০.০০)।',
  };

  return (
    <EvidenceVaultClient
      caseId={id}
      locale={locale}
      initialItems={initialItems}
      initialReconciliation={initialReconciliation}
    />
  );
}
