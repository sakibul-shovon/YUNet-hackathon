import { getTranslations } from 'next-intl/server';
import { cookies } from 'next/headers';
import { Header } from '@/components/layout/Header';
import { ConsumerDashboardClient, DashboardCase } from '@/components/dashboard/ConsumerDashboardClient';

const BACKEND_API_URL = process.env.BACKEND_API_URL || 'http://127.0.0.1:8000';

async function fetchCases(): Promise<DashboardCase[]> {
  try {
    const cookieStore = await cookies();
    const sessionCookie = cookieStore.get('cc_session');
    const tokenCookie = cookieStore.get('cc_token');
    const headers: Record<string, string> = {};
    if (sessionCookie) {
      headers['Cookie'] = `cc_session=${sessionCookie.value}`;
    }
    if (tokenCookie) {
      headers['Authorization'] = `Bearer ${tokenCookie.value}`;
    }

    const res = await fetch(`${BACKEND_API_URL}/v1/cases?limit=30`, {
      cache: 'no-store',
      headers,
    });
    if (res.ok) {
      const data = await res.json();
      const items = data.items || [];
      return items.map((c: any) => ({
        id: c.id,
        title: c.title,
        display_reference: c.display_reference,
        lifecycle_status: c.lifecycle_status,
        incident_date: c.incident_date ? String(c.incident_date) : null,
        merchant_name: c.merchant_name ? String(c.merchant_name) : null,
        story_narrative: c.story_narrative ? String(c.story_narrative) : null,
        created_at: c.created_at,
        is_demo: Boolean(c.is_demo),
      }));
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
  let cases = await fetchCases();

  // If no server cases exist yet for fresh guest, provide representative dispute
  if (cases.length === 0) {
    cases = [
      {
        id: 'case_demo_phone',
        title: isBangla
          ? 'অনলাইন গ্যাজেট শপ: অগ্রিম টাকা পরিশোধ সত্ত্বেও পণ্য নিখোঁজ'
          : 'Prepaid purchase, non-delivery with ৳3,200 mismatch',
        display_reference: '#case_demo_phone',
        lifecycle_status: 'ACTION_PREPARED',
        incident_date: '2026-10-18',
        merchant_name: 'Gadget Zone BD',
        story_narrative: isBangla
          ? 'অনলাইন পেজ থেকে অগ্রিম ৩,২০০ টাকা বিকাশে পরিশোধ করার পর পণ্য সরবরাহ করা হয়নি এবং যোগাযোগ বিচ্ছিন্ন করা হয়েছে।'
          : 'Paid BDT 3,200 in advance via bKash. Seller failed to deliver and blocked messenger communications.',
        created_at: new Date().toISOString(),
        is_demo: true,
      },
    ];
  }

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

      <main className="flex-1 max-w-5xl mx-auto px-4 sm:px-6 md:px-8 py-8 w-full">
        <ConsumerDashboardClient initialCases={cases} locale={locale} />
      </main>
    </div>
  );
}
