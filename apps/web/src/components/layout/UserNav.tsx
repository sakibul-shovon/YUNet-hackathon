'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { User, LogOut, Sparkles } from 'lucide-react';
import { apiFetch } from '@/lib/api';

interface UserNavProps {
  locale: string;
}

export function UserNav({ locale }: UserNavProps) {
  const router = useRouter();
  const isBangla = locale === 'bn';
  const [user, setUser] = useState<{
    logged_in: boolean;
    email?: string;
    full_name?: string;
    is_demo_judge?: boolean;
  } | null>(null);

  useEffect(() => {
    // Check localStorage first for instant hydration
    try {
      const stored = localStorage.getItem('claimcraft_user');
      if (stored) {
        setUser(JSON.parse(stored));
      }
    } catch {
      // ignore
    }

    // Verify with backend /api/v1/auth/me
    apiFetch('/api/v1/auth/me')
      .then((res) => (res.ok ? res.json() : null))
      .then((data) => {
        if (data && data.logged_in) {
          setUser(data);
          localStorage.setItem('claimcraft_user', JSON.stringify(data));
        }
      })
      .catch(() => {
        // offline or guest
      });
  }, []);

  const handleLogout = async () => {
    try {
      await apiFetch('/api/v1/auth/logout', { method: 'POST' });
    } catch {
      // ignore
    }
    localStorage.removeItem('claimcraft_user');
    setUser(null);
    router.push(`/${locale}`);
    router.refresh();
  };

  if (!user || !user.logged_in) {
    return (
      <Link
        href={`/${locale}/login`}
        className="inline-flex items-center gap-1.5 text-xs font-bold px-3 py-1.5 rounded-[var(--radius-control)] border border-primary/40 text-primary hover:bg-primary/10 transition-colors"
      >
        <User className="w-3.5 h-3.5" />
        <span>{isBangla ? 'লগইন' : 'Sign In'}</span>
      </Link>
    );
  }

  return (
    <div className="flex items-center gap-2">
      <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-surface border border-border text-xs font-medium text-foreground">
        {user.is_demo_judge ? (
          <span className="text-emerald-500 font-bold flex items-center gap-1">
            <Sparkles className="w-3.5 h-3.5" />
            <span>{isBangla ? 'বিচারক ডেমো' : 'Judge Demo'}</span>
          </span>
        ) : (
          <span className="truncate max-w-[120px] font-semibold">{user.full_name || user.email}</span>
        )}
      </div>

      <button
        onClick={handleLogout}
        title={isBangla ? 'লগআউট' : 'Sign Out'}
        className="p-1.5 rounded-lg text-muted-foreground hover:text-destructive hover:bg-destructive/10 transition-colors"
      >
        <LogOut className="w-3.5 h-3.5" />
      </button>
    </div>
  );
}

