import { getTranslations } from 'next-intl/server';
import Link from 'next/link';
import { ArrowLeft, Sparkles, Shield, Info, CheckCircle2 } from 'lucide-react';
import { Header } from '@/components/layout/Header';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { ScenarioLauncher } from '@/components/scenarios/ScenarioLauncher';

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
      id: 'scenario_a',
      letter: 'A',
      isFeatured: true,
      title: isBangla ? '১. অগ্রিম পরিশোধিত অনলাইন ফোন অর্ডার ডেলিভারি হয়নি' : 'A: Prepaid Phone Non-Delivery with Amount Mismatch',
      domain: 'E-Commerce',
      inputs: isBangla ? 'বাংলা বিবরণ + বিকাশ পেমেন্ট রসিদ' : 'Bangla Story + bKash Receipt Image',
      highlights: isBangla
        ? 'বহু-পেমেন্ট অসঙ্গতি সমাধান (৫৫০০ বনাম ৫০০০ টাকা), প্রমাণ ট্র্যাকিং এবং ধারা ৪৫ অনুযায়ী প্রস্তুতকৃত নোটিশ।'
        : 'Multi-payment discrepancy (৳5,500 narration vs ৳5,000 receipt), provenance, and prepared consumer request.',
      differentiator: isBangla ? 'মার্চেন্ট বনাম পেমেন্ট প্রোভাইডার বিরোধ পৃথকীকরণ (টি১৯)' : 'T19 merchant vs payment provider fault separation',
    },
    {
      id: 'scenario_b',
      letter: 'B',
      isFeatured: true,
      title: isBangla ? '২. এমএফএস অসফল লেনদেন: ব্যালেন্স কর্তন কিন্তু মার্চেন্টে জমা হয়নি' : 'B: Debit Without Credit / MFS Failed Transfer',
      domain: 'Fintech / MFS',
      inputs: isBangla ? 'ভয়েস অডিও + অ্যাপ স্ক্রিনশট' : 'Voice Note + App Screenshot',
      highlights: isBangla
        ? 'ভয়েস-টু-কেস পার্সিং, দুই ধাপের অভিযোগ শৃঙ্খলা (ধাপ ১ প্রোভাইডার নোটিশ -> ধাপ ২ বাংলাদেশ ব্যাংক সিআইপিসি)।'
        : 'Voice-to-case, provider-service distinction, two-stage complaint channel (T20) and reassessment.',
      differentiator: isBangla ? 'বাধ্যতামূলক ধাপ ১ প্রোভাইডার গ্রিভেন্স (টি২০)' : 'Mandatory Stage 1 provider grievance (T20)',
    },
    {
      id: 'scenario_c',
      letter: 'C',
      isFeatured: false,
      title: isBangla ? '৩. ত্রুটিপূর্ণ পণ্য ক্রয় ও ওয়ারেন্টি প্রদানে অস্বীকৃতি' : 'C: Defective Purchase & Repudiated Return',
      domain: 'Retail Goods',
      inputs: isBangla ? 'ইংরেজি বিবরণ + রিটার্ন পলিসি নথি' : 'English Text + Return Policy PDF',
      highlights: isBangla
        ? 'দোকানের নিজস্ব পলিসি বনাম আইনি অধিকারের পার্থক্য, বদল বা রিফান্ড আবেদন ও ধারা ৪১/৪৪ ক্ষতিপূরণ প্রস্তুতি।'
        : 'Native PDF parsing, policy-vs-law distinction, replacement/refund request, and statutory citations.',
      differentiator: isBangla ? 'ব্যক্তিগত শর্তের ওপর ভোক্তা অধিকার আইনের প্রাধান্য' : 'Statutory rights override seller invoice fine print',
    },
    {
      id: 'scenario_d',
      letter: 'D',
      isFeatured: false,
      title: isBangla ? '৪. ব্রডব্যান্ড ইন্টারনেট একটানা ৫ দিন বিচ্ছিন্ন ও বাড়তি বিল' : 'D: Telecom/ISP Prolonged Outage & Unexpected Overbilling',
      domain: 'Telecom / ISP',
      inputs: isBangla ? 'বিলের ছবি + কাস্টমার সাপোর্ট চ্যাট' : 'Bill Image + Support Chat Ticket',
      highlights: isBangla
        ? 'ইমেজ স্পষ্টকরণ, অপারেটর টিকিট ট্র্যাকিং, বিটিআরসি কোয়ালিটি অব সার্ভিস ক্ষতিপূরণ ও বিটিআরসি সেল প্রস্তুতি।'
        : 'Image clarification, provider ticket prerequisite, BTRC QoS directive credit clauses, and official escalation.',
      differentiator: isBangla ? 'বিটিআরসি ভোক্তা অভিযোগ ফরম্যাপিং ও নির্দেশনা' : 'BTRC portal field mapping and direct QoS escalation',
    },
    {
      id: 'scenario_e',
      letter: 'E',
      isFeatured: false,
      title: isBangla ? '৫. স্বাস্থ্য বীমা দাবি অন্যায্যভাবে প্রত্যাখ্যান ও বিলম্ব' : 'E: Insurance Legitimate Claim Settlement Denial',
      domain: 'Insurance',
      inputs: isBangla ? 'পলিসি শর্তাবলী + প্রত্যাখ্যান পত্র' : 'Policy Terms + Denial Letter PDF',
      highlights: isBangla
        ? 'স্ক্যান নথি পার্সিং, ৯১ দিন বিলম্বের আইনি পর্যালোচনা, আইডিআরএ গ্রাহক সুরক্ষা সেলে আবেদন ও ধাপভিত্তিক বিশ্লেষণ।'
        : 'Mixed PDF extraction, 90+ day delay analysis, conditional insurer reconsideration and IDRA cell guidance.',
      differentiator: isBangla ? 'মিথ্যা আশ্বাসের কঠোর পরিহার ও আইডিআরএ সেল' : 'Remedy-aware guidance without guaranteed payout claims',
    },
    {
      id: 'scenario_f',
      letter: 'F',
      isFeatured: false,
      title: isBangla ? '৬. জরুরি ফিশিং ও নিরাপত্তা ঝুঁকি' : 'F: Ongoing Phishing & Security Credential Hazard',
      domain: 'Safety & Security',
      inputs: isBangla ? 'সন্দেহজনক এসএমএস + ভুয়া পেমেন্ট পোর্টাল' : 'Suspicious SMS Text + Fake Portal Screenshot',
      highlights: isBangla
        ? 'জরুরি নিরাপত্তা অগ্রাধিকার, ওটিপি/পিন সংগ্রহ সম্পূর্ণ নিষিদ্ধকরণ ও হটলাইন ১৬১২১ তাৎক্ষণিক নির্দেশনা।'
        : 'Safety-first next action, strict OTP/PIN prohibition, evidence preservation, and 16121 emergency hotline.',
      differentiator: isBangla ? 'টি৩২ ইনভ্যারিয়েন্ট: জরুরি হটলাইন ওভাররাইড ও পিন সুরক্ষা' : 'T32 Invariant: Zero OTP/PIN collection & emergency override',
    },
    {
      id: 'scenario_g',
      letter: 'G',
      isFeatured: false,
      title: isBangla ? '৭. সরকারি সেবা প্রদান বিলম্ব ও সিটিজেন চার্টার লঙ্ঘন' : 'G: Public Service Grievance & Citizen Charter Delay',
      domain: 'Public GRS',
      inputs: isBangla ? 'আবেদন মেমো + সিটিজেন চার্টার নির্দেশিকা' : 'Application Memo + Citizen Charter Directive',
      highlights: isBangla
        ? 'সরকারি সেবা সনদ (সিটিজেন চার্টার) সময়সীমা লঙ্ঘন, বিভাগীয় কর্মকর্তা ও কেন্দ্রীয় জিআরএস পোর্টাল পথ।'
        : 'Secondary GRS scope, departmental GRO notice and grs.gov.bd central filing while excluding court matters.',
      differentiator: isBangla ? 'প্রশাসনিক জিআরএস ও বিচারাধীন মামলার স্পষ্ট বহিষ্কার' : 'Administrative grievance with sub-judice court exclusion',
    },
    {
      id: 'scenario_h',
      letter: 'H',
      isFeatured: true,
      title: isBangla ? '৮. চলমান কেস ট্র্যাকিং, সিদ্ধান্ত পরিবর্তন ও নিরাপত্তা প্রতিরক্ষা' : 'H: Living Case, Decision Changes & Adversarial Isolation',
      domain: 'Living Case & Audit',
      inputs: isBangla ? 'বিক্রেতার নতুন উত্তর + প্রম্পট ইনজেকশন টেক্সট' : 'New Merchant Response + Adversarial Prompt Injection',
      highlights: isBangla
        ? 'সংস্করণভিত্তিক সিদ্ধান্ত পরিবর্তন (Diff), প্রম্পট ইনজেকশন প্রতিরোধ, স্বচ্ছ প্রসেসিং লগ ও নির্ভরযোগ্য ফলো-আপ।'
        : 'Versioned decision changes (T39), prompt injection isolation (T47), source-health caution, and durable audit traces.',
      differentiator: isBangla ? 'অর্থবহ সিদ্ধান্ত পরিবর্তন (টি৩৯) ও ইনজেকশন প্রতিরোধ (টি৪৭)' : 'Semantic decision diffs & proven prompt injection defense',
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

      <main id="main-content" className="flex-1 max-w-6xl mx-auto px-4 md:px-8 py-10 w-full space-y-8">
        <Link
          href={`/${locale}`}
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-muted-foreground hover:text-foreground transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>{isBangla ? 'হোমে ফিরে যান' : 'Back to home'}</span>
        </Link>

        {/* Header and Synthetic Data Notice (Section 20.1 & T52) */}
        <div className="space-y-4">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-brand-50 dark:bg-brand-950/40 text-brand-600 dark:text-brand-400 border border-brand-200 dark:border-brand-800 text-xs font-semibold">
            <Sparkles className="w-3.5 h-3.5" />
            <span>{isBangla ? 'বিচারক স্যান্ডবক্স ও দৃশ্যপট ল্যাব' : 'Competition Judge Sandbox & Scenario Lab'}</span>
          </div>

          <h1 className="text-3xl md:text-4xl font-extrabold tracking-tight text-foreground">
            {isBangla ? 'আটটি বাস্তবসম্মত বিরোধ দৃশ্যপট' : 'Eight Real-Pipeline Dispute Scenarios'}
          </h1>

          {/* Mandatory Synthetic Data Notice */}
          <div className="p-4 rounded-xl bg-surface border border-border flex items-start gap-3 shadow-xs">
            <Info className="w-5 h-5 text-primary shrink-0 mt-0.5" />
            <div className="text-xs space-y-1">
              <span className="font-bold text-foreground">
                {isBangla ? 'সিন্থেটিক ডেটা ও আইসোলেশন নিশ্চয়তা:' : 'Notice for Judges & Evaluators:'}
              </span>
              <p className="text-muted-foreground leading-relaxed">
                {isBangla
                  ? 'প্রতিটি দৃশ্যপট বাস্তবসম্মত কৃত্রিম তথ্যের ওপর ভিত্তি করে নির্মিত। কোনো নাগরিকের ব্যক্তিগত গোপন তথ্য এখানে ব্যবহৃত হয়নি। সিনারিও চালু করলে সম্পূর্ণ পৃথক একটি লাইভ কেস তৈরি হয়; কোনো বিচারকের পরিবর্তন অন্য বিচারককে প্রভাবিত করতে পারবে না (টি৫২)।'
                  : 'All scenarios in this gallery use synthetic dispute data. No actual personal consumer records are displayed. Launching a scenario provisions an isolated private case in the real production engine. Concurrent evaluations cannot share mutations (T52).'}
              </p>
            </div>
          </div>
        </div>

        {/* Featured Quick Starts (A, B, H) */}
        <div>
          <div className="flex items-center gap-2 mb-4">
            <Shield className="w-4 h-4 text-primary" />
            <h2 className="text-sm font-bold uppercase tracking-wider text-muted-foreground">
              {isBangla ? 'নির্বাচিত কুইক স্টার্ট (৩টি প্রধান দৃশ্যপট)' : 'Featured Quick Starts (3 Core Scenarios)'}
            </h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
            {scenarios.filter(s => s.isFeatured).map(sc => (
              <Card key={sc.id} className="border-primary/40 bg-brand-50/20 dark:bg-brand-950/20 flex flex-col justify-between">
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between mb-2">
                    <Badge variant="brand" className="text-[10px]">Featured Quick Start</Badge>
                    <span className="text-xs font-mono font-bold text-primary">Scenario {sc.letter}</span>
                  </div>
                  <CardTitle className="text-base font-bold leading-snug">{sc.title}</CardTitle>
                  <CardDescription className="text-xs font-medium text-muted-foreground">{sc.inputs}</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4 pt-1">
                  <p className="text-xs text-muted-foreground leading-relaxed">
                    {sc.highlights}
                  </p>
                  <div className="pt-2 border-t border-border flex items-center justify-between">
                    <ScenarioLauncher scenarioId={sc.id} locale={locale} isBangla={isBangla} />
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* Complete 8 Scenario Coverage */}
        <div className="pt-4">
          <h2 className="text-sm font-bold uppercase tracking-wider text-muted-foreground mb-4">
            {isBangla ? 'সম্পূর্ণ আটটি দৃশ্যপটের তালিকা (ক্যাপাবিলিটি কভারেজ)' : 'Complete Capability Gallery (All 8 Scenarios)'}
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            {scenarios.map(sc => (
              <Card key={sc.id} className="hover:border-primary/50 transition-colors flex flex-col justify-between">
                <CardHeader className="pb-2">
                  <div className="flex items-center justify-between mb-1.5">
                    <Badge variant="neutral" className="text-[10px]">{sc.domain}</Badge>
                    <div className="flex items-center gap-2">
                      {sc.isFeatured && <Badge variant="brand" className="text-[9px]">Featured</Badge>}
                      <span className="text-xs font-mono font-bold text-muted-foreground">Scenario {sc.letter}</span>
                    </div>
                  </div>
                  <CardTitle className="text-base font-bold leading-snug">{sc.title}</CardTitle>
                  <CardDescription className="text-xs font-medium">{sc.inputs}</CardDescription>
                </CardHeader>
                <CardContent className="space-y-3.5 pt-1">
                  <p className="text-xs text-muted-foreground leading-relaxed">
                    {sc.highlights}
                  </p>
                  <div className="p-2.5 rounded-md bg-elevated border border-border text-[11px] text-muted-foreground flex items-center gap-2">
                    <CheckCircle2 className="w-3.5 h-3.5 text-primary shrink-0" />
                    <span>{sc.differentiator}</span>
                  </div>
                  <div className="pt-2 border-t border-border flex items-center justify-end">
                    <ScenarioLauncher scenarioId={sc.id} locale={locale} isBangla={isBangla} />
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
}
