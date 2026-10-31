'use client';

import { usePathname, useRouter } from 'next/navigation';
import { Button } from '@/components/ui/Button';

export function LanguageToggle({ currentLocale }: { currentLocale: string }) {
  const pathname = usePathname();
  const router = useRouter();

  const switchLocale = (newLocale: string) => {
    if (newLocale === currentLocale) return;

    // Replace the locale prefix in current path
    const segments = pathname.split('/');
    if (segments[1] === 'en' || segments[1] === 'bn') {
      segments[1] = newLocale;
    } else {
      segments.splice(1, 0, newLocale);
    }

    const nextPath = segments.join('/') || `/${newLocale}`;
    localStorage.setItem('claimcraft_locale', newLocale);
    router.push(nextPath);
  };

  return (
    <div className="inline-flex items-center rounded-lg border border-border p-0.5 bg-surface text-xs font-semibold">
      <button
        onClick={() => switchLocale('en')}
        className={`px-2.5 py-1 rounded-[6px] transition-colors cursor-pointer ${
          currentLocale === 'en'
            ? 'bg-primary text-primary-foreground shadow-xs'
            : 'text-muted-foreground hover:text-foreground'
        }`}
        aria-label="English"
      >
        EN
      </button>
      <button
        onClick={() => switchLocale('bn')}
        className={`px-2.5 py-1 rounded-[6px] transition-colors cursor-pointer font-bengali ${
          currentLocale === 'bn'
            ? 'bg-primary text-primary-foreground shadow-xs'
            : 'text-muted-foreground hover:text-foreground'
        }`}
        aria-label="বাংলা"
      >
        বাংলা
      </button>
    </div>
  );
}

