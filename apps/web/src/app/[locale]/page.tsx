import { getTranslations } from 'next-intl/server';
import Link from 'next/link';
import {
  ArrowRight,
  Shield,
  Sparkles,
  FileText,
  CheckCircle2,
  AlertTriangle,
  Scale,
  Lock,
  Layers,
  HelpCircle,
  Eye,
  GitCompare,
  Send,
  Database,
  Cpu,
} from 'lucide-react';
import { Header } from '@/components/layout/Header';
import { Button } from '@/components/ui/Button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';

export default async function HomePage({ params }: { params: Promise<{ locale: string }> }) {
  const { locale } = await params;
  const t = await getTranslations({ locale, namespace: 'landing' });
  const tNav = await getTranslations({ locale, namespace: 'nav' });
  const tCommon = await getTranslations({ locale, namespace: 'common' });

  const headerLabels = {
    home: tNav('home'),
    scenarios: tNav('scenarios'),
    cases: tNav('overview'),
    startCase: t('start_cta'),
  };

  return (
    <div className="min-h-screen flex flex-col bg-canvas text-foreground">
      {/* 1. Header with Event Sticker slot */}
      <Header locale={locale} labels={headerLabels} />

      {/* 2. Hero Section with Real Product Preview */}
      <section className="relative px-4 md:px-8 pt-12 pb-20 max-w-7xl mx-auto w-full flex flex-col items-center text-center">
        <div className="inline-flex items-center gap-2 px-3.5 py-1 rounded-full bg-[var(--brand-soft)] text-primary text-xs font-semibold mb-6 border border-primary/20">
          <Sparkles className="w-3.5 h-3.5" />
          <span>{t('tagline')}</span>
        </div>

        <h1 className="text-4xl sm:text-5xl md:text-6xl font-extrabold tracking-tight max-w-4xl leading-[1.15] mb-6">
          {t('hero_title')}
        </h1>

        <p className="text-base sm:text-lg md:text-xl text-muted-foreground max-w-2xl mb-10 leading-relaxed font-normal">
          {t('hero_description')}
        </p>

        {/* Two Primary CTAs */}
        <div className="flex flex-col sm:flex-row gap-4 w-full sm:w-auto justify-center mb-16">
          <Link
            href={`/${locale}/cases/new`}
            className="inline-flex items-center justify-center gap-2 px-7 py-3.5 rounded-[var(--radius-control)] bg-primary text-primary-foreground font-semibold hover:opacity-90 shadow-sm transition-all text-base min-h-[48px]"
          >
            <span>{t('start_cta')}</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
          <Link
            href={`/${locale}/scenarios`}
            className="inline-flex items-center justify-center gap-2 px-7 py-3.5 rounded-[var(--radius-control)] border border-border bg-surface font-semibold hover:bg-elevated transition-colors text-base min-h-[48px]"
          >
            <Eye className="w-4 h-4 text-muted-foreground" />
            <span>{t('scenarios_cta')}</span>
          </Link>
        </div>

        {/* Real Product Workspace Composition Preview (Section 5.2) */}
        <div className="w-full max-w-5xl rounded-[var(--radius-panel)] border border-border bg-surface shadow-md overflow-hidden text-left">
          {/* Mock Browser/Workspace Chrome */}
          <div className="bg-elevated px-4 py-2.5 border-b border-border flex items-center justify-between text-xs text-muted-foreground">
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-red-400/80 inline-block" />
              <span className="w-3 h-3 rounded-full bg-amber-400/80 inline-block" />
              <span className="w-3 h-3 rounded-full bg-emerald-400/80 inline-block" />
              <span className="ml-2 font-mono text-[11px] font-medium text-foreground">
                claimcraft.bd/cases/case_demo_phone
              </span>
            </div>
            <Badge variant="brand" className="text-[10px] py-0">
              {t('preview_badge')}
            </Badge>
          </div>

          {/* Workspace Body */}
          <div className="p-6 md:p-8 grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Left 2/3: Main Action & Timeline */}
            <div className="lg:col-span-2 space-y-6">
              {/* One Next Action Card */}
              <div className="p-5 rounded-[var(--radius-panel)] border-2 border-primary/40 bg-gradient-to-br from-surface to-[var(--brand-soft)]/20 shadow-xs">
                <div className="flex items-center justify-between mb-2">
                  <Badge variant="warning" className="text-xs">
                    {locale === 'bn' ? 'আপনার পরের কাজ' : 'One Next Step'}
                  </Badge>
                  <span className="text-xs text-muted-foreground font-mono">Case #CC-2026-081</span>
                </div>
                <h3 className="text-lg font-bold text-foreground mb-2">
                  {locale === 'bn' ? 'লেনদেনের মোট টাকা নিশ্চিত করুন' : 'Clarify payment amount mismatch'}
                </h3>
                <p className="text-xs text-muted-foreground mb-4">
                  {locale === 'bn'
                    ? 'আপনার বক্তব্যে উল্লেখ করেছেন ৫,৫০০ টাকা, কিন্তু প্রথম রসিদে ৫,০০০ টাকা রয়েছে। আরেকটি রসিদ যোগ করুন অথবা المبلغ নিশ্চিত করুন।'
                    : 'You stated ৳5,500 total, but receipt #1 shows ৳5,000. Add second ৳500 memo or adjust amount to resolve contradiction.'}
                </p>
                <div className="flex flex-wrap gap-2.5">
                  <Button size="sm" variant="primary" className="text-xs gap-1.5 min-h-[38px]">
                    <span>{locale === 'bn' ? 'দ্বিতীয় রসিদ যুক্ত করুন (+৳৫০০)' : 'Add second receipt (+৳500)'}</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </Button>
                  <Button size="sm" variant="outline" className="text-xs min-h-[38px]">
                    {locale === 'bn' ? 'বক্তব্য সংশোধন করুন' : 'Correct my amount'}
                  </Button>
                </div>
              </div>

              {/* Verified Procedural Path preview */}
              <div className="p-4 rounded-[var(--radius-control)] border border-border bg-elevated/40 space-y-2">
                <div className="flex items-center gap-2 text-xs font-semibold text-primary">
                  <Scale className="w-4 h-4" />
                  <span>{t('preview_finding')}</span>
                </div>
                <p className="text-xs text-foreground/80 leading-relaxed">
                  {t('preview_action')}
                </p>
              </div>
            </div>

            {/* Right 1/3: Context & Evidence Drawer */}
            <div className="border-t lg:border-t-0 lg:border-l border-border pt-4 lg:pt-0 lg:pl-6 space-y-4 text-xs">
              <div>
                <h4 className="font-semibold text-muted-foreground uppercase tracking-wider text-[11px] mb-2">
                  {locale === 'bn' ? 'সংযুক্ত প্রমাণাদি' : 'Attached Evidence'}
                </h4>
                <div className="space-y-2">
                  <div className="p-2.5 rounded-md border border-border bg-surface flex items-center justify-between">
                    <span className="font-mono text-[11px]">bKash_trx_9K4...png</span>
                    <Badge variant="success" className="text-[10px]">
                      {locale === 'bn' ? 'যাচাইকৃত' : 'Reviewed'}
                    </Badge>
                  </div>
                  <div className="p-2.5 rounded-md border border-dashed border-border bg-surface/50 text-muted-foreground text-center">
                    + {locale === 'bn' ? 'দ্বিতীয় প্রমাণ যোগ করুন' : 'Add secondary document'}
                  </div>
                </div>
              </div>

              <div>
                <h4 className="font-semibold text-muted-foreground uppercase tracking-wider text-[11px] mb-2">
                  {locale === 'bn' ? 'আইনি সময়সীমা' : 'Statutory Deadlines'}
                </h4>
                <div className="p-3 rounded-md bg-[var(--warning-soft)] text-[var(--warning-ink)] border border-[var(--warning-ink)]/20 leading-snug">
                  {locale === 'bn'
                    ? 'ঘটনার তারিখ থেকে ৩০ দিনের মধ্যে ভোক্তা অধিদপ্তরে অভিযোগ দায়ের করা বাধ্যতামূলক।'
                    : 'CRPA 2009 requires filing within 30 days of cause of action.'}
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 3. Scenario Gallery (Section 5.6 #3) */}
      <section className="px-4 md:px-8 py-16 bg-surface border-y border-border">
        <div className="max-w-7xl mx-auto">
          <div className="flex flex-col md:flex-row md:items-end justify-between mb-12 gap-4">
            <div>
              <h2 className="text-3xl font-bold tracking-tight text-foreground">
                {t('scenario_gallery_title')}
              </h2>
              <p className="text-muted-foreground mt-2 text-base">
                {t('scenario_gallery_sub')}
              </p>
            </div>
            <Link
              href={`/${locale}/scenarios`}
              className="inline-flex items-center gap-1.5 text-sm font-semibold text-primary hover:underline"
            >
              <span>{t('view_all_scenarios')}</span>
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Scenario 1 */}
            <Card className="hover:border-primary/50 transition-colors">
              <CardHeader>
                <div className="flex items-center justify-between mb-1">
                  <Badge variant="brand">E-Commerce</Badge>
                  <span className="text-xs text-muted-foreground font-mono">Scenario #1</span>
                </div>
                <CardTitle className="text-base font-bold">
                  {locale === 'bn' ? 'অনলাইন কেনাকাটা: টাকা পরিশোধ সত্ত্বেও পণ্য নিখোঁজ' : 'Prepaid purchase, non-delivery with ৳5,500 mismatch'}
                </CardTitle>
                <CardDescription className="text-xs">
                  {locale === 'bn' ? 'ইনপুট: বাংলা অডিও + বিকাশ স্ক্রিনশট' : 'Inputs: Bengali voice + bKash screenshot'}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-xs text-muted-foreground leading-relaxed mb-4">
                  {locale === 'bn'
                    ? 'ক্রেতা ৫,৫০০ টাকা পরিশোধের দাবি করেন, কিন্তু প্রথম রসিদ ৫,০০০ টাকার। দ্বিতীয় রসিদ যুক্ত করার পর মোট টাকা সমন্বিত হয়।'
                    : 'Customer paid ৳5,500 across two transactions. Demonstrates multi-payment resolution and DNCRP s.45 formal notice.'}
                </p>
                <Link
                  href={`/${locale}/scenarios/sc-1`}
                  className="text-xs font-semibold text-primary inline-flex items-center gap-1 hover:underline"
                >
                  <span>{locale === 'bn' ? 'সিনারিও চালান' : 'Run scenario in lab'}</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </Link>
              </CardContent>
            </Card>

            {/* Scenario 2 */}
            <Card className="hover:border-primary/50 transition-colors">
              <CardHeader>
                <div className="flex items-center justify-between mb-1">
                  <Badge variant="warning">Fintech / MFS</Badge>
                  <span className="text-xs text-muted-foreground font-mono">Scenario #2</span>
                </div>
                <CardTitle className="text-base font-bold">
                  {locale === 'bn' ? 'এমএফএস লেনদেন: ব্যালেন্স কর্তন কিন্তু মার্চেন্টে জমা হয়নি' : 'MFS failed transfer: debited but uncredited'}
                </CardTitle>
                <CardDescription className="text-xs">
                  {locale === 'bn' ? 'ইনপুট: এসএমএস টেক্সট + অ্যাপ স্ক্রিনশট' : 'Inputs: SMS text + app transaction screenshot'}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-xs text-muted-foreground leading-relaxed mb-4">
                  {locale === 'bn'
                    ? 'বাংলাদেশ ব্যাংক এনপিএসবি/এমএফএস রেজোলিউশন নির্দেশনা অনুযায়ী ব্যাংকিং কমপ্লেন এসকেলেশন প্রস্তুতকরণ।'
                    : 'Evaluates Bangladesh Bank PSD guidelines for auto-reversal and formal banking dispute escalation.'}
                </p>
                <Link
                  href={`/${locale}/scenarios/sc-2`}
                  className="text-xs font-semibold text-primary inline-flex items-center gap-1 hover:underline"
                >
                  <span>{locale === 'bn' ? 'সিনারিও চালান' : 'Run scenario in lab'}</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </Link>
              </CardContent>
            </Card>

            {/* Scenario 3 */}
            <Card className="hover:border-primary/50 transition-colors">
              <CardHeader>
                <div className="flex items-center justify-between mb-1">
                  <Badge variant="danger">Health & Safety</Badge>
                  <span className="text-xs text-muted-foreground font-mono">Scenario #3</span>
                </div>
                <CardTitle className="text-base font-bold">
                  {locale === 'bn' ? 'ভেজাল বা নকল ওষুধ ক্রয়: জরুরি প্রতিরোধ ও অভিযোগ' : 'Counterfeit medicine purchased at local pharmacy'}
                </CardTitle>
                <CardDescription className="text-xs">
                  {locale === 'bn' ? 'ইনপুট: ওষুধের প্যাকেটের ছবি + মেমো' : 'Inputs: Packaging photo + cash memo'}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-xs text-muted-foreground leading-relaxed mb-4">
                  {locale === 'bn'
                    ? 'তাত্ক্ষণিক স্বাস্থ্য সুরক্ষা নির্দেশনা, ওষুধ প্রশাসন অধিদপ্তরে তথ্য প্রেরণ এবং ভোক্তা আইনে দ্রুত ব্যবস্থা।'
                    : 'Prioritizes immediate safety guidance, evidence preservation, and fast-track DGDA/DNCRP filing.'}
                </p>
                <Link
                  href={`/${locale}/scenarios/sc-3`}
                  className="text-xs font-semibold text-primary inline-flex items-center gap-1 hover:underline"
                >
                  <span>{locale === 'bn' ? 'সিনারিও চালান' : 'Run scenario in lab'}</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </Link>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* 4. How It Works (Section 5.6 #4) */}
      <section className="px-4 md:px-8 py-20 max-w-7xl mx-auto w-full">
        <div className="text-center max-w-3xl mx-auto mb-16">
          <h2 className="text-3xl font-bold tracking-tight text-foreground">
            {t('how_it_works_title')}
          </h2>
          <p className="text-muted-foreground mt-3 text-base">
            {t('how_it_works_sub')}
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="p-6 rounded-[var(--radius-panel)] border border-border bg-surface relative">
            <div className="w-10 h-10 rounded-full bg-primary/10 text-primary font-bold flex items-center justify-center text-lg mb-4">
              1
            </div>
            <h3 className="font-bold text-base mb-2">{t('step1_title')}</h3>
            <p className="text-sm text-muted-foreground leading-relaxed">{t('step1_desc')}</p>
          </div>

          <div className="p-6 rounded-[var(--radius-panel)] border border-border bg-surface relative">
            <div className="w-10 h-10 rounded-full bg-primary/10 text-primary font-bold flex items-center justify-center text-lg mb-4">
              2
            </div>
            <h3 className="font-bold text-base mb-2">{t('step2_title')}</h3>
            <p className="text-sm text-muted-foreground leading-relaxed">{t('step2_desc')}</p>
          </div>

          <div className="p-6 rounded-[var(--radius-panel)] border border-border bg-surface relative">
            <div className="w-10 h-10 rounded-full bg-primary/10 text-primary font-bold flex items-center justify-center text-lg mb-4">
              3
            </div>
            <h3 className="font-bold text-base mb-2">{t('step3_title')}</h3>
            <p className="text-sm text-muted-foreground leading-relaxed">{t('step3_desc')}</p>
          </div>

          <div className="p-6 rounded-[var(--radius-panel)] border border-border bg-surface relative">
            <div className="w-10 h-10 rounded-full bg-primary/10 text-primary font-bold flex items-center justify-center text-lg mb-4">
              4
            </div>
            <h3 className="font-bold text-base mb-2">{t('step4_title')}</h3>
            <p className="text-sm text-muted-foreground leading-relaxed">{t('step4_desc')}</p>
          </div>
        </div>
      </section>

      {/* 5. Product Capabilities (Section 5.6 #5) */}
      <section className="px-4 md:px-8 py-16 bg-surface border-t border-border">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-3xl font-bold tracking-tight text-center mb-12">
            {t('capabilities_title')}
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="flex gap-4">
              <div className="w-10 h-10 rounded-[var(--radius-control)] bg-[var(--brand-soft)] text-primary flex items-center justify-center shrink-0">
                <FileText className="w-5 h-5" />
              </div>
              <div>
                <h3 className="font-bold text-base mb-1">{t('cap1_title')}</h3>
                <p className="text-sm text-muted-foreground leading-relaxed">{t('cap1_desc')}</p>
              </div>
            </div>

            <div className="flex gap-4">
              <div className="w-10 h-10 rounded-[var(--radius-control)] bg-[var(--brand-soft)] text-primary flex items-center justify-center shrink-0">
                <Layers className="w-5 h-5" />
              </div>
              <div>
                <h3 className="font-bold text-base mb-1">{t('cap2_title')}</h3>
                <p className="text-sm text-muted-foreground leading-relaxed">{t('cap2_desc')}</p>
              </div>
            </div>

            <div className="flex gap-4">
              <div className="w-10 h-10 rounded-[var(--radius-control)] bg-[var(--brand-soft)] text-primary flex items-center justify-center shrink-0">
                <Scale className="w-5 h-5" />
              </div>
              <div>
                <h3 className="font-bold text-base mb-1">{t('cap3_title')}</h3>
                <p className="text-sm text-muted-foreground leading-relaxed">{t('cap3_desc')}</p>
              </div>
            </div>

            <div className="flex gap-4">
              <div className="w-10 h-10 rounded-[var(--radius-control)] bg-[var(--brand-soft)] text-primary flex items-center justify-center shrink-0">
                <GitCompare className="w-5 h-5" />
              </div>
              <div>
                <h3 className="font-bold text-base mb-1">{t('cap4_title')}</h3>
                <p className="text-sm text-muted-foreground leading-relaxed">{t('cap4_desc')}</p>
              </div>
            </div>

            <div className="flex gap-4">
              <div className="w-10 h-10 rounded-[var(--radius-control)] bg-[var(--brand-soft)] text-primary flex items-center justify-center shrink-0">
                <Send className="w-5 h-5" />
              </div>
              <div>
                <h3 className="font-bold text-base mb-1">{t('cap5_title')}</h3>
                <p className="text-sm text-muted-foreground leading-relaxed">{t('cap5_desc')}</p>
              </div>
            </div>

            <div className="flex gap-4">
              <div className="w-10 h-10 rounded-[var(--radius-control)] bg-[var(--brand-soft)] text-primary flex items-center justify-center shrink-0">
                <CheckCircle2 className="w-5 h-5" />
              </div>
              <div>
                <h3 className="font-bold text-base mb-1">{t('cap6_title')}</h3>
                <p className="text-sm text-muted-foreground leading-relaxed">{t('cap6_desc')}</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 6. Trust, Privacy & Consumer Control (Section 5.6 #6) */}
      <section className="px-4 md:px-8 py-16 bg-elevated/40 border-t border-border">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-3xl font-bold tracking-tight text-center mb-12">
            {t('trust_title')}
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="p-5 rounded-[var(--radius-panel)] border border-border bg-surface">
              <Shield className="w-6 h-6 text-primary mb-3" />
              <h3 className="font-bold text-sm mb-1">{t('trust1_title')}</h3>
              <p className="text-xs text-muted-foreground leading-relaxed">{t('trust1_desc')}</p>
            </div>

            <div className="p-5 rounded-[var(--radius-panel)] border border-border bg-surface">
              <AlertTriangle className="w-6 h-6 text-amber-600 mb-3" />
              <h3 className="font-bold text-sm mb-1">{t('trust2_title')}</h3>
              <p className="text-xs text-muted-foreground leading-relaxed">{t('trust2_desc')}</p>
            </div>

            <div className="p-5 rounded-[var(--radius-panel)] border border-border bg-surface">
              <Lock className="w-6 h-6 text-primary mb-3" />
              <h3 className="font-bold text-sm mb-1">{t('trust3_title')}</h3>
              <p className="text-xs text-muted-foreground leading-relaxed">{t('trust3_desc')}</p>
            </div>

            <div className="p-5 rounded-[var(--radius-panel)] border border-border bg-surface">
              <CheckCircle2 className="w-6 h-6 text-emerald-600 mb-3" />
              <h3 className="font-bold text-sm mb-1">{t('trust4_title')}</h3>
              <p className="text-xs text-muted-foreground leading-relaxed">{t('trust4_desc')}</p>
            </div>
          </div>
        </div>
      </section>

      {/* 7. Technology Explained (Section 5.6 #7) */}
      <section className="px-4 md:px-8 py-16 bg-surface border-t border-border">
        <div className="max-w-4xl mx-auto text-center">
          <Badge variant="brand" className="mb-3">
            Deterministic + Generative
          </Badge>
          <h2 className="text-3xl font-bold tracking-tight mb-3">{t('tech_title')}</h2>
          <p className="text-muted-foreground text-sm max-w-xl mx-auto mb-8">
            {t('tech_sub')}
          </p>

          <div className="p-6 rounded-[var(--radius-panel)] border border-border bg-elevated/30 text-left grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div className="space-y-1">
              <div className="flex items-center gap-1.5 font-bold text-xs uppercase tracking-wide text-foreground">
                <Cpu className="w-4 h-4 text-primary" />
                <span>Multimodal Perception</span>
              </div>
              <p className="text-xs text-muted-foreground">
                Google Gemini 3.8 Flash + Tesseract OCR + Google Cloud STT V2
              </p>
            </div>

            <div className="space-y-1">
              <div className="flex items-center gap-1.5 font-bold text-xs uppercase tracking-wide text-foreground">
                <Database className="w-4 h-4 text-primary" />
                <span>Hybrid Retrieval</span>
              </div>
              <p className="text-xs text-muted-foreground">
                Dense E5 embeddings + Bengali BM25s lexical snapshots via RRF
              </p>
            </div>

            <div className="space-y-1">
              <div className="flex items-center gap-1.5 font-bold text-xs uppercase tracking-wide text-foreground">
                <Scale className="w-4 h-4 text-primary" />
                <span>Policy Evaluation</span>
              </div>
              <p className="text-xs text-muted-foreground">
                Three-valued AST Kleene logic engine; 100% deterministic decision traces
              </p>
            </div>
          </div>

          <Link
            href={`/${locale}/technology`}
            className="text-sm font-semibold text-primary hover:underline"
          >
            {t('see_how_built')}
          </Link>
        </div>
      </section>

      {/* 8. FAQ & Final CTA (Section 5.6 #8) */}
      <section className="px-4 md:px-8 py-16 bg-canvas border-t border-border">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl font-bold tracking-tight text-center mb-10">
            {t('faq_title')}
          </h2>

          <div className="space-y-4 mb-16">
            <div className="p-5 rounded-[var(--radius-control)] border border-border bg-surface">
              <h3 className="font-bold text-sm text-foreground mb-1.5">{t('faq1_q')}</h3>
              <p className="text-xs text-muted-foreground leading-relaxed">{t('faq1_a')}</p>
            </div>

            <div className="p-5 rounded-[var(--radius-control)] border border-border bg-surface">
              <h3 className="font-bold text-sm text-foreground mb-1.5">{t('faq2_q')}</h3>
              <p className="text-xs text-muted-foreground leading-relaxed">{t('faq2_a')}</p>
            </div>

            <div className="p-5 rounded-[var(--radius-control)] border border-border bg-surface">
              <h3 className="font-bold text-sm text-foreground mb-1.5">{t('faq3_q')}</h3>
              <p className="text-xs text-muted-foreground leading-relaxed">{t('faq3_a')}</p>
            </div>
          </div>

          {/* Final Call to Action */}
          <div className="p-8 md:p-12 rounded-[var(--radius-panel)] bg-gradient-to-br from-primary/10 via-surface to-elevated border-2 border-primary/30 text-center">
            <h3 className="text-2xl md:text-3xl font-bold text-foreground mb-2">
              {t('final_cta_title')}
            </h3>
            <p className="text-sm text-muted-foreground max-w-lg mx-auto mb-6">
              {t('final_cta_sub')}
            </p>
            <Link
              href={`/${locale}/cases/new`}
              className="inline-flex items-center gap-2 px-8 py-3.5 rounded-[var(--radius-control)] bg-primary text-primary-foreground font-semibold hover:opacity-90 shadow-sm text-sm"
            >
              <span>{t('start_cta')}</span>
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </div>
      </section>

      {/* Footer with Mandatory Links (Section 5.6) */}
      <footer className="border-t border-border bg-surface py-10 px-4 md:px-8 text-xs text-muted-foreground">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="flex flex-col items-center md:items-start gap-1">
            <div className="flex items-center gap-2 font-bold text-foreground">
              <Shield className="w-4 h-4 text-primary" />
              <span>ClaimCraft BD</span>
            </div>
            <p className="text-center md:text-left text-[11px] max-w-md">
              {tCommon('independent_notice')}
            </p>
          </div>

          <div className="flex flex-wrap items-center justify-center gap-6 font-medium">
            <Link href={`/${locale}/sources`} className="hover:text-foreground transition-colors">
              {tNav('sources')}
            </Link>
            <Link href={`/${locale}/how-it-works`} className="hover:text-foreground transition-colors">
              {tNav('howItWorks')}
            </Link>
            <Link href={`/${locale}/technology`} className="hover:text-foreground transition-colors">
              {tNav('technology')}
            </Link>
            <Link href={`/${locale}/privacy`} className="hover:text-foreground transition-colors">
              {tNav('privacy')}
            </Link>
            <Link href={`/${locale}/limitations`} className="hover:text-foreground transition-colors">
              {tNav('limitations')}
            </Link>
            <Link href={`/${locale}/help`} className="hover:text-foreground transition-colors">
              {tNav('help')}
            </Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
