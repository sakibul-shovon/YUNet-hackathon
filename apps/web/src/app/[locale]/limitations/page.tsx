import { getTranslations } from 'next-intl/server';
import Link from 'next/link';
import { ArrowLeft, AlertTriangle, Scale, ShieldAlert } from 'lucide-react';
import { Header } from '@/components/layout/Header';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';

export default async function LimitationsPage({ params }: { params: Promise<{ locale: string }> }) {
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
          {isBangla ? 'সীমাবদ্ধতা ও আইনি অস্বীকৃতি' : 'Product Scope & Limitations'}
        </h1>
        <p className="text-muted-foreground text-base mb-10 leading-relaxed">
          {isBangla
            ? 'ক্লেইমক্রাফট বিডি ব্যবহারের ক্ষেত্রে যা জানা অপরিহার্য।'
            : 'Essential boundaries and non-negotiable operational commitments of ClaimCraft BD.'}
        </p>

        <div className="space-y-6">
          <Card className="border-l-4 border-l-amber-500">
            <CardHeader className="flex flex-row items-center gap-3">
              <Scale className="w-5 h-5 text-amber-600" />
              <CardTitle className="text-base font-bold">
                {isBangla ? 'আমরা কোনো আদালত বা সরকারি সংস্থা নই' : 'Independent Tool, Not a Court or Legal Representative'}
              </CardTitle>
            </CardHeader>
            <CardContent className="text-sm text-muted-foreground leading-relaxed">
              {isBangla
                ? 'ক্লেইমক্রাফট বিডি একটি নিরপেক্ষ ডিজিটাল অ্যাসিস্ট্যান্ট। এটি ভোক্তা অধিকার অধিদপ্তর বা বাংলাদেশ ব্যাংকের প্রতিনিধি নয়। এটি কোনো বাধ্যতামূলক আইনি রায় বা আদেশ প্রদান করে না।'
                : 'ClaimCraft BD is an independent consumer dispute preparation copilot. It is not affiliated with the Directorate of National Consumer Rights Protection (DNCRP), Bangladesh Bank, or any judicial body. It does not provide licensed legal representation or adjudicate disputes.'}
            </CardContent>
          </Card>

          <Card className="border-l-4 border-l-amber-500">
            <CardHeader className="flex flex-row items-center gap-3">
              <AlertTriangle className="w-5 h-5 text-amber-600" />
              <CardTitle className="text-base font-bold">
                {isBangla ? 'রিফান্ডের নিশ্চয়তা নেই' : 'No Guaranteed Financial Recovery'}
              </CardTitle>
            </CardHeader>
            <CardContent className="text-sm text-muted-foreground leading-relaxed">
              {isBangla
                ? 'আমাদের কাজ হলো আপনার প্রমাণ ও দাবিকে সুসংগঠিত করা। কোনো নির্দিষ্ট বিক্রেতা বা মার্চেন্ট টাকা ফেরত দেবে কি না, তা সংশ্লিষ্ট সরকারি সংস্থা বা আদালতের সিদ্ধান্তের ওপর নির্ভরশীল।'
                : 'Our engine structures facts and cites applicable regulations to maximize your procedural readiness. We never guarantee refunds, compensation amounts, or specific merchant concessions.'}
            </CardContent>
          </Card>

          <Card className="border-l-4 border-l-amber-500">
            <CardHeader className="flex flex-row items-center gap-3">
              <ShieldAlert className="w-5 h-5 text-amber-600" />
              <CardTitle className="text-base font-bold">
                {isBangla ? 'স্বয়ংক্রিয় ফাইলিং নয়' : 'User-Controlled Submission'}
              </CardTitle>
            </CardHeader>
            <CardContent className="text-sm text-muted-foreground leading-relaxed">
              {isBangla
                ? 'ক্লেইমক্রাফট বিডি আপনার অজান্তে স্বয়ংক্রিয়ভাবে সরকারি পোর্টালে কোনো অভিযোগ জমা দেয় না। আপনি নিজে প্রস্তুতকৃত নথি পর্যালোচনা করবেন এবং নিজের পছন্দে পোর্টাল বা ইমেইলে জমা দেবেন।'
                : 'We prepare compliant complaint packages and pre-fill portal fields, but you retain sole authority to submit your dispute to regulatory authorities.'}
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
}

