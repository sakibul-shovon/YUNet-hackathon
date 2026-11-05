'use client';
import { createContext, useCallback, useContext, useEffect, useRef, useState, type ReactNode } from 'react';
import { useRouter } from 'next/navigation';
import { invalidateSessionRequests, logoutClientSession, SESSION_EVENT, SESSION_STORAGE_EVENT } from '@/lib/api';
import { request, type Profile } from '@/features/workspace/data';

export function hasStaffAccess(profile: Profile | null) {
  return Boolean(profile?.logged_in && profile.roles.some(role => ['admin', 'reviewer', 'publisher', 'operator'].includes(role)));
}
export function signedInHome(profile: Profile, locale: string) {
  return `/${locale}/${hasStaffAccess(profile) ? 'admin' : 'cases'}`;
}
type AuthSession = {
  profile: Profile | null; loading: boolean; error: boolean; signingOut: boolean;
  reload: () => void; logout: () => Promise<void>;
};
const Context = createContext<AuthSession | null>(null);

export function AuthSessionProvider({ locale, children }: { locale: string; children: ReactNode }) {
  const router = useRouter();
  const [profile, setProfile] = useState<Profile | null>(null);
  const [loading, setLoading] = useState(true); const [error, setError] = useState(false);
  const [signingOut, setSigningOut] = useState(false); const requestId = useRef(0);
  const reload = useCallback(async () => {
    const current = ++requestId.current;
    setLoading(true); setError(false);
    try { const result = await request<Profile>('auth/me'); if (requestId.current === current) setProfile(result); }
    catch { if (requestId.current === current) { setProfile(null); setError(true); } }
    finally { if (requestId.current === current) setLoading(false); }
  }, []);
  useEffect(() => {
    void reload();
    const local = (event: Event) => {
      if ((event as CustomEvent).detail?.type === 'signed_out') {
        requestId.current += 1; setProfile(null); setLoading(false);
      }
    };
    const otherTab = (event: StorageEvent) => {
      if (event.key !== SESSION_STORAGE_EVENT) return;
      invalidateSessionRequests(); requestId.current += 1;
      setProfile(null); setLoading(true);
      let signedOut = false;
      try { signedOut = JSON.parse(event.newValue || '{}').type === 'signed_out'; } catch {}
      // Hard navigation clears private component state cached in the other tab.
      window.location.replace(`/${locale}/${signedOut ? 'login' : 'cases'}`);
    };
    window.addEventListener(SESSION_EVENT, local); window.addEventListener('storage', otherTab);
    return () => { requestId.current += 1; window.removeEventListener(SESSION_EVENT, local); window.removeEventListener('storage', otherTab); };
  }, [locale, reload]);
  const logout = useCallback(async () => {
    setSigningOut(true); requestId.current += 1;
    try {
      await logoutClientSession(); setProfile(null); setLoading(false);
      router.replace(`/${locale}/login`); router.refresh();
    } finally { setSigningOut(false); }
  }, [locale, router]);
  return <Context.Provider value={{ profile, loading, error, signingOut, reload, logout }}>
    <div className="ui-session-root" key={profile?.principal_id || 'anonymous'}>{children}</div>
  </Context.Provider>;
}

export function useAuthSession() {
  const session = useContext(Context);
  if (!session) throw new Error('Ebarki authentication requires AuthSessionProvider.');
  return session;
}
