'use client';
import { useState } from 'react';
import Link from 'next/link';
import { Glyph, words } from '@/features/workspace/ui';
import { hasStaffAccess, signedInHome, useAuthSession } from './AuthSession';

export function LogoutButton({ locale, className = 'ui-button ui-button-secondary' }: { locale: string; className?: string }) {
  const session = useAuthSession(); const [failed, setFailed] = useState(false);
  if (!session.profile?.logged_in) return null;
  return <span className="ui-logout-control"><button type="button" className={className} disabled={session.signingOut} onClick={async () => {
    setFailed(false); try { await session.logout(); } catch { setFailed(true); }
  }}><Glyph name="logout" size={16} />{words(locale, session.signingOut ? 'Logging out…' : 'Log out', session.signingOut ? 'লগ আউট হচ্ছে…' : 'লগ আউট করুন')}</button>
    {failed && <span role="alert">{words(locale, 'Logout failed. You are still signed in. Try again.', 'লগ আউট হয়নি। আপনি এখনো লগ ইন আছেন। আবার চেষ্টা করুন।')}</span>}</span>;
}

export function AccountMenu({ locale }: { locale: string }) {
  const { profile, loading, error, reload } = useAuthSession();
  if (loading) return <span role="status" className="ui-small">{words(locale, 'Checking session…', 'সেশন দেখা হচ্ছে…')}</span>;
  if (error) return <button className="ui-button ui-button-quiet" onClick={reload}>{words(locale, 'Retry account', 'অ্যাকাউন্ট আবার দেখুন')}</button>;
  if (!profile?.logged_in) return <Link className="ui-button ui-button-secondary" href={`/${locale}/login`}>{words(locale, 'Log in', 'লগ ইন করুন')}</Link>;
  return <details className="ui-account-menu" onKeyDown={event => { if (event.key === 'Escape') { event.currentTarget.open = false; event.currentTarget.querySelector('summary')?.focus(); } }}>
    <summary aria-label={words(locale, 'Your account', 'আপনার অ্যাকাউন্ট')}><span className="ui-avatar">{(profile.full_name || profile.email || 'E')[0].toUpperCase()}</span><span className="ui-account-label">{words(locale, 'Account', 'অ্যাকাউন্ট')}</span></summary>
    <div className="ui-account-panel"><strong>{profile.full_name || profile.email}</strong><Link href={signedInHome(profile, locale)}>{words(locale, 'My workspace', 'আমার কাজের জায়গা')}</Link>{hasStaffAccess(profile) && <Link href={`/${locale}/admin`}>{words(locale, 'Administration', 'অ্যাডমিন')}</Link>}<Link href={`/${locale}/settings`}>{words(locale, 'Settings', 'সেটিংস')}</Link><LogoutButton locale={locale} /></div>
  </details>;
}
