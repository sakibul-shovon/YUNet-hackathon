import React from 'react';
import { getTranslations } from 'next-intl/server';
import { Header } from '@/components/layout/Header';
import { CommunityClient } from '@/components/community/CommunityClient';

export default async function CommunityForumPage({
  params,
}: {
  params: Promise<{ locale: string }>;
}) {
  const { locale } = await params;
  const tNav = await getTranslations({ locale, namespace: 'nav' });
  const tLanding = await getTranslations({ locale, namespace: 'landing' });

  // Fetch initial community posts from backend
  const backendUrl = process.env.BACKEND_API_URL || 'http://127.0.0.1:8000';
  let initialPosts = [];

  try {
    const res = await fetch(`${backendUrl}/api/v1/community/posts`, { cache: 'no-store' });
    if (res.ok) {
      initialPosts = await res.json();
    }
  } catch {
    // fallback
  }

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

      <main className="flex-1 max-w-5xl mx-auto w-full px-4 md:px-8 py-10">
        <CommunityClient initialPosts={initialPosts} locale={locale} />
      </main>
    </div>
  );
}

