import { getTranslations } from 'next-intl/server';
import { cookies } from 'next/headers';
import Link from 'next/link';
import { Plus, ArrowRight, FolderOpen } from 'lucide-react';
import { Header } from '@/components/layout/Header';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { CaseOut } from '@claimcraft/contracts';

const BACKEND_API_URL = process.env.BACKEND_API_URL || 'http://127.0.0.1:8000';

async function fetchCases(): Promise<CaseOut[]> {
  try {
    const cookieStore = await cookies();
    const sessionCookie = cookieStore.get('cc_session');
    const headers: Record<string, string> = {};
    if (sessionCookie) {
      headers['Cookie'] = `cc_session=${sessionCookie.value}`;
    }

    const res = await fetch(`${BACKEND_API_URL}/v1/cases?limit=20`, {
      cache: 'no-store',
      headers,
    });
    if (res.ok) {
      const data = await res.json();
      return data.items || [];
    }
  } catch {
    // Offline or server component without bearer header
  }
  return [];
}

export default async function CasesListPage({
  params,
}: {
  params: Promise<{ locale: string }>;
}) {
  const { locale } = await params;
  const t = await getTranslations({ locale, namespace: 'cases' });
  const tNav = await getTranslations({ locale, namespace: 'nav' });

  const isBangla = locale === 'bn';
  const cases = await fetchCases();

  return (
    <div className="min-h-screen flex flex-col bg-canvas text-foreground">
      <Header
        locale={locale}
        labels={{
          home: tNav('home'),
          scenarios: tNav('scenarios'),
          cases: t('title'),
          startCase: t('new_case'),
        }}
      />

      <main className="flex-1 max-w-4xl mx-auto px-4 md:px-8 py-10 w-full space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-3xl font-extrabold tracking-tight text-foreground">{t('title')}</h1>
            <p className="text-xs md:text-sm text-muted-foreground mt-1">{t('subtitle')}</p>
          </div>
          <Link
            href={`/${locale}/cases/new`}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-[var(--radius-control)] bg-primary text-primary-foreground font-semibold text-xs hover:opacity-90"
          >
            <Plus className="w-4 h-4" />
            <span>{t('new_case')}</span>
          </Link>
        </div>

        {/* Dynamic & Demo Cases */}
        <div className="space-y-4">
          {cases.map((c) => (
            <Link key={c.id} href={`/${locale}/cases/${c.id}`} className="block group">
              <Card className="hover:border-primary/50 transition-colors">
                <CardHeader className="flex flex-row items-start justify-between pb-2">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-xs font-bold text-muted-foreground">
                        {c.display_reference}
                      </span>
                      <Badge variant="brand">{c.lifecycle_status}</Badge>
                    </div>
                    <CardTitle className="text-base font-bold group-hover:text-primary transition-colors">
                      {c.title}
                    </CardTitle>
                  </div>
                  <ArrowRight className="w-4 h-4 text-muted-foreground group-hover:text-primary group-hover:translate-x-1 transition-all" />
                </CardHeader>
                <CardContent className="pt-2 text-xs text-muted-foreground flex items-center justify-between">
                  <span>{String(c.merchant_name || 'Retail Seller')} • {String(c.jurisdiction || 'BD')}</span>
                  <span>{new Date(c.created_at).toLocaleDateString()}</span>
                </CardContent>
              </Card>
            </Link>
          ))}

          {/* Seed Demo Case */}
          <Link href={`/${locale}/cases/case_demo_phone`} className="block group">
            <Card className="hover:border-primary/50 transition-colors">
              <CardHeader className="flex flex-row items-start justify-between pb-2">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-xs font-bold text-muted-foreground">#case_demo_phone</span>
                    <Badge variant="brand">{t('status_open')}</Badge>
                  </div>
                  <CardTitle className="text-base font-bold group-hover:text-primary transition-colors">
                    {isBangla
                      ? 'অনলাইন কেনাকাটা: টাকা পরিশোধ সত্ত্বেও পণ্য নিখোঁজ'
                      : 'Prepaid purchase, non-delivery with ৳5,500 mismatch'}
                  </CardTitle>
                </div>
                <ArrowRight className="w-4 h-4 text-muted-foreground group-hover:text-primary group-hover:translate-x-1 transition-all" />
              </CardHeader>
              <CardContent className="pt-2 text-xs text-muted-foreground flex items-center justify-between">
                <span>E-Commerce • Gadget Zone BD • ৳5,500 BDT</span>
                <span>15 Oct 2026</span>
              </CardContent>
            </Card>
          </Link>
        </div>
      </main>
    </div>
  );
}
