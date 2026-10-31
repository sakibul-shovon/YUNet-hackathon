import { getTranslations } from 'next-intl/server';
import { Upload, Eye, Trash2, CheckCircle2, AlertTriangle, Layers, FileImage } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';

export default async function CaseEvidencePage({
  params,
}: {
  params: Promise<{ locale: string; id: string }>;
}) {
  const { locale, id } = await params;
  const t = await getTranslations({ locale, namespace: 'evidence' });

  const isBangla = locale === 'bn';

  return (
    <div className="space-y-6">
      {/* Header & Add Evidence CTA */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-foreground">{t('title')}</h2>
          <p className="text-xs text-muted-foreground mt-1">{t('subtitle')}</p>
        </div>
        <Button variant="primary" size="sm" className="gap-2">
          <Upload className="w-4 h-4" />
          <span>{t('upload_btn')}</span>
        </Button>
      </div>

      {/* Responsive Document Viewer Canvas (Section 5.2 & 5.3) */}
      <Card className="overflow-hidden border-2 border-border">
        <CardHeader className="bg-elevated/40 flex flex-row items-center justify-between py-3">
          <div className="flex items-center gap-2">
            <FileImage className="w-4 h-4 text-primary" />
            <span className="text-xs font-bold text-foreground font-mono">
              bKash_statement_trx9K41.png
            </span>
          </div>
          <Badge variant="success" className="text-[10px]">
            {t('status_accepted')}
          </Badge>
        </CardHeader>
        <CardContent className="p-0">
          <div className="bg-neutral-900/90 text-white min-h-[300px] md:min-h-[420px] flex flex-col items-center justify-center p-6 relative select-none">
            {/* Visual simulation of receipt with bounding box highlight */}
            <div className="w-full max-w-sm bg-neutral-800 border border-neutral-700 rounded-lg p-5 shadow-lg space-y-4 text-xs font-mono relative">
              <div className="flex justify-between border-b border-neutral-700 pb-2 text-neutral-400">
                <span>bKash Payment</span>
                <span>Success</span>
              </div>
              <div className="space-y-1">
                <span className="text-neutral-400 block text-[10px]">Recipient:</span>
                <span className="text-emerald-400 font-bold">Gadget Zone BD (01700-XXXXXX)</span>
              </div>
              {/* Highlighted Bounding Box Span */}
              <div className="p-2 rounded bg-primary/20 border-2 border-primary relative">
                <span className="absolute -top-2.5 right-2 bg-primary text-[9px] font-bold px-1.5 py-0.2 rounded text-white font-sans">
                  Span #1: Amount
                </span>
                <span className="text-neutral-400 block text-[10px]">Amount Paid:</span>
                <span className="text-lg font-bold text-white">৳ 5,000.00</span>
              </div>
              <div className="space-y-1">
                <span className="text-neutral-400 block text-[10px]">Transaction ID:</span>
                <span className="text-neutral-300">9K41MZ98P1</span>
              </div>
              <div className="text-[10px] text-neutral-500 pt-2 border-t border-neutral-700">
                15/10/2026 14:45:12
              </div>
            </div>

            <div className="absolute bottom-3 right-3 text-[10px] text-neutral-400 bg-neutral-800/80 px-2 py-1 rounded backdrop-blur-xs">
              Region [x: 42, y: 120, w: 260, h: 54] • OCR Confidence: 99.4%
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Linked Facts & Extraction Metadata */}
      <div className="space-y-3">
        <h3 className="text-sm font-bold text-foreground uppercase tracking-wider text-muted-foreground">
          {t('linked_facts')} (2)
        </h3>

        <div className="p-4 rounded-[var(--radius-control)] border border-border bg-surface flex items-center justify-between text-xs">
          <div>
            <span className="font-bold text-foreground block">Extracted Amount: ৳5,000.00 BDT</span>
            <span className="text-muted-foreground text-[11px]">Mapped to Receipt #1 (bKash Payment)</span>
          </div>
          <Badge variant="success">Confirmed Fact</Badge>
        </div>

        <div className="p-4 rounded-[var(--radius-control)] border border-border bg-surface flex items-center justify-between text-xs">
          <div>
            <span className="font-bold text-foreground block">Counterparty: Gadget Zone BD</span>
            <span className="text-muted-foreground text-[11px]">Merchant Wallet Name</span>
          </div>
          <Badge variant="success">Confirmed Fact</Badge>
        </div>
      </div>
    </div>
  );
}

