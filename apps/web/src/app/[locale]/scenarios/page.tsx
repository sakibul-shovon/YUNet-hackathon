import { getTranslations } from 'next-intl/server';
import Link from 'next/link';
import { ArrowLeft, ArrowRight, Play, Eye, Sparkles } from 'lucide-react';
import { Header } from '@/components/layout/Header';
import { Button } from '@/components/ui/Button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';

export default async function ScenariosPage({
  params,
}: {
  params: Promise<{ locale: string }>;
}) {
  const { locale } = await params;
  const tNav = await getTranslations({ locale, namespace: 'nav' });
  const tLanding = await getTranslations({ locale, namespace: 'landing' });

  const isBangla = locale === 'bn';

  const scenarios = [
    {
      id: 'sc-1',
      title: isBangla ? '১. অগ্রিম পরিশোধিত অনলাইন ফোন অর্ডার ডেলিভারি হয়নি' : '1. Prepaid Phone Non-Delivery with Amount Mismatch',
      domain: 'E-Commerce',
      inputs: isBangla ? 'বাংলা ভয়েস + বিকাশ রসিদ' : 'Bengali Voice + bKash Receipt',
      highlights: isBangla ? '৫,৫০০ বনাম ৫,০০০ টাকার অমিল ও সমাধান' : '৳5,500 vs ৳5,000 contradiction resolution',
    },
    {
      id: 'sc-2',
      title: isBangla ? '২. এমএফএস অসফল লেনদেন: ব্যালেন্স কর্তন কিন্তু মার্চেন্টে জমা হয়নি' : '2. MFS Unsuccessful Transfer & Auto-Reversal Delay',
      domain: 'Fintech / MFS',
      inputs: isBangla ? 'এসএমএস টেক্সট + অ্যাপ স্ক্রিনশট' : 'SMS Text + App Screenshot',
      highlights: isBangla ? 'বাংলাদেশ ব্যাংক পিএসডি গাইডলাইন ও এসকেলেশন' : 'Bangladesh Bank PSD guidelines escalation',
    },
    {
      id: 'sc-3',
      title: isBangla ? '৩. ফার্মেসি থেকে নকল ও মেয়াদোত্তীর্ণ ওষুধ বিক্রয়' : '3. Counterfeit & Expired Medicine Purchase',
      domain: 'Health & Safety',
      inputs: isBangla ? 'ওষুধের মেমো + মোড়কের ছবি' : 'Cash Memo + Medicine Packaging Photo',
      highlights: isBangla ? 'তাত্ক্ষণিক স্বাস্থ্য সুরক্ষা ও ডিজিডিএ নোটিশ' : 'Immediate safety guidance & DGDA report',
    },
    {
      id: 'sc-4',
      title: isBangla ? '৪. ব্রডব্যান্ড ইন্টারনেট একটানা ৫ দিন বিচ্ছিন্ন' : '4. Broadband ISP Prolonged Outage Without Credit',
      domain: 'Telecom / ISP',
      inputs: isBangla ? 'চুক্তির নথি + অভিযোগ চ্যাট' : 'ISP Agreement + Support Chat',
      highlights: isBangla ? 'বিটিআরসি ক্ষতিপূরণ বিধি ও বিল ছাড়' : 'BTRC compensatory credit clauses',
    },
    {
      id: 'sc-5',
      title: isBangla ? '৫. স্বাস্থ্য বীমা দাবি অন্যায্যভাবে প্রত্যাখ্যান' : '5. Health Insurance Legitimate Claim Denial',
      domain: 'Insurance',
      inputs: isBangla ? 'পলিসি শর্তাবলী + হাসপাতালের বিল' : 'Policy Terms + Hospital Bill PDF',
      highlights: isBangla ? 'আইডিআরএ অভিযোগ সেল উপস্থাপনা' : 'IDRA regulatory complaint preparation',
    },
    {
      id: 'sc-6',
      title: isBangla ? '৬. ই-কমার্স ওয়ারেন্টি প্রদানে অস্বীকৃতি' : '6. Electronics Laptop Warranty Repudiation',
      domain: 'Retail Warranty',
      inputs: isBangla ? 'ওয়ারেন্টি কার্ড + সার্ভিসিং ইনভয়েস' : 'Warranty Card + Service Receipt',
      highlights: isBangla ? 'ভোক্তা অধিকার আইনের সেবা বিধান' : 'CRPA warranty enforcement provisions',
    },
    {
      id: 'sc-7',
      title: isBangla ? '৭. এয়ারলাইন্স টিকিট বাতিল ও রিফান্ড বিলম্ব' : '7. Domestic Airline Flight Cancellation Delay',
      domain: 'Aviation Transport',
      inputs: isBangla ? 'ই-টিকিট + বাতিলের এসএমএস' : 'E-Ticket PDF + Cancellation SMS',
      highlights: isBangla ? 'বেসামরিক বিমান চলাচল বিধিমালা' : 'Civil Aviation consumer guidelines',
    },
    {
      id: 'sc-8',
      title: isBangla ? '৮. সরকারি ইউটিলিটি বিলিং অসঙ্গতি' : '8. Public Utility Overbilling Dispute',
      domain: 'Public GRS',
      inputs: isBangla ? 'স্মার্ট মিটার রিডিং + বিদ্যুৎ বিল' : 'Meter Photo + Electric Bill PDF',
      highlights: isBangla ? 'সরকারি অভিযোগ নিষ্পত্তি ব্যবস্থাপনা (GRS)' : 'Government Grievance Redress System',
    },
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

      <main className="flex-1 max-w-5xl mx-auto px-4 md:px-8 py-12 w-full space-y-8">
        <Link
          href={`/${locale}`}
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-muted-foreground hover:text-foreground"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>{isBangla ? 'হোমে ফিরে যান' : 'Back to home'}</span>
        </Link>

        <div>
          <Badge variant="brand" className="mb-2">Production Engine Sandbox</Badge>
          <h1 className="text-3xl md:text-4xl font-extrabold tracking-tight text-foreground">
            {isBangla ? 'আটটি বাস্তবসম্মত বিরোধ সিনারিও' : 'Eight Real-Pipeline Dispute Scenarios'}
          </h1>
          <p className="text-muted-foreground text-sm mt-1.5 max-w-2xl leading-relaxed">
            {isBangla
              ? 'প্রতিটি সিনারিও আমাদের মূল ব্যাকএন্ড ও পলিসি ইঞ্জিনের মধ্য দিয়ে পরিচালিত হয়। যেকোনো একটি সিনারিও নির্বাচন করে পরীক্ষা করুন।'
              : 'Every scenario runs through the actual production ingestion, review, and policy engine without simulated shortcuts.'}
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          {scenarios.map((sc) => (
            <Card key={sc.id} className="hover:border-primary/50 transition-colors">
              <CardHeader className="pb-2">
                <div className="flex items-center justify-between mb-1">
                  <Badge variant="brand" className="text-[10px]">{sc.domain}</Badge>
                  <span className="text-[11px] font-mono text-muted-foreground font-semibold">#{sc.id}</span>
                </div>
                <CardTitle className="text-base font-bold">{sc.title}</CardTitle>
                <CardDescription className="text-xs">{sc.inputs}</CardDescription>
              </CardHeader>
              <CardContent className="space-y-3 pt-2">
                <p className="text-xs text-muted-foreground leading-relaxed">
                  {sc.highlights}
                </p>
                <Link
                  href={`/${locale}/cases/case_demo_phone`}
                  className="inline-flex items-center gap-1.5 text-xs font-semibold text-primary hover:underline"
                >
                  <Play className="w-3.5 h-3.5" />
                  <span>{isBangla ? 'সিনারিও লোড করুন' : 'Load scenario in workspace'}</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </Link>
              </CardContent>
            </Card>
          ))}
        </div>
      </main>
    </div>
  );
}
