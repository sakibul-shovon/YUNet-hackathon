import Link from 'next/link';
import { Shield, Sparkles } from 'lucide-react';
import { ThemeToggle } from './ThemeToggle';
import { LanguageToggle } from './LanguageToggle';

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
    <header className="border-b border-border bg-surface sticky top-0 z-40 px-4 md:px-8 py-3.5 transition-colors">
      <div className="max-w-7xl mx-auto flex items-center justify-between gap-4">
        {/* Brand & Tagline */}
        <div className="flex items-center gap-3">
          <Link href={`/${locale}`} className="flex items-center gap-2.5 group">
            <div className="w-9 h-9 rounded-[var(--radius-control)] bg-primary text-primary-foreground flex items-center justify-center font-bold text-lg shadow-xs group-hover:opacity-90 transition-opacity">
              <Shield className="w-5 h-5" />
            </div>
            <div className="flex flex-col">
              <span className="font-bold text-lg tracking-tight text-foreground leading-none">
                ClaimCraft <span className="text-primary font-extrabold">BD</span>
              </span>
              <span className="text-[10px] text-muted-foreground font-medium tracking-wide mt-0.5">
                Resolution Copilot
              </span>
            </div>
          </Link>

          {/* Official Event Sticker / Badge Slot per Section 5.2 & Section 20 */}
          <div className="hidden sm:inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-elevated border border-border/80 text-[11px] font-medium text-muted-foreground ml-3">
            <Sparkles className="w-3.5 h-3.5 text-primary" />
            <span>YU-Net AI Ignite 2026</span>
          </div>
        </div>

        {/* Navigation links & controls */}
        <div className="flex items-center gap-2 md:gap-5">
          <nav className="hidden md:flex items-center gap-5 text-sm font-medium text-muted-foreground">
            <Link href={`/${locale}/scenarios`} className="hover:text-foreground transition-colors">
              {labels.scenarios}
            </Link>
            <Link href={`/${locale}/cases`} className="hover:text-foreground transition-colors">
              {labels.cases || 'My Cases'}
            </Link>
          </nav>

          <div className="h-4 w-px bg-border hidden sm:block" />

          {/* Language & Theme Controls */}
          <LanguageToggle currentLocale={locale} />
          <ThemeToggle />

          {/* Primary CTA */}
          <Link
            href={`/${locale}/cases/new`}
            className="inline-flex items-center justify-center text-xs md:text-sm font-semibold px-4 py-2 rounded-[var(--radius-control)] bg-primary text-primary-foreground hover:opacity-90 transition-opacity min-h-[40px]"
          >
            {labels.startCase}
          </Link>
        </div>
      </div>
    </header>
  );
}

