import { getTranslations } from 'next-intl/server';
import Link from 'next/link';
import type { ReactNode } from 'react';
import {
  FileText,
  Compass,
  CheckCircle,
  Clock,
  Shield,
  Layers,
  ArrowLeft,
  ExternalLink,
  Trash2,
} from 'lucide-react';
import { Header } from '@/components/layout/Header';
import { Badge } from '@/components/ui/Badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';

export default async function CaseLayout({
  children,
  params,
}: {
  children: ReactNode;
  params: Promise<{ locale: string; id: string }>;
}) {
  const { locale, id } = await params;
  const tNav = await getTranslations({ locale, namespace: 'nav' });
  const tLanding = await getTranslations({ locale, namespace: 'landing' });
  const tCase = await getTranslations({ locale, namespace: 'caseView' });

  const isBangla = locale === 'bn';

  const navTabs = [
    { name: tNav('overview'), href: `/${locale}/cases/${id}`, icon: FileText },
    { name: tNav('evidence'), href: `/${locale}/cases/${id}/evidence`, icon: Layers },
    { name: tNav('paths'), href: `/${locale}/cases/${id}/paths`, icon: Compass },
    { name: tNav('actions'), href: `/${locale}/cases/${id}/actions`, icon: CheckCircle },
    { name: tNav('activity'), href: `/${locale}/cases/${id}/activity`, icon: Clock },
  ];

  return (
    <div className="min-h-screen flex flex-col bg-canvas text-foreground">
      <Header
        locale={locale}
        labels={{
          home: tNav('home'),
          scenarios: tNav('scenarios'),
          cases: tNav('overview'),
          startCase: tLanding('start_cta'),
        }}
      />

      {/* Case Header Banner */}
      <div className="border-b border-border bg-surface px-4 md:px-8 py-5">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="space-y-1">
            <div className="flex items-center gap-2 text-xs text-muted-foreground">
              <Link href={`/${locale}/cases`} className="hover:text-foreground inline-flex items-center gap-1 font-semibold">
                <ArrowLeft className="w-3.5 h-3.5" />
                <span>{isBangla ? 'কেস তালিকা' : 'My Cases'}</span>
              </Link>
              <span>/</span>
              <span className="font-mono text-[11px]">#{id}</span>
              <Badge variant="brand" className="text-[10px]">
                {isBangla ? 'সক্রিয় বিরোধ' : 'Active Dispute'}
              </Badge>
            </div>
            <h1 className="text-xl md:text-2xl font-bold tracking-tight text-foreground">
              {isBangla
                ? 'অনলাইন কেনাকাটা: টাকা পরিশোধ সত্ত্বেও পণ্য নিখোঁজ'
                : 'Prepaid purchase, non-delivery with ৳5,500 mismatch'}
            </h1>
          </div>

          <div className="flex items-center gap-3">
            <Link
              href={`/${locale}/cases/${id}/review`}
              className="inline-flex items-center gap-1.5 text-xs font-semibold px-3 py-1.5 rounded-[var(--radius-control)] border border-primary text-primary hover:bg-[var(--brand-soft)] transition-colors min-h-[38px]"
            >
              <span>{tCase('review_facts_btn')}</span>
            </Link>
          </div>
        </div>

        {/* Five Connected Case Views Navigation Tabs (Section 5.2) */}
        <div className="max-w-7xl mx-auto mt-6 flex overflow-x-auto border-b border-border/80 gap-1 sm:gap-2">
          {navTabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <Link
                key={tab.name}
                href={tab.href}
                className="inline-flex items-center gap-2 px-3.5 py-2.5 text-xs md:text-sm font-semibold border-b-2 border-transparent hover:text-foreground text-muted-foreground transition-colors shrink-0"
              >
                <Icon className="w-4 h-4 text-primary" />
                <span>{tab.name}</span>
              </Link>
            );
          })}
        </div>
      </div>

      {/* Main Workspace Body: 2/3 Main View + 1/3 Context Sidebar (Section 5.2) */}
      <div className="flex-1 max-w-7xl mx-auto w-full px-4 md:px-8 py-8 grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left 2/3: Primary Case View */}
        <main className="lg:col-span-2 space-y-6">
          {children}
        </main>

        {/* Right 1/3: Context Sidebar */}
        <aside className="space-y-6">
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-bold uppercase tracking-wider text-muted-foreground">
                {tCase('sidebar_summary')}
              </CardTitle>
            </CardHeader>
            <CardContent className="text-xs space-y-3">
              <div>
                <span className="text-muted-foreground block text-[11px]">Category:</span>
                <span className="font-semibold text-foreground">E-Commerce / Consumer Goods</span>
              </div>
              <div>
                <span className="text-muted-foreground block text-[11px]">Disputed Total:</span>
                <span className="font-semibold text-foreground">৳5,500.00 BDT</span>
              </div>
              <div>
                <span className="text-muted-foreground block text-[11px]">Dispute Date:</span>
                <span className="font-semibold text-foreground">15 October 2026</span>
              </div>
              <div>
                <span className="text-muted-foreground block text-[11px]">Seller/Merchant:</span>
                <span className="font-semibold text-foreground">Gadget Zone BD (F-Commerce Page)</span>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-bold uppercase tracking-wider text-muted-foreground">
                {tCase('sidebar_remedy')}
              </CardTitle>
            </CardHeader>
            <CardContent className="text-xs space-y-2">
              <Badge variant="brand" className="text-xs">Full Refund (৳5,500)</Badge>
              <p className="text-muted-foreground text-[11px] leading-relaxed pt-1">
                {isBangla
                  ? 'ভোক্তা অধিকার আইনের ধারা ৪৫ অনুযায়ী প্রতিশ্রুত পণ্য সরবরাহ না করার কারণে সম্পূর্ণ রিফান্ডের দাবি।'
                  : 'Claiming full reimbursement under Section 45 for unfulfilled delivery.'}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-bold uppercase tracking-wider text-muted-foreground">
                {tCase('sidebar_sources')}
              </CardTitle>
            </CardHeader>
            <CardContent className="text-xs space-y-2">
              <div className="p-2.5 rounded-md bg-elevated border border-border/80">
                <span className="font-semibold block text-foreground">DNCRP (ভোক্তা অধিকার)</span>
                <span className="text-muted-foreground text-[11px]">Act No. 26 of 2009 • s.45, s.76</span>
              </div>
            </CardContent>
          </Card>

          {/* Data Controls / Privacy link */}
          <div className="p-3 rounded-[var(--radius-control)] border border-border bg-surface text-xs text-muted-foreground flex items-center justify-between">
            <span>{isBangla ? 'ব্যক্তিগত তথ্য নিয়ন্ত্রণ' : 'Case Data Controls'}</span>
            <Link
              href={`/${locale}/settings/data`}
              className="text-red-600 hover:underline inline-flex items-center gap-1 font-medium text-[11px]"
            >
              <Trash2 className="w-3.5 h-3.5" />
              <span>{isBangla ? 'কেস মুছুন' : 'Delete Case'}</span>
            </Link>
          </div>
        </aside>
      </div>
    </div>
  );
}
