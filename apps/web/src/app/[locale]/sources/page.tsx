import { getTranslations } from 'next-intl/server';
import Link from 'next/link';
import { ArrowLeft, ExternalLink } from 'lucide-react';
import { Header } from '@/components/layout/Header';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { StatutorySourceDrawer } from '@/components/sources/StatutorySourceDrawer';
import { SourceHealthMonitor } from '@/components/sources/SourceHealthMonitor';

export default async function SourcesPage({ params }: { params: Promise<{ locale: string }> }) {
  const { locale } = await params;
  const t = await getTranslations({ locale, namespace: 'landing' });
  const tNav = await getTranslations({ locale, namespace: 'nav' });

  const isBangla = locale === 'bn';

  return (
    <div className="min-h-screen flex flex-col bg-canvas text-foreground">
      <Header
        locale={locale}
        labels={{
          home: tNav('home'),
          scenarios: tNav('scenarios'),
          cases: tNav('overview'),
          startCase: t('start_cta'),
        }}
      />

      <main className="flex-1 max-w-4xl mx-auto px-4 md:px-8 py-12 w-full">
        <Link
          href={`/${locale}`}
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-muted-foreground hover:text-foreground mb-6"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>{isBangla ? 'হোমে ফিরে যান' : 'Back to home'}</span>
        </Link>

        <h1 className="text-3xl md:text-4xl font-extrabold tracking-tight mb-4">
          {isBangla ? 'আইনি ও সরকারি রেফারেন্সসমূহ' : 'Official Statutory Sources & References'}
        </h1>
        <p className="text-muted-foreground text-base mb-8 leading-relaxed">
          {isBangla
            ? 'আমাদের সকল আইনি বিশ্লেষণ ও সুপারিশ বাংলাদেশ সরকারের অফিশিয়াল গেজেট ও বিধি দ্বারা সমর্থিত। কোনো মনগড়া আইনি পরামর্শ দেওয়া হয় না।'
            : 'All statutory citations in ClaimCraft BD correspond to verified official legislation and gazettes published by the Government of Bangladesh. Zero hallucinated legal advice.'}
        </p>

        {/* Live Official Watcher Monitor & Release Status */}
        <div className="mb-10">
          <SourceHealthMonitor locale={locale} />
        </div>

        {/* Interactive Statutory Citations & Exact Provisions */}
        <div className="mb-10">
          <h2 className="text-lg font-bold mb-4">
            {isBangla ? 'অনুমোদিত আইনি ধারা ও বিধানসমূহ' : 'Approved Provisions & Citations'}
          </h2>
          <StatutorySourceDrawer locale={locale} />
        </div>

        <div className="space-y-4">
          <h2 className="text-lg font-bold mb-2">
            {isBangla ? 'মূল বিধিবদ্ধ সংস্থা ও কর্তৃপক্ষ' : 'Authoritative Bodies & Official Portals'}
          </h2>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <Badge variant="brand" className="mb-1">Statute</Badge>
                <CardTitle className="text-base font-bold">
                  ভোক্তা অধিকার সংরক্ষণ আইন, ২০০৯ (Act No. 26 of 2009)
                </CardTitle>
              </div>
              <a
                href="http://bdlaws.minlaw.gov.bd/act-1014.html"
                target="_blank"
                rel="noreferrer"
                className="text-primary hover:opacity-80 p-1"
                aria-label="Open BDLaws text"
              >
                <ExternalLink className="w-4 h-4" />
              </a>
            </CardHeader>
            <CardContent className="text-xs text-muted-foreground space-y-1">
              <p>ধারা ৪৫: প্রতিশ্রুত পণ্য বা সেবা যথাযথভাবে বিক্রয় বা সরবরাহে ব্যর্থতার দণ্ড।</p>
              <p>ধারা ৬০: অভিযোগ দায়েরের তামাদি ও ঘটনার ৩০ দিনের মধ্যে প্রতিকার প্রার্থনার নিয়মাবলী।</p>
              <p>ধারা ৭৬: অভিযোগ দাখিল এবং আরোপিত জরিমানার ২৫% অর্থ অভিযোগকারীকে প্রদানের বিধান।</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <Badge variant="brand" className="mb-1">Central Bank Regulation</Badge>
                <CardTitle className="text-base font-bold">
                  বাংলাদেশ ব্যাংক গ্রাহক স্বার্থ সংরক্ষণ কেন্দ্র (CIPC Procedure & MFS 2022)
                </CardTitle>
              </div>
              <a
                href="https://bb.org.bd"
                target="_blank"
                rel="noreferrer"
                className="text-primary hover:opacity-80 p-1"
                aria-label="Open Bangladesh Bank portal"
              >
                <ExternalLink className="w-4 h-4" />
              </a>
            </CardHeader>
            <CardContent className="text-xs text-muted-foreground space-y-1">
              <p>দ্বি-স্তরীয় অভিযোগ নিষ্পত্তি ফ্রেমওয়ার্ক: স্তর ১ এ ব্যাংক বা এমএফএস প্রোভাইডারে অভিযোগ দাখিল বাধ্যতামূলক।</p>
              <p>অমীমাংসিত থাকলে বাংলাদেশ ব্যাংকের সিআইপিসি সেলে আনুষ্ঠানিক এসকেলেশন।</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <Badge variant="brand" className="mb-1">Telecom Directive</Badge>
                <CardTitle className="text-base font-bold">
                  বাংলাদেশ টেলিযোগাযোগ নিয়ন্ত্রণ কমিশন (BTRC) কনজিউমার প্রোটেকশন নির্দেশিকা
                </CardTitle>
              </div>
              <a
                href="http://btrc.gov.bd"
                target="_blank"
                rel="noreferrer"
                className="text-primary hover:opacity-80 p-1"
                aria-label="Open BTRC portal"
              >
                <ExternalLink className="w-4 h-4" />
              </a>
            </CardHeader>
            <CardContent className="text-xs text-muted-foreground space-y-1">
              <p>টেলিকম ও ব্রডব্যান্ড ইন্টারনেট গ্রাহকদের সেবা বিচ্ছিন্নতা ও প্যাকেজ সংক্রান্ত অভিযোগ নিষ্পত্তি নীতিমালা।</p>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
}
