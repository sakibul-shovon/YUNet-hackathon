'use client';

import React from 'react';
import Link from 'next/link';
import { Shield, Sparkles } from 'lucide-react';
import { ThemeToggle } from './ThemeToggle';
import { LanguageToggle } from './LanguageToggle';
import { UserNav } from './UserNav';
import { LiveAgentTelemetryTicker } from '@/components/ai/LiveAgentTelemetryTicker';

interface HeaderProps {
  locale: string;
  labels: {
    home: string;
    scenarios: string;
    cases?: string;
    howItWorks?: string;
    startCase: string;
  };
}

export function Header({ locale, labels }: HeaderProps) {
  return (
    <header className="border-b border-border bg-surface sticky top-0 z-40 transition-colors">
      {/* Primary Navigation Bar */}
      <div className="px-4 md:px-8 py-3.5">
        <div className="max-w-7xl mx-auto flex items-center justify-between gap-4">
          {/* Brand & Tagline */}
          <div className="flex items-center gap-3">
            <Link href={`/${locale}`} className="flex items-center gap-2.5 group">
              <div className="w-9 h-9 rounded-[var(--radius-control)] bg-primary text-primary-foreground flex items-center justify-center font-bold text-lg shadow-xs group-hover:opacity-90 transition-opacity">
                <Shield className="w-5 h-5" />
              </div>
              <div className="flex flex-col">
                <span className="font-bold text-lg tracking-tight text-foreground leading-none">
                  {locale === 'bn' ? (
                    <>
                      এবার কি<span className="text-primary font-black">?</span>
                    </>
                  ) : (
                    <>
                      EbarKi<span className="text-primary font-black">?</span>
                    </>
                  )}
                </span>
                <span className="text-[10px] text-muted-foreground font-medium tracking-wide mt-0.5">
                  {locale === 'bn' ? 'ভোক্তা আইনি সমাধান কোপাইলট' : 'Consumer Resolution Copilot'}
                </span>
              </div>
            </Link>

            {/* Official Event Sticker / Badge per Hackathon Rule 6 */}
            <a
              href="https://yunet-aignite26.devpost.com/"
              target="_blank"
              rel="noopener noreferrer"
              className="hidden sm:inline-flex items-center ml-2.5 transition-all hover:scale-[1.02]"
              title="Official Entry — Ostad Presents YUNet AIgnite Buildathon 2026"
            >
              <img
                src="/built-for-aignite-2026.png"
                alt="Built for Ostad Presents YUNet AIgnite Buildathon 2026"
                height={36}
                style={{ maxHeight: '36px', maxWidth: '160px', height: '36px', width: 'auto' }}
                className="h-8 md:h-9 w-auto object-contain rounded-md shadow-2xs border border-border/40 hover:border-primary/40 transition-colors"
              />
            </a>
          </div>

          {/* Navigation links & controls */}
          <div className="flex items-center gap-2 md:gap-5">
            <nav className="hidden md:flex items-center gap-4 text-xs font-semibold text-muted-foreground">
              <Link href={`/${locale}/merchants`} className="hover:text-foreground transition-colors text-[var(--danger-ink)] flex items-center gap-1 bg-[var(--danger-soft)]/50 px-2.5 py-1 rounded-lg border border-[var(--danger-ink)]/20">
                <span>{locale === 'bn' ? '🛡️ মার্চেন্ট সতর্কতা রাডার' : '🛡️ Scam Radar'}</span>
              </Link>
              <Link href={`/${locale}/community`} className="hover:text-foreground transition-colors px-2 py-1">
                <span>{locale === 'bn' ? 'কমিউনিটি ফোরাম' : 'Community'}</span>
              </Link>
              <Link href={`/${locale}/scenarios`} className="hover:text-foreground transition-colors px-2 py-1">
                {labels.scenarios}
              </Link>
              <Link
                href={`/${locale}/cases`}
                className="hover:text-foreground transition-all px-3 py-1.5 text-primary font-bold flex items-center gap-1.5 bg-primary/10 rounded-lg border border-primary/25 shadow-2xs hover:bg-primary/20"
                title={locale === 'bn' ? 'ভোক্তা অধিকার সমাধান ড্যাশবোর্ড' : 'Consumer Resolution Dashboard'}
              >
                <span>📊</span>
                <span>{locale === 'bn' ? 'ড্যাশবোর্ড' : 'Dashboard'}</span>
              </Link>
              <Link
                href={`/${locale}/admin`}
                className="hover:text-foreground transition-colors px-2 py-1 text-primary font-bold flex items-center gap-1 bg-primary/10 rounded-md border border-primary/20"
              >
                <span>{locale === 'bn' ? 'অ্যাডমিন' : 'Admin'}</span>
              </Link>
            </nav>

            <div className="h-4 w-px bg-border hidden sm:block" />

            {/* Language & Theme Controls */}
            <LanguageToggle currentLocale={locale} />
            <ThemeToggle />

            {/* User Account Login State */}
            <UserNav locale={locale} />

            {/* Primary CTA */}
            <Link
              href={`/${locale}/cases/new`}
              className="inline-flex items-center justify-center text-xs md:text-sm font-semibold px-4 py-2 rounded-[var(--radius-control)] bg-primary text-primary-foreground hover:opacity-90 transition-opacity min-h-[40px]"
            >
              {labels.startCase}
            </Link>
          </div>
        </div>
      </div>

      {/* Docked Agent Swarm Telemetry Stream */}
      <LiveAgentTelemetryTicker locale={locale} />
    </header>
  );
}
