import { getTranslations } from 'next-intl/server';
import Link from 'next/link';
import { ArrowLeft, HelpCircle, PhoneCall, Mail, MessageSquare } from 'lucide-react';
import { Header } from '@/components/layout/Header';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';

export default async function HelpPage({ params }: { params: Promise<{ locale: string }> }) {
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
          {isBangla ? 'সহায়তা ও সরকারি হটলাইন' : 'Help & Consumer Helplines'}
        </h1>
        <p className="text-muted-foreground text-base mb-10 leading-relaxed">
          {isBangla
            ? 'ভোক্তা বিরোধে দ্রুত যোগাযোগ ও অফিশিয়াল হটলাইন নম্বরসমূহ।'
            : 'Immediate assistance resources and direct government consumer helpline directories in Bangladesh.'}
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card>
            <CardHeader className="flex flex-row items-center gap-3">
              <PhoneCall className="w-5 h-5 text-primary" />
              <CardTitle className="text-base font-bold">
                {isBangla ? 'ভোক্তা অধিকার হটলাইন' : 'National Consumer Rights (DNCRP)'}
              </CardTitle>
            </CardHeader>
            <CardContent className="text-xs text-muted-foreground space-y-2">
              <p className="text-sm font-semibold text-foreground">হটলাইন: 16121</p>
              <p>ওয়েবসাইট: dncrp.portal.gov.bd</p>
              <p>ইমেইল: ncrp@dncrp.gov.bd</p>
              <p className="pt-2 text-[11px]">
                {isBangla
                  ? 'সরাসরি ভোক্তা অধিকারের টোল-ফ্রি জাতীয় হেল্পলাইনে কল করুন।'
                  : 'Official government helpline for shopping, pricing, and product defects.'}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center gap-3">
              <PhoneCall className="w-5 h-5 text-primary" />
              <CardTitle className="text-base font-bold">
                {isBangla ? 'বাংলাদেশ ব্যাংক কমপ্লেন সেল' : 'Bangladesh Bank Financial Complaint'}
              </CardTitle>
            </CardHeader>
            <CardContent className="text-xs text-muted-foreground space-y-2">
              <p className="text-sm font-semibold text-foreground">হটলাইন: 16236</p>
              <p>ওয়েবসাইট: bb.org.bd (Financial Integrity & Customer Services)</p>
              <p>ইমেইল: bb.cica@bb.org.bd</p>
              <p className="pt-2 text-[11px]">
                {isBangla
                  ? 'ব্যাংক, বিকাশ, নগদ বা এটিএম বিরোধের জন্য কেন্দ্রীয় ব্যাংক অভিযোগ সেল।'
                  : 'For unresolved bank, card, and MFS mobile wallet disputes.'}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center gap-3">
              <PhoneCall className="w-5 h-5 text-primary" />
              <CardTitle className="text-base font-bold">
                {isBangla ? 'বিটিআরসি টেলিযোগাযোগ অভিযোগ' : 'BTRC Telecom & Internet Complaints'}
              </CardTitle>
            </CardHeader>
            <CardContent className="text-xs text-muted-foreground space-y-2">
              <p className="text-sm font-semibold text-foreground">হটলাইন: 100</p>
              <p>ওয়েবসাইট: btrc.gov.bd</p>
              <p className="pt-2 text-[11px]">
                {isBangla
                  ? 'মোবাইল নেটওয়ার্ক, ইন্টারনেট বা আইএসপি সংক্রান্ত বিরোধের জন্য।'
                  : 'Direct regulatory oversight for mobile SIM, balance deduction, and broadband ISP issues.'}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center gap-3">
              <MessageSquare className="w-5 h-5 text-primary" />
              <CardTitle className="text-base font-bold">
                {isBangla ? 'জাতীয় জরুরি সেবা' : 'National Emergency Service'}
              </CardTitle>
            </CardHeader>
            <CardContent className="text-xs text-muted-foreground space-y-2">
              <p className="text-sm font-semibold text-foreground">হটলাইন: 999</p>
              <p className="pt-2 text-[11px]">
                {isBangla
                  ? 'মারাত্মক জালিয়াতি, শারীরিক হুমকি বা গুরুতর অপরাধের জন্য তাত্ক্ষণিক পুলিশ সহায়তা।'
                  : 'Emergency police, ambulance, and fire services in Bangladesh.'}
              </p>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
}

