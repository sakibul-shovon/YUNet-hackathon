'use client';
import { useState } from 'react';
import { send, type Profile } from '@/features/workspace/data';
import { Glyph, words } from '@/features/workspace/ui';
import { AgentMark } from './AgentMark';
import { rememberClientSession } from '@/lib/api';

export function rememberSession(profile: Profile) { rememberClientSession(profile); }
export function JudgeDemoButton({ locale, primary = false, view }: { locale: string; primary?: boolean; view?: 'timeline' | 'whatif' | 'reply' }) {
  const [busy, setBusy] = useState(false); const [error, setError] = useState(false);
  return <span className="ag-demo-entry"><button type="button" className={`ag-demo-button ${primary ? 'is-primary' : ''}`} onClick={async () => {
    setBusy(true); setError(false);
    try {
      const profile = await send<Profile & { demo_case_id?: string }>('auth/judge-demo');
      rememberSession(profile);
      window.location.assign(profile.demo_case_id ? `/${locale}/cases/${profile.demo_case_id}?start=1${view ? `&view=${view}` : ''}` : `/${locale}/scenarios`);
    } catch { setError(true); setBusy(false); }
  }} disabled={busy} aria-busy={busy || undefined}><AgentMark small state={busy ? 'working' : 'ready'} /><span>{words(locale, busy ? 'Opening your demo…' : 'Judge demo', busy ? 'আপনার ডেমো খোলা হচ্ছে…' : 'Judge demo')}</span>{!busy && <Glyph name="arrow" size={15} />}</button>{error && <span className="ag-entry-error" role="alert">{words(locale, 'Could not open the demo. Please try again.', 'ডেমো খোলা যায়নি। আবার চেষ্টা করুন।')}</span>}</span>;
}
export function JudgeAdminButton({ locale, primary = false }: { locale: string; primary?: boolean }) {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(false);
  return (
    <span className="ag-demo-entry">
      <button
        type="button"
        className={`ag-demo-button ${primary ? 'is-primary' : ''}`}
        onClick={async () => {
          setBusy(true);
          setError(false);
          try {
            const profile = await send<Profile>('auth/judge-admin-demo');
            rememberSession(profile);
            window.location.assign(`/${locale}/admin`);
          } catch {
            setError(true);
            setBusy(false);
          }
        }}
        disabled={busy}
        aria-busy={busy || undefined}
      >
        <AgentMark small state={busy ? 'working' : 'ready'} />
        <span>
          {words(
            locale,
            busy ? 'Opening Admin Console…' : 'Judge Admin 1-Click Access',
            busy ? 'অ্যাডমিন কনসোলে প্রবেশ করা হচ্ছে…' : 'বিচারক অ্যাডমিন ১-ক্লিক লগইন',
          )}
        </span>
        {!busy && <Glyph name="arrow" size={15} />}
      </button>
      {error && (
        <span className="ag-entry-error" role="alert">
          {words(
            locale,
            'Could not open Judge Admin session. Please try again.',
            'বিচারক অ্যাডমিন সেশন খোলা যায়নি। আবার চেষ্টা করুন।',
          )}
        </span>
      )}
    </span>
  );
}
