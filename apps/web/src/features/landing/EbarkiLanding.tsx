'use client';

import { useEffect, useRef, useState, type MouseEvent, type ReactNode } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { AnimatePresence, MotionConfig, motion, useMotionValue, useReducedMotion, useSpring } from 'motion/react';
import { bangla, english, type LandingCopy } from './copy';
import { AgentShowcase } from './AgentShowcase';
import { ConnectedExperience } from './ConnectedExperience';
import { JudgeDemoButton } from '@/features/agent/SessionEntry';
import { AccountMenu } from '@/features/agent/AuthControls';
import { signedInHome, useAuthSession } from '@/features/agent/AuthSession';
import './agent-showcase.css';

type IconName = 'arrow' | 'check' | 'plus' | 'file' | 'mic' | 'link' | 'search' | 'shield' | 'clock' | 'sun' | 'moon' | 'menu' | 'close' | 'reset' | 'external' | 'chevron';

function Icon({ name, className = '' }: { name: IconName; className?: string }) {
  const paths: Record<IconName, ReactNode> = {
    arrow: <path d="M4 12h15m-6-6 6 6-6 6" />,
    check: <path d="m5 12 4 4L19 6" />,
    plus: <path d="M12 5v14M5 12h14" />,
    file: <><path d="M14 3H5v18h14V8Z" /><path d="M14 3v5h5M8 12h8M8 16h6" /></>,
    mic: <><rect x="9" y="3" width="6" height="12" rx="3" /><path d="M5 10v2a7 7 0 0 0 14 0v-2M12 19v3m-4 0h8" /></>,
    link: <><path d="m10 8 3-3a4 4 0 0 1 6 6l-3 3M14 16l-3 3a4 4 0 0 1-6-6l3-3M8 16l8-8" /></>,
    search: <><circle cx="10" cy="10" r="6" /><path d="m15 15 6 6" /></>,
    shield: <><path d="m12 3 8 3v6c0 4-8 9-8 9s-8-5-8-9V6Z" /><path d="m8 12 3 3 5-6" /></>,
    clock: <><circle cx="12" cy="12" r="9" /><path d="M12 6v6l4 2" /></>,
    sun: <><circle cx="12" cy="12" r="4" /><path d="M12 1v2m0 18v2M1 12h2m18 0h2M4 4l2 2m12 12 2 2M4 20l2-2M18 6l2-2" /></>,
    moon: <path d="M20 14A9 9 0 0 1 10 3a9 9 0 1 0 10 11Z" />,
    menu: <path d="M4 7h16M4 12h16M4 17h16" />,
    close: <path d="m6 6 12 12M6 18 18 6" />,
    reset: <><path d="M4 9a8 8 0 1 1 0 6M4 3v6h6" /></>,
    external: <><path d="M14 3h7v7m0-7L10 14M10 4H4v16h16v-6" /></>,
    chevron: <path d="m7 10 5 5 5-5" />,
  };
  return <svg className={`eb-icon ${className}`} width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">{paths[name]}</svg>;
}

function Brand({ small = false }: { small?: boolean }) {
  return <span className={`eb-brand ${small ? 'eb-brand-small' : ''}`}>
    <svg className="eb-brand-symbol" width="32" height="36" viewBox="0 0 32 36" fill="none" aria-hidden="true"><path d="M6 3h15l7 7v23H6V3Z" stroke="currentColor" strokeWidth="2" /><path d="M21 3v8h7M11 19h11m-5-5 5 5-5 5" stroke="currentColor" strokeWidth="2" strokeLinejoin="round" /></svg>
    <span>Ebarki<span className="eb-brand-period">.</span></span>
  </span>;
}

function MagneticLink({ href, children, secondary = false, className = '' }: { href: string; children: ReactNode; secondary?: boolean; className?: string }) {
  const reduced = useReducedMotion();
  const x = useMotionValue(0);
  const y = useMotionValue(0);
  const sx = useSpring(x, { stiffness: 260, damping: 22 });
  const sy = useSpring(y, { stiffness: 260, damping: 22 });
  function move(event: MouseEvent<HTMLAnchorElement>) {
    if (reduced || !window.matchMedia('(pointer: fine)').matches) return;
    const box = event.currentTarget.getBoundingClientRect();
    x.set(((event.clientX - box.left) / box.width - .5) * 6);
    y.set(((event.clientY - box.top) / box.height - .5) * 6);
  }
  return <Link href={href} className={`eb-button ${secondary ? 'eb-button-secondary' : ''} ${className}`} onMouseMove={move} onMouseLeave={() => { x.set(0); y.set(0); }}>
    <motion.span style={{ x: sx, y: sy }}>{children}<Icon name="arrow" /></motion.span>
  </Link>;
}

function Receipt({ copy, second = false, mini = false, amount }: { copy: LandingCopy; second?: boolean; mini?: boolean; amount: string }) {
  return <div className={`eb-receipt ${second ? 'eb-receipt-second' : ''} ${mini ? 'eb-receipt-mini' : ''}`}>
    <div className="eb-receipt-top"><span className="eb-receipt-mark">s.</span><span>{second ? copy.scene.receipt2 : copy.scene.receipt}<span className="eb-receipt-synthetic">SAMPLE</span></span></div>
    <strong className="eb-receipt-merchant">{copy.scene.merchant}</strong>
    <div className="eb-receipt-rule" />
    <div className="eb-receipt-row"><span>{copy.scene.transaction}</span><span>{second ? 'SAMPLE—002' : copy.scene.ref}</span></div>
    {!mini && <div className="eb-receipt-row"><span>{copy.scene.date}</span><span>{copy.scene.dateValue}</span></div>}
    <div className="eb-receipt-total"><span>{copy.scene.total}</span><strong>{amount}</strong></div>
    <div className="eb-receipt-barcode" aria-hidden="true" />
    <div className="eb-receipt-bottom">FICTIONAL TRANSACTION / DEMONSTRATION ONLY</div>
  </div>;
}

function CaseScene({ copy, receiptAdded, setReceiptAdded, money }: { copy: LandingCopy; receiptAdded: boolean; setReceiptAdded: (value: boolean) => void; money: (value: number) => string }) {
  return <div className="eb-case-scene" data-hero-art>
    <div className="eb-desk-grid" aria-hidden="true" />
    <svg className="eb-thread" viewBox="0 0 600 560" fill="none" aria-hidden="true"><path d="M76 108h385v264H335v98H85" stroke="currentColor" strokeWidth="1.5" strokeDasharray="4 5" /><circle cx="76" cy="108" r="5" fill="currentColor" /><path d="m80 466-6 4 6 4" stroke="currentColor" strokeWidth="1.5" /></svg>
    <div className="eb-desk-tab"><span className="eb-live-dot" />{copy.scene.label}<span>{copy.scene.sample}</span></div>
    <div className="eb-case-sheet">
      <div className="eb-sheet-head"><Brand small /><span className="eb-mono">CASE / 001</span></div>
      <h2>{copy.scene.title}</h2>
      <div className="eb-story-note"><span className="eb-mono">{copy.scene.storyLabel}</span><p>{copy.scene.story}</p><span className="eb-note-corner" /></div>
      <div className="eb-case-fact"><span>{copy.scene.reported}</span><strong>{money(5500)}</strong></div>
      <div className="eb-case-fact"><span>{copy.scene.documented}</span><motion.strong key={receiptAdded ? '5500' : '5000'} initial={{ opacity: .3, y: 5 }} animate={{ opacity: 1, y: 0 }}>{money(receiptAdded ? 5500 : 5000)}</motion.strong></div>
      <div className={`eb-discrepancy ${receiptAdded ? 'is-resolved' : ''}`} role="status"><span className="eb-status-symbol">{receiptAdded ? <Icon name="check" /> : '!'}</span><span>{receiptAdded ? copy.scene.match : copy.scene.mismatch}</span></div>
      <div className="eb-sheet-foot"><span className="eb-tiny-dot" />{receiptAdded ? copy.scene.review : copy.scene.warning}</div>
    </div>
    <div className="eb-floating-receipt"><Receipt copy={copy} amount={money(5000)} /></div>
    <AnimatePresence>{receiptAdded && <motion.div className="eb-floating-second" initial={{ opacity: 0, x: 24, y: 12, rotate: 10 }} animate={{ opacity: 1, x: 0, y: 0, rotate: 5 }} exit={{ opacity: 0, x: 20, y: 12 }} transition={{ duration: .35 }}><Receipt copy={copy} second mini amount={money(500)} /></motion.div>}</AnimatePresence>
    <div className="eb-scene-question">
      <div><span className="eb-question-mark">?</span><strong>{receiptAdded ? copy.scene.reviewNote : copy.scene.question}</strong></div>
      <button className={`eb-add-receipt ${receiptAdded ? 'is-added' : ''}`} onClick={() => setReceiptAdded(!receiptAdded)}><Icon name={receiptAdded ? 'reset' : 'plus'} />{receiptAdded ? copy.scene.reset : copy.scene.add}</button>
    </div>
    <span className="eb-handwritten">{copy.hero.handwritten}<svg viewBox="0 0 80 35" fill="none" aria-hidden="true"><path d="M2 6c25 23 41 28 71 14m-11-5 13 4-7 10" stroke="currentColor" strokeWidth="1.2" /></svg></span>
  </div>;
}

function FeatureArt({ index, copy, money }: { index: number; copy: LandingCopy; money: (value: number) => string }) {
  if (index === 0) return <div className="eb-voice-art" aria-hidden="true"><div className="eb-art-caption"><Icon name="mic" /><span>VOICE → STORY</span><span className="eb-tiny-dot" /></div><div className="eb-wave">{Array.from({ length: 39 }, (_, i) => <i key={i} style={{ height: `${12 + Math.abs(Math.sin(i * .72) * Math.cos(i * .24)) * 55}px` }} />)}</div><p lang="bn">{copy.toolkit.voiceText}</p><span className="eb-review-tag"><span />{copy.toolkit.voiceReview}</span></div>;
  if (index === 1) return <div className="eb-evidence-art" aria-hidden="true"><div className="eb-mini-file"><Icon name="file" /><div className="eb-mini-lines"><i /><i /><i /></div><strong>{money(5000)}</strong><span className="eb-evidence-bracket" /></div><div className="eb-link-thread"><Icon name="link" /></div><div className="eb-mini-fact"><span className="eb-mono">{copy.toolkit.fact}</span><strong>{money(5000)}</strong><span><Icon name="link" />{copy.toolkit.linked}</span></div><p>{copy.toolkit.supported}</p></div>;
  if (index === 2) return <div className="eb-paths-art" aria-hidden="true">{copy.toolkit.paths.map((name, i) => <div key={name} className={`eb-path-line eb-path-line-${i}`}><span className="eb-condition-dot">{i === 0 ? <Icon name="check" /> : i === 1 ? '—' : '?'}</span><div><strong>{name}</strong><span>{copy.toolkit.pathState[i]}</span></div><Icon name="arrow" /></div>)}</div>;
  return <div className="eb-activity-art" aria-hidden="true"><span className="eb-mono">CASE / 001</span>{copy.toolkit.activity.map((name, i) => <div key={name} className="eb-mini-event"><span className={`eb-event-dot eb-event-dot-${i}`} /><div><strong>{name}</strong><span>{copy.toolkit.activityTime[i]}</span></div>{i === 2 && <Icon name="check" />}</div>)}</div>;
}

export function EbarkiLanding({ locale }: { locale: string }) {
  const copy = locale === 'bn' ? bangla : english;
  const session = useAuthSession();
  const root = useRef<HTMLDivElement>(null);
  const [dark, setDark] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);
  const [receiptAdded, setReceiptAdded] = useState(false);
  const [step, setStep] = useState(0);
  const [copyMessage, setCopyMessage] = useState('');
  const money = (value: number) => `৳${new Intl.NumberFormat(locale === 'bn' ? 'bn-BD' : 'en-BD').format(value)}`;

  useEffect(() => {
    const sync = () => setDark(document.documentElement.classList.contains('dark'));
    sync();
    const observer = new MutationObserver(sync);
    observer.observe(document.documentElement, { attributes: true, attributeFilter: ['class'] });
    return () => observer.disconnect();
  }, []);

  useEffect(() => {
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    let disposed = false;
    let cleanup: (() => void) | undefined;
    Promise.all([import('gsap'), import('gsap/ScrollTrigger'), import('gsap/SplitText')]).then(([{ gsap }, { ScrollTrigger }, { SplitText }]) => {
      if (disposed || !root.current) return;
      gsap.registerPlugin(ScrollTrigger, SplitText);
      const context = gsap.context(() => {
        const heading = root.current?.querySelector('[data-hero-title]');
        if (heading && locale !== 'bn') {
          const split = SplitText.create(heading, { type: 'lines', autoSplit: true, onSplit(self) { return gsap.from(self.lines, { opacity: 0, y: 24, duration: .65, stagger: .1, ease: 'power3.out' }); } });
          cleanup = () => split.revert();
        } else if (heading) gsap.from(heading.children, { opacity: 0, y: 12, duration: .6, stagger: .1 });
        gsap.from('[data-hero-art]', { opacity: 0, y: 18, duration: .8, delay: .15, ease: 'power3.out' });
        gsap.utils.toArray<HTMLElement>('.eb-reveal').forEach(element => {
          gsap.from(element, { y: 20, opacity: 0, duration: .65, ease: 'power2.out', scrollTrigger: { trigger: element, start: 'top 94%', once: true } });
        });
      }, root);
      const revertSplit = cleanup;
      cleanup = () => { revertSplit?.(); context.revert(); };
    }).catch(() => { /* Content remains fully usable if optional animation fails. */ });
    return () => { disposed = true; cleanup?.(); };
  }, [locale]);

  useEffect(() => {
    if (!menuOpen) return;
    const listener = (event: KeyboardEvent) => { if (event.key === 'Escape') { setMenuOpen(false); document.getElementById('eb-menu-button')?.focus(); } };
    window.addEventListener('keydown', listener);
    return () => window.removeEventListener('keydown', listener);
  }, [menuOpen]);

  function toggleTheme() {
    const next = !dark;
    document.documentElement.classList.add('eb-theme-changing');
    document.documentElement.classList.toggle('dark', next);
    document.documentElement.classList.toggle('light', !next);
    document.documentElement.style.colorScheme = next ? 'dark' : 'light';
    try { localStorage.setItem('ebarki_theme', next ? 'dark' : 'light'); } catch { /* The current tab still changes when storage is unavailable. */ }
    setDark(next);
    window.setTimeout(() => document.documentElement.classList.remove('eb-theme-changing'), 240);
  }

  async function copyDraft() {
    const text = [copy.demo.draftTitle, copy.demo.draftGreeting, copy.demo.draftBody, receiptAdded ? copy.demo.draftResolved : copy.demo.draftUnresolved, copy.demo.draftFoot].join('\n\n');
    try { await navigator.clipboard.writeText(text); setCopyMessage(copy.demo.copied); } catch { setCopyMessage(copy.demo.copyError); }
  }

  return <MotionConfig reducedMotion="user"><div className="ebarki" ref={root} id="top">
    <header className="eb-header">
      <div className="eb-container eb-header-inner">
        <Link href={`/${locale}`} aria-label="Ebarki" className="eb-home"><Brand /></Link>
        <nav className="eb-desktop-nav" aria-label={locale === 'bn' ? 'প্রধান নেভিগেশন' : 'Main navigation'}><a href="#how-it-works">{copy.nav.how}</a><a href="#toolkit">{copy.nav.toolkit}</a><a href="#trust">{copy.nav.trust}</a></nav>
        <div className="eb-header-actions"><Link href={locale === 'bn' ? '/en' : '/bn'} className="eb-language" lang={locale === 'bn' ? 'en' : 'bn'}>{copy.nav.language}</Link><button className="eb-theme" onClick={toggleTheme} aria-label={dark ? copy.nav.light : copy.nav.theme} aria-pressed={dark}><Icon name={dark ? 'sun' : 'moon'} /></button><AccountMenu locale={locale} />{!session.profile?.logged_in && <JudgeDemoButton locale={locale} />}<button id="eb-menu-button" className="eb-menu-toggle" aria-label={menuOpen ? copy.nav.close : copy.nav.menu} aria-expanded={menuOpen} aria-controls="eb-mobile-nav" onClick={() => setMenuOpen(!menuOpen)}><Icon name={menuOpen ? 'close' : 'menu'} /></button></div>
      </div>
      {menuOpen && <nav id="eb-mobile-nav" className="eb-mobile-nav" aria-label={copy.nav.menu}><a href="#how-it-works" onClick={() => setMenuOpen(false)}>{copy.nav.how}</a><a href="#toolkit" onClick={() => setMenuOpen(false)}>{copy.nav.toolkit}</a><a href="#trust" onClick={() => setMenuOpen(false)}>{copy.nav.trust}</a><Link href={session.profile?.logged_in ? signedInHome(session.profile, locale) : `/${locale}/login`}>{session.profile?.logged_in ? (locale === 'bn' ? 'আমার কাজের জায়গা' : 'My workspace') : copy.nav.login}</Link><Link href={`/${locale}/cases/new`}>{copy.nav.start}<Icon name="arrow" /></Link></nav>}
    </header>

    <main id="main-content">
      <section className="eb-hero eb-container" aria-labelledby="eb-hero-heading">
        <div className="eb-hero-copy">
          <div className="eb-event"><a href="https://yunet-aignite26.devpost.com/" target="_blank" rel="noopener noreferrer"><Image src="/built-for-aignite-2026.png" alt="Built for Ostad Presents YUNet AIgnite Buildathon 2026" width={2105} height={747} priority sizes="172px" /></a><span>{copy.hero.event}</span></div>
          <p className="eb-eyebrow"><span className="eb-tiny-dot" />{copy.hero.eyebrow}</p>
          <h1 id="eb-hero-heading" data-hero-title aria-label={`${copy.hero.line1} ${copy.hero.line2} ${copy.hero.line3}`}><span>{copy.hero.line1}</span><span>{copy.hero.line2} <em>{copy.hero.line3}</em></span></h1>
          <p className="eb-hero-description">{copy.hero.description}</p>
          <div className="eb-hero-actions"><MagneticLink href={`/${locale}/cases/new`}>{copy.nav.start}</MagneticLink><a className="eb-text-link" href="#walkthrough"><span className="eb-play"><svg width="9" height="10" viewBox="0 0 9 10" fill="currentColor" aria-hidden="true"><path d="m1 0 8 5-8 5Z" /></svg></span>{copy.hero.sample}</a></div>
          <p className="eb-hero-note"><Icon name="shield" />{copy.hero.note}</p><div className="eb-agent-hero-entry"><JudgeDemoButton locale={locale} /><span>{locale === 'bn' ? 'English sample workspace' : 'Open your own English sample. Inspect every step.'}</span></div>
        </div>
        <div className="eb-hero-visual"><AgentShowcase locale={locale} added={receiptAdded} onAdd={setReceiptAdded} /><p className="eb-sample-caption"><span className="eb-tiny-dot" />{copy.scene.caption}</p></div>
        <div className="eb-hero-bottom"><span className="eb-mono">{copy.hero.marker}</span><a href="#how-it-works" aria-label={copy.nav.how}><Icon name="arrow" /></a><span className="eb-mono">BD / EN + বাংলা</span></div>
      </section>

      <div className="eb-principle-strip"><div className="eb-container">{copy.strip.map((text, index) => <span key={text}><span className="eb-strip-symbol">{index === 0 ? '↗' : index === 1 ? '⊞' : '↳'}</span>{text}</span>)}</div></div>

      <section id="how-it-works" className="eb-section eb-container eb-problem" aria-labelledby="eb-problem-title">
        <div className="eb-section-heading eb-reveal"><div><p className="eb-eyebrow">{copy.problem.eyebrow}</p><h2 id="eb-problem-title">{copy.problem.title}</h2></div><p>{copy.problem.description}</p></div>
        <div className="eb-process">{copy.problem.parts.map((part, i) => <article className="eb-process-item eb-reveal" key={part.title}><div className="eb-process-art" aria-hidden="true">{i === 0 ? <div className="eb-scattered"><span><Icon name="file" /></span><span><Icon name="mic" /></span><span><Icon name="file" /></span></div> : i === 1 ? <div className="eb-assembled"><span /><span /><span /><b><Icon name="check" /></b></div> : <div className="eb-forward"><span /><Icon name="arrow" /></div>}</div><span className="eb-mono">{part.label}</span><h3>{part.title}</h3><p>{part.text}</p></article>)}</div>
      </section>

      <ConnectedExperience locale={locale} />

      <section className="eb-section eb-container eb-toolkit" id="toolkit" aria-labelledby="eb-toolkit-title">
        <div className="eb-section-heading eb-reveal"><div><p className="eb-eyebrow">{copy.toolkit.eyebrow}</p><h2 id="eb-toolkit-title">{copy.toolkit.title}</h2></div><p>{copy.toolkit.intro}</p></div>
        <div className="eb-tool-grid">{copy.toolkit.items.map((item, index) => <article className={`eb-tool eb-tool-${index} eb-reveal`} key={item.title}><div className="eb-tool-visual"><FeatureArt index={index} copy={copy} money={money} /></div><div className="eb-tool-copy"><span className="eb-mono">{item.label}</span><h3>{item.title}</h3><p>{item.text}</p><Link href={index === 0 ? `/${locale}/cases/new` : index === 1 ? '#walkthrough' : index === 2 ? `/${locale}/how-it-works` : `/${locale}/scenarios`} className="eb-text-link">{item.link}<Icon name="arrow" /></Link></div></article>)}</div>
        <div className="eb-beyond eb-reveal"><h3>{copy.toolkit.moreTitle}</h3><Link href={`/${locale}/merchants`}><span className="eb-beyond-icon"><Icon name="search" /></span><div><strong>{copy.toolkit.merchantTitle}</strong><p>{copy.toolkit.merchantText}</p><span>{copy.toolkit.merchantLink}<Icon name="arrow" /></span></div></Link><Link href={`/${locale}/community`}><span className="eb-beyond-icon"><Icon name="link" /></span><div><strong>{copy.toolkit.communityTitle}</strong><p>{copy.toolkit.communityText}</p><span>{copy.toolkit.communityLink}<Icon name="arrow" /></span></div></Link></div>
      </section>

      <section className="eb-living-section"><div className="eb-container eb-living-inner"><div className="eb-reveal"><p className="eb-eyebrow">{copy.living.eyebrow}</p><h2>{copy.living.title}</h2><p>{copy.living.description}</p></div><div className="eb-living-comparison eb-reveal"><div className="eb-before"><span className="eb-mono">{copy.living.before}</span><p>{copy.living.beforeText}</p><strong>{money(5000)} <span>≠ {money(5500)}</span></strong></div><span className="eb-living-arrow"><Icon name="arrow" /></span><div className="eb-after"><span className="eb-mono">{copy.living.after}</span><p>{copy.living.afterText}</p><strong>{money(5000)} + {money(500)}<Icon name="check" /></strong></div><p className="eb-living-note"><Icon name="link" />{copy.living.note}</p></div></div></section>

      <section className="eb-section eb-container eb-trust" id="trust" aria-labelledby="eb-trust-title"><div className="eb-section-heading eb-reveal"><div><p className="eb-eyebrow">{copy.trust.eyebrow}</p><h2 id="eb-trust-title">{copy.trust.title}</h2></div><div className="eb-trust-seal" aria-hidden="true"><Icon name="shield" /><span>GROUNDED<br />BY DESIGN</span></div></div><div className="eb-trust-grid">{copy.trust.items.map((item, i) => <article className="eb-reveal" key={item.title}><span className="eb-trust-number">0{i + 1}</span><h3>{item.title}</h3><p>{item.text}</p><Link href={`/${locale}/${item.href}`} className="eb-text-link">{item.link}<Icon name="arrow" /></Link></article>)}</div><div className="eb-tech-note eb-reveal"><div><h3>{copy.trust.techTitle}</h3><p>{copy.trust.techText}</p><Link href={`/${locale}/technology`} className="eb-text-link">{copy.trust.techLink}<Icon name="arrow" /></Link></div><div className="eb-tech-flow" aria-label={copy.trust.techSteps.join(' → ')}>{copy.trust.techSteps.map((name, i) => <span key={name}><i>{i === 4 ? <Icon name="arrow" /> : `0${i + 1}`}</i>{name}</span>)}</div></div><div className="eb-privacy-note"><Icon name="shield" /><p>{copy.trust.privacy}</p><Link href={`/${locale}/privacy`}>{copy.trust.privacyLink}<Icon name="arrow" /></Link></div></section>

      <section className="eb-section eb-container eb-faq" aria-labelledby="eb-faq-title"><div className="eb-reveal"><p className="eb-eyebrow">{copy.faq.eyebrow}</p><h2 id="eb-faq-title">{copy.faq.title}</h2><span className="eb-faq-doodle" aria-hidden="true">?</span></div><div className="eb-faq-list eb-reveal">{copy.faq.items.map((item, i) => <details key={item.q} name="ebarki-faq"><summary><span className="eb-mono">0{i + 1}</span>{item.q}<span className="eb-faq-plus"><Icon name="plus" /></span></summary><p>{item.a}</p></details>)}</div></section>

      <section className="eb-final-section"><div className="eb-container eb-final-inner"><div className="eb-reveal"><p className="eb-eyebrow">{copy.final.eyebrow}</p><h2>{copy.final.title}</h2><p>{copy.final.text}</p><div className="eb-final-actions"><MagneticLink href={`/${locale}/cases/new`}>{copy.nav.start}</MagneticLink><a href="#walkthrough" className="eb-text-link">{copy.final.sample}<Icon name="arrow" /></a></div></div><div className="eb-final-art eb-reveal" aria-hidden="true"><div className="eb-folder-back" /><div className="eb-folder-paper"><Brand small /><div /><div /><div /><span>YOUR STORY / YOUR NEXT STEP</span></div><div className="eb-folder-front"><span>CASE / NEXT</span><svg width="90" height="90" viewBox="0 0 90 90" fill="none"><path d="M16 45h56M48 20l25 25-25 25" stroke="currentColor" strokeWidth="2.5" /></svg></div><span className="eb-final-stamp">{copy.final.stamp}</span></div></div></section>
    </main>

    <footer className="eb-footer"><div className="eb-container"><div className="eb-footer-top"><div><Link href={`/${locale}`} aria-label="Ebarki"><Brand /></Link><p>{copy.footer.tagline}</p></div><div className="eb-footer-links"><div><span className="eb-mono">{copy.footer.product}</span><a href="#how-it-works">{copy.footer.how}</a><Link href={`/${locale}/cases`}>{copy.footer.cases}</Link><Link href={`/${locale}/scenarios`}>{copy.footer.scenarios}</Link><Link href={`/${locale}/technology`}>{copy.footer.tech}</Link></div><div><span className="eb-mono">{copy.footer.useful}</span><Link href={`/${locale}/sources`}>{copy.footer.sources}</Link><Link href={`/${locale}/privacy`}>{copy.footer.privacy}</Link><Link href={`/${locale}/limitations`}>{copy.footer.limits}</Link><Link href={`/${locale}/help`}>{copy.footer.help}</Link></div></div><a className="eb-back-top" href="#top" aria-label={copy.footer.top}><Icon name="arrow" /></a></div><div className="eb-footer-bottom"><span>© 2026 Ebarki. {copy.footer.made}</span><span>{copy.footer.note}</span><Link className="eb-made-in" href={`/${locale}/admin/login`}>Admin login</Link></div></div></footer>
  </div></MotionConfig>;
}
