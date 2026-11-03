import { NextIntlClientProvider } from 'next-intl';
import { getMessages, setRequestLocale } from 'next-intl/server';
import { notFound } from 'next/navigation';
import { locales } from '@/lib/i18n/config';
import type { ReactNode } from 'react';
import '@/app/globals.css';
import { AppShell } from '@/features/workspace/AppShell';
import { JudgeQuickStartDrawer } from '@/components/ai/JudgeQuickStartDrawer';
import '@/features/workspace/workspace.css';
import '@/features/workspace/sections.css';

export function generateStaticParams() {
  return locales.map((locale) => ({ locale }));
}

export default async function LocaleLayout({
  children,
  params,
}: {
  children: ReactNode;
  params: Promise<{ locale: string }>;
}) {
  const { locale } = await params;

  if (!locales.includes(locale as any)) {
    notFound();
  }

  setRequestLocale(locale);
  const messages = await getMessages();

  return (
    <html lang={locale} className="light" suppressHydrationWarning>
      <head>
        <script dangerouslySetInnerHTML={{ __html: `(function(){try{var p=localStorage.getItem('ebarki_theme');var d=p==='dark'||(p==='system'&&matchMedia('(prefers-color-scheme: dark)').matches);document.documentElement.classList.toggle('dark',d);document.documentElement.classList.toggle('light',!d);document.documentElement.style.colorScheme=d?'dark':'light'}catch(e){}})()` }} />
      </head>
      <body className="antialiased min-h-screen bg-canvas text-foreground">
        <a
          href="#main-content"
          className="sr-only focus:not-sr-only focus:fixed focus:top-2 focus:left-2 focus:z-50 focus:px-4 focus:py-2 focus:bg-primary focus:text-primary-foreground focus:rounded-md focus:shadow-md"
        >
          {locale === 'bn' ? 'মূল বিষয়বস্তুতে যান' : 'Skip to main content'}
        </a>
        <NextIntlClientProvider messages={messages} locale={locale}>
          <AppShell locale={locale}>{children}</AppShell>
          <JudgeQuickStartDrawer locale={locale} />
        </NextIntlClientProvider>
      </body>
    </html>
  );
}

