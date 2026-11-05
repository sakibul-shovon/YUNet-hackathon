'use client';
import { useEffect, useState, type FormEvent } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { RequestError, send, type Profile } from '@/features/workspace/data';
import { Button, ErrorPanel, Field, Glyph, Loading, Notice, words } from '@/features/workspace/ui';
import { hasStaffAccess, signedInHome, useAuthSession } from './AuthSession';
import { AgentMark } from './AgentMark';
import { JudgeAdminButton, JudgeDemoButton, rememberSession } from './SessionEntry';

export function Access({ locale, register = false, admin = false }: { locale: string; register?: boolean; admin?: boolean }) {
  const session = useAuthSession(); const router = useRouter();
  const redirect = session.profile?.logged_in && (!admin || hasStaffAccess(session.profile)) ? signedInHome(session.profile, locale) : null;
  useEffect(() => { if (redirect) router.replace(redirect); }, [redirect, router]);
  const [name, setName] = useState(''); const [email, setEmail] = useState(''); const [password, setPassword] = useState('');
  const [visible, setVisible] = useState(false); const [busy, setBusy] = useState(false); const [error, setError] = useState('');
  async function submit(event: FormEvent) {
    event.preventDefault(); setBusy(true); setError('');
    try {
      const profile = await send<Profile>(`auth/${register ? 'register' : admin ? 'admin-login' : 'login'}`, { email, password, ...(register ? { full_name: name } : {}) });
      rememberSession(profile);
      if (admin && !profile.roles.some(role => ['admin', 'reviewer', 'publisher', 'operator'].includes(role))) { setError(words(locale, 'This account does not have administrative access.', 'এই অ্যাকাউন্টে অ্যাডমিনের প্রবেশাধিকার নেই।')); return; }
      window.location.assign(signedInHome(profile, locale));
    } catch (reason) { if (admin && reason instanceof RequestError && reason.status === 403) { setError(words(locale, 'Administrative access is not permitted for this account. Use User login for your cases.', 'এই অ্যাকাউন্টে অ্যাডমিনের প্রবেশাধিকার নেই। নিজের অভিযোগের জন্য ব্যবহারকারীর লগ ইন খুলুন।')); } else setError(words(locale, register ? 'The account could not be created. Check your details or sign in if this email is already registered.' : 'We could not sign you in. Check your email and password, then try again.', register ? 'অ্যাকাউন্ট খোলা যায়নি। তথ্যগুলো মিলিয়ে দেখুন। এই ইমেইলে আগে অ্যাকাউন্ট থাকলে লগ ইন করুন।' : 'লগ ইন করা যায়নি। ইমেইল ও পাসওয়ার্ড মিলিয়ে আবার চেষ্টা করুন।')); }
    finally { setBusy(false); }
  }
  if (session.loading || redirect) return <Loading locale={locale} />;
  if (session.error) return <ErrorPanel locale={locale} retry={session.reload} />;
  return <main id="main-content" className="ag-access"><aside className="ag-access-story"><span className="ag-eyebrow">{words(locale, 'INTELLIGENCE YOU CAN FOLLOW', 'কাজের ধাপ দেখুন, ভিত্তি বুঝুন')}</span><h1>{words(locale, admin ? 'A clear process.\nAn accountable platform.' : 'Your story, understood.\nYour next step, prepared.', admin ? 'প্রতিটি পরিবর্তনের\nজবাবদিহি থাকুক।' : 'ঘটনা বুঝে নেওয়া।\nপরের ধাপের প্রস্তুতি।')}</h1><p>{words(locale, admin ? 'Review source changes, inspect platform activity, and make explicit administrative decisions.' : 'Work with an assistant that connects your records, asks the useful question, and keeps you in control.', admin ? 'সূত্রের পরিবর্তন দেখুন, কাজের ইতিহাস পর্যালোচনা করুন এবং ভেবেচিন্তে প্রশাসনিক সিদ্ধান্ত নিন।' : 'নথির সঙ্গে তথ্য মেলান, দরকারি প্রশ্নের উত্তর দিন আর নিজের সিদ্ধান্তে এগিয়ে যান।')}</p><div className="ag-access-visual"><div><AgentMark /><strong>Ebarki</strong><span>{words(locale, 'Working beside you', 'আপনার কাজে পাশে আছি')}</span></div><ol>{[[words(locale, 'Understand the situation', 'ঘটনা বোঝা'), 'check'], [words(locale, 'Connect the evidence', 'প্রমাণের সঙ্গে মেলানো'), 'check'], [words(locale, 'Prepare a useful next step', 'পরের ধাপের প্রস্তুতি'), 'arrow']].map(([label, icon], index) => <li key={label}><span>{index < 2 ? <Glyph name="check" size={13} /> : <i />}</span>{label}</li>)}</ol><div className="ag-access-artifact"><Glyph name="file" size={25} /><span>{words(locale, 'Your case. Taking shape.', 'আপনার ঘটনা, গুছিয়ে আসছে।')}</span><i /><i /></div></div><Link href={`/${locale}/privacy`}><Glyph name="shield" size={16} />{words(locale, 'Your records stay private.', 'আপনার নথি ব্যক্তিগত থাকে।')}</Link></aside>
    <section className="ag-access-form"><nav className="ag-access-options" aria-label={words(locale, 'Choose your Ebarki access', 'Ebarki-তে প্রবেশের ধরন')}><Link href={`/${locale}/login`} aria-current={!admin ? 'page' : undefined}><Glyph name="people" size={21} /><span><strong>{words(locale, 'User login', 'ব্যবহারকারীর লগ ইন')}</strong><small>{words(locale, 'Your private cases', 'নিজের অভিযোগ ও নথি')}</small></span></Link><Link href={`/${locale}/admin/login`} aria-current={admin ? 'page' : undefined}><Glyph name="shield" size={21} /><span><strong>{words(locale, 'Admin login', 'অ্যাডমিন লগ ইন')}</strong><small>{words(locale, 'Authorized staff', 'অনুমোদিত প্রশাসক')}</small></span></Link></nav><span className="ag-eyebrow">{words(locale, admin ? 'ADMINISTRATIVE ACCESS' : register ? 'YOUR OWN WORKSPACE' : 'WELCOME BACK', admin ? 'অ্যাডমিনের প্রবেশাধিকার' : register ? 'আপনার নিজের কাজের জায়গা' : 'আবার স্বাগতম')}</span><h2>{words(locale, admin ? 'Sign in to administration.' : register ? 'Create your account.' : 'Pick up where you left off.', admin ? 'অ্যাডমিন হিসেবে লগ ইন করুন।' : register ? 'অ্যাকাউন্ট খুলুন।' : 'যেখান থেকে রেখেছিলেন, শুরু করুন।')}</h2><p>{words(locale, admin ? 'Use your authorized account. Permissions are checked by the server.' : register ? 'Keep access to your cases with your email.' : 'Open your saved cases and continue working with Ebarki.', admin ? 'অনুমোদিত অ্যাকাউন্ট ব্যবহার করুন। সার্ভারেও কাজের অনুমতি পরীক্ষা করা হয়।' : register ? 'পরে অভিযোগগুলো দেখতে এই ইমেইল ব্যবহার করতে পারবেন।' : 'সংরক্ষিত অভিযোগ খুলে Ebarki-র সঙ্গে কাজ এগিয়ে নিন।')}</p>
      {admin ? (
        <div className="ag-access-judge ag-access-judge-prominent">
          <div>
            <strong>{words(locale, 'Hackathon judges & evaluators', 'হ্যাকাথন বিচারক ও মূল্যায়নকারীদের জন্য')}</strong>
            <p>{words(locale, '1-Click Judge Admin Access. Instantly explore the administrative control room, overview metrics, merchant radar, community moderation, and audit logs. No credentials required.', '১-ক্লিকে বিচারক অ্যাডমিন অ্যাক্সেস। সরাসরি অ্যাডমিন কন্ট্রোল রুম, ওভারভিউ পরিসংখ্যান, মার্চেন্ট রাডার, কমিউনিটি মডারেশন এবং অডিট লগ মূল্যায়ন করুন। কোনো পাসওয়ার্ডের প্রয়োজন নেই।')}</p>
          </div>
          <JudgeAdminButton locale={locale} primary />
        </div>
      ) : (
        <div className="ag-access-judge ag-access-judge-prominent">
          <div>
            <strong>{words(locale, 'Hackathon judges', 'হ্যাকাথনের বিচারকদের জন্য')}</strong>
            <p>{words(locale, 'One click opens an isolated fictional case. No account required. Consumer access only.', 'এক ক্লিকে আলাদা নমুনা অভিযোগ খুলুন। অ্যাকাউন্ট লাগবে না।')}</p>
            <p style={{ marginTop: '6px', fontSize: '13px' }}>
              <Link href={`/${locale}/admin/login`} style={{ color: 'var(--brand)', textDecoration: 'underline' }}>
                {words(locale, 'Need to evaluate Admin Console? Switch to Judge Admin Access →', 'অ্যাডমিন কনসোল মূল্যায়ন করতে চান? বিচারক অ্যাডমিন লগইনে যান →')}
              </Link>
            </p>
          </div>
          <JudgeDemoButton locale={locale} primary />
        </div>
      )}
      {admin && (
        <div style={{ marginTop: '14px', marginBottom: '6px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '13px', background: 'var(--canvas)', padding: '10px 14px', border: '1px solid var(--border)', borderRadius: '6px', gap: '10px', flexWrap: 'wrap' }}>
          <div>
            <span style={{ fontWeight: 500 }}>{words(locale, 'Bootstrap Admin Credentials:', 'বুটস্ট্র্যাপ অ্যাডমিন লগইন:')}&nbsp;</span>
            <code style={{ fontSize: '12px' }}>admin@claimcraft.bd</code>
          </div>
          <button
            type="button"
            className="ui-button ui-button-secondary"
            style={{ padding: '4px 10px', fontSize: '12px', minHeight: '30px' }}
            onClick={() => {
              setEmail('admin@claimcraft.bd');
              setPassword('8sUb9caTA_s1sQ-8gY0L-Z5ePB3YYlUCl7n4zLsUI9s');
            }}
          >
            {words(locale, 'Auto-fill password', 'তথ্য বসান')}
          </button>
        </div>
      )}
      {admin && session.profile?.logged_in && <Notice>{words(locale,'You are signed in as a consumer. Enter an authorized staff account to switch to administration.','আপনি ব্যবহারকারী হিসেবে লগ ইন আছেন। অ্যাডমিন খুলতে অনুমোদিত কর্মীর অ্যাকাউন্ট দিন।')} <Link href={`/${locale}/cases`}>{words(locale,'Return to my cases','আমার অভিযোগে ফিরুন')}</Link></Notice>}{error && <Notice tone="danger">{error}</Notice>}<form onSubmit={submit}>{register && <Field label={words(locale, 'Your name', 'আপনার নাম')}><input autoComplete="name" minLength={2} maxLength={255} required value={name} onChange={event => setName(event.target.value)} /></Field>}<Field label={words(locale, 'Email address', 'ইমেইল')}><input type="email" autoComplete="email" required value={email} maxLength={255} onChange={event => setEmail(event.target.value)} /></Field><Field label={words(locale, 'Password', 'পাসওয়ার্ড')} hint={register ? words(locale, 'Use at least 6 characters.', 'অন্তত ৬ অক্ষরের পাসওয়ার্ড দিন।') : undefined}><div className="ui-password"><input autoComplete={register ? 'new-password' : 'current-password'} type={visible ? 'text' : 'password'} minLength={6} maxLength={128} value={password} required onChange={event => setPassword(event.target.value)} /><button type="button" onClick={() => setVisible(!visible)} aria-label={words(locale, visible ? 'Hide password' : 'Show password', visible ? 'পাসওয়ার্ড আড়াল করুন' : 'পাসওয়ার্ড দেখুন')} aria-pressed={visible}><Glyph name="eye" size={17} /></button></div></Field><Button busy={busy} type="submit">{words(locale, register ? 'Create account' : 'Log in', register ? 'অ্যাকাউন্ট খুলুন' : 'লগ ইন করুন')}<Glyph name="arrow" size={16} /></Button></form>
      {!admin && <><p className="ag-access-switch">{words(locale, register ? 'Already registered?' : 'New to Ebarki?', register ? 'আগেই অ্যাকাউন্ট আছে?' : 'Ebarki-তে প্রথমবার?')} <Link href={`/${locale}/${register ? 'login' : 'register'}`}>{words(locale, register ? 'Log in' : 'Create an account', register ? 'লগ ইন করুন' : 'অ্যাকাউন্ট খুলুন')}</Link></p><div className="ag-access-guest"><Link className="ui-button ui-button-secondary" href={`/${locale}/cases`}>{words(locale, 'Continue as a guest', 'অ্যাকাউন্ট ছাড়াই শুরু করুন')}<Glyph name="arrow" size={16} /></Link><small>{words(locale, 'Guest cases belong to this browser session.', 'অ্যাকাউন্ট ছাড়া করা অভিযোগ এই ব্রাউজারের সেশনে থাকে।')}</small></div></>}
      <div className="ag-access-footer"><Link href={`/${locale}/${admin ? 'login' : 'admin/login'}`}>{words(locale, admin ? 'Consumer login' : 'Admin login', admin ? 'ব্যবহারকারীর লগ ইন' : 'Admin login')}</Link><Link href={`/${locale}/help`}>{words(locale, 'Need help?', 'সহায়তা দরকার?')}</Link></div>
    </section></main>;
}
