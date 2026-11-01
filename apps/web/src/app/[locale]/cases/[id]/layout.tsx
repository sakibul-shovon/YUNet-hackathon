import { getTranslations } from 'next-intl/server';
import Link from 'next/link';
import type { ReactNode } from 'react';
import {
  FileText,
  Compass,
  CheckCircle,
  Clock,
  Layers,
} from 'lucide-react';
import { Header } from '@/components/layout/Header';
import { CaseProgressStepper } from '@/components/cases/CaseProgressStepper';
import { CaseHeaderBanner } from '@/components/cases/CaseHeaderBanner';
import { CaseContextSidebar } from '@/components/cases/CaseContextSidebar';

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

  const defaultTitle = isBangla
    ? 'ভোক্তা অধিকার বিরোধ ও প্রতিকার আবেদন'
    : 'Consumer Dispute & Resolution Claim';
  const displayRef = `CC-${id.slice(0, 6).toUpperCase()}`;

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

      {/* Case Header Banner (Hydrated Dynamically with Real Title & Reference) */}
      <CaseHeaderBanner
        caseId={id}
        locale={locale}
        initialTitle={defaultTitle}
        initialRef={displayRef}
        reviewLabel={tCase('review_facts_btn')}
      />

      {/* Five Connected Case Views Navigation Tabs (Section 5.2) */}
      <div className="border-b border-border bg-surface px-4 md:px-8">
        <div className="max-w-7xl mx-auto flex overflow-x-auto gap-1 sm:gap-2">
          {navTabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <Link
                key={tab.name}
                href={tab.href}
                className="inline-flex items-center gap-2 px-3.5 py-3 text-xs md:text-sm font-semibold border-b-2 border-transparent hover:text-foreground text-muted-foreground transition-colors shrink-0"
              >
                <Icon className="w-4 h-4 text-primary" />
                <span>{tab.name}</span>
              </Link>
            );
          })}
        </div>
      </div>

      {/* Main Workspace Body: 2/3 Main View + 1/3 Context Sidebar (Section 5.2) */}
      <div className="flex-1 max-w-7xl mx-auto w-full px-4 md:px-8 py-8">
        {/* Interactive Case Resolution Pipeline Stepper */}
        <CaseProgressStepper caseId={id} locale={locale} />

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mt-6">
          {/* Left 2/3: Primary Case View */}
          <main className="lg:col-span-2 space-y-6">
            {children}
          </main>

          {/* Right 1/3: Context Sidebar (Hydrated Dynamically with Real Merchant & Amount) */}
          <CaseContextSidebar caseId={id} locale={locale} />
        </div>
      </div>
    </div>
  );
}
