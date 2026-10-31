import { getTranslations } from 'next-intl/server';
import Link from 'next/link';
import { ArrowRight, Sparkles } from 'lucide-react';

export default async function HomePage({ params }: { params: Promise<{ locale: string }> }) {
  const { locale } = await params;
  const t = await getTranslations({ locale, namespace: 'landing' });
  const tNav = await getTranslations({ locale, namespace: 'nav' });
  const tCommon = await getTranslations({ locale, namespace: 'common' });

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="border-b border-border bg-surface px-6 py-4 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 rounded bg-primary text-primary-foreground flex items-center justify-center font-bold text-lg">
            C
          </div>
          <span className="font-bold text-xl tracking-tight">ClaimCraft BD</span>
        </div>
        <nav className="flex items-center space-x-6">
          <Link href={`/${locale}/scenarios`} className="text-sm font-medium hover:text-primary transition-colors">
            {tNav('scenarios')}
          </Link>
          <Link href={`/${locale}/cases/new`} className="text-sm font-medium text-primary hover:underline">
            {t('start_cta')}
          </Link>
        </nav>
      </header>

      {/* Hero */}
      <main className="flex-1 max-w-5xl mx-auto px-6 py-16 flex flex-col items-center text-center">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-elevated text-xs font-semibold text-primary mb-6">
          <Sparkles className="w-4 h-4" />
          <span>{t('tagline')}</span>
        </div>

        <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight max-w-3xl mb-6">
          {t('hero_title')}
        </h1>

        <p className="text-lg md:text-xl text-muted-foreground max-w-2xl mb-10 leading-relaxed">
          {t('hero_description')}
        </p>

        <div className="flex flex-col sm:flex-row gap-4 w-full justify-center">
          <Link
            href={`/${locale}/cases/new`}
            className="inline-flex items-center justify-center gap-2 px-6 py-3 rounded-lg bg-primary text-primary-foreground font-semibold hover:opacity-90 transition-opacity"
          >
            <span>{t('start_cta')}</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
          <Link
            href={`/${locale}/scenarios`}
            className="inline-flex items-center justify-center px-6 py-3 rounded-lg border border-border bg-surface font-semibold hover:bg-elevated transition-colors"
          >
            {t('scenarios_cta')}
          </Link>
        </div>

        {/* 4-Step Explanation */}
        <section className="grid grid-cols-1 md:grid-cols-4 gap-6 mt-20 text-left w-full">
          <div className="p-5 rounded-xl border border-border bg-surface">
            <h3 className="font-bold text-base mb-2">{t('step1_title')}</h3>
            <p className="text-sm text-muted-foreground">{t('step1_desc')}</p>
          </div>
          <div className="p-5 rounded-xl border border-border bg-surface">
            <h3 className="font-bold text-base mb-2">{t('step2_title')}</h3>
            <p className="text-sm text-muted-foreground">{t('step2_desc')}</p>
          </div>
          <div className="p-5 rounded-xl border border-border bg-surface">
            <h3 className="font-bold text-base mb-2">{t('step3_title')}</h3>
            <p className="text-sm text-muted-foreground">{t('step3_desc')}</p>
          </div>
          <div className="p-5 rounded-xl border border-border bg-surface">
            <h3 className="font-bold text-base mb-2">{t('step4_title')}</h3>
            <p className="text-sm text-muted-foreground">{t('step4_desc')}</p>
          </div>
        </section>

        {/* Independence Disclaimer */}
        <div className="mt-16 text-xs text-muted-foreground max-w-xl">
          <p>{tCommon('independent_notice')}</p>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-border bg-surface py-6 px-6 text-center text-xs text-muted-foreground">
        © 2026 ClaimCraft BD. Built for the Bangladesh Consumer Dispute Resolution Community.
      </footer>
    </div>
  );
}
