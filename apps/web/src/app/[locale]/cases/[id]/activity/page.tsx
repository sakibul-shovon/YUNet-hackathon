import { getTranslations } from 'next-intl/server';
import { Clock, Plus, CheckCircle2, FileText, Send, UserCheck } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';

export default async function CaseActivityPage({
  params,
}: {
  params: Promise<{ locale: string; id: string }>;
}) {
  const { locale, id } = await params;
  const t = await getTranslations({ locale, namespace: 'activity' });

  const isBangla = locale === 'bn';

  return (
    <div className="space-y-6">
      {/* Header & Add Update Button */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-foreground">{t('title')}</h2>
          <p className="text-xs text-muted-foreground mt-1">{t('subtitle')}</p>
        </div>
        <Button variant="primary" size="sm" className="gap-2">
          <Plus className="w-4 h-4" />
          <span>{t('add_update_btn')}</span>
        </Button>
      </div>

      {/* Human-Readable Event Timeline (Section 5.3) */}
      <Card>
        <CardContent className="p-6">
          <div className="relative pl-6 border-l-2 border-border space-y-8">
            {/* Event 1 */}
            <div className="relative">
              <span className="absolute -left-[31px] top-1 w-3 h-3 rounded-full bg-primary" />
              <div className="flex items-center gap-2">
                <Badge variant="brand" className="text-[10px]">Case Ingestion</Badge>
                <span className="text-xs text-muted-foreground font-mono">15 Oct 2026, 03:20 PM</span>
              </div>
              <h4 className="text-sm font-bold text-foreground mt-1">
                {isBangla ? 'বিরোধের বিবরণ ও বিকাশ রসিদ গৃহীত হয়েছে' : 'Dispute story and bKash receipt ingested'}
              </h4>
              <p className="text-xs text-muted-foreground mt-0.5">
                {isBangla
                  ? 'ব্যবহারকারীর বাংলা বক্তব্য থেকে এআই এক্সট্রাকশন সম্পন্ন। প্রাথমিক খসড়া তৈরি।'
                  : 'Extracted initial facts: ৳5,000 bKash memo TrxID 9K41MZ98P1 against Gadget Zone BD.'}
              </p>
            </div>

            {/* Event 2 */}
            <div className="relative">
              <span className="absolute -left-[31px] top-1 w-3 h-3 rounded-full bg-emerald-500" />
              <div className="flex items-center gap-2">
                <Badge variant="success" className="text-[10px]">Fact Confirmed</Badge>
                <span className="text-xs text-muted-foreground font-mono">15 Oct 2026, 03:25 PM</span>
              </div>
              <h4 className="text-sm font-bold text-foreground mt-1">
                {isBangla ? 'মার্চেন্টের নাম ও পরিচয় ভোক্তা কর্তৃক নিশ্চিতকৃত' : 'Merchant identity confirmed by consumer'}
              </h4>
              <p className="text-xs text-muted-foreground mt-0.5">
                User verified seller Facebook page and transaction counterparty.
              </p>
            </div>

            {/* Event 3 */}
            <div className="relative">
              <span className="absolute -left-[31px] top-1 w-3 h-3 rounded-full bg-amber-500" />
              <div className="flex items-center gap-2">
                <Badge variant="warning" className="text-[10px]">Discrepancy Flagged</Badge>
                <span className="text-xs text-muted-foreground font-mono">15 Oct 2026, 03:26 PM</span>
              </div>
              <h4 className="text-sm font-bold text-foreground mt-1">
                {isBangla ? 'পেমেন্ট অমিল: দাবিকৃত ৫,৫০০ বনাম রসিদের ৫,০০০ টাকা' : 'Payment discrepancy flagged: ৳5,500 claimed vs ৳5,000 receipt'}
              </h4>
              <p className="text-xs text-muted-foreground mt-0.5">
                Engine generated Next Best Question (NBQ) requesting clarification or second receipt.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
