import React from 'react';
import { getTranslations } from 'next-intl/server';
import { Header } from '@/components/layout/Header';
import { AdminDashboardClient } from './AdminDashboardClient';

export default async function AdminPage({
  params,
}: {
  params: Promise<{ locale: string }>;
}) {
  const { locale } = await params;
  const tNav = await getTranslations({ locale, namespace: 'nav' });

  return (
    <div className="min-h-screen flex flex-col bg-background text-foreground transition-colors">
      <Header
        locale={locale}
        labels={{
          home: tNav('home'),
          scenarios: tNav('scenarios'),
          cases: tNav('myCases'),
          startCase: locale === 'bn' ? 'কেস শুরু করুন' : 'Start Your Case',
        }}
      />
      <main className="flex-1 pb-16">
        <AdminDashboardClient locale={locale} />
      </main>
    </div>
  );
}
