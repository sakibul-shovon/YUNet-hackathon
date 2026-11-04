'use client';
import { createContext, useContext, type ReactNode } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useResource, type CaseRecord } from './data';
import { ErrorPanel, Glyph, Loading, Status, words } from './ui';
import { statusLabel } from './labels';
import { AgentMark } from '@/features/agent/AgentMark';

const CaseContext = createContext<{ record: CaseRecord; refresh: () => void } | null>(null);
export const useCase = () => { const value = useContext(CaseContext); if (!value) throw new Error('Case workspace is unavailable'); return value; };
export function CaseShell({ locale, caseId, children }: { locale: string; caseId: string; children: ReactNode }) {
  const resource = useResource<CaseRecord>(`cases/${caseId}`); const path = usePathname();
  if (resource.loading && !resource.data) return <Loading locale={locale} />;
  if (!resource.data) return <ErrorPanel locale={locale} retry={resource.reload} />;
  const record = resource.data; const base = `/${locale}/cases/${caseId}`; const workspace = path === base;
  const tabs = [['', 'Workspace', 'কাজের জায়গা'], ['/evidence', 'Evidence', 'নথি ও প্রমাণ'], ['/review', 'Review', 'তথ্য মিলিয়ে দেখুন'], ['/paths', 'Next steps', 'করণীয়'], ['/actions', 'Documents', 'খসড়া ও প্রস্তুতি'], ['/activity', 'Activity', 'ঘটনাক্রম']];
  return <CaseContext.Provider value={{ record, refresh: resource.reload }}>
    <header className={`ag-case-header ${workspace ? 'is-workspace' : ''}`}>
      <div className="ag-case-breadcrumb"><Link href={`/${locale}/cases`}><Glyph name="back" size={14} />{words(locale, 'My cases', 'আমার অভিযোগ')}</Link><span>/</span><span>{record.display_reference}</span>{record.is_demo && <Status>{words(locale, 'Sample workspace', 'নমুনা')}</Status>}</div>
      <div className="ag-case-title"><div><h1>{record.title}</h1><p>{record.merchant_name || words(locale, 'A case you control', 'আপনার নিজের অভিযোগ')}</p></div><Status tone={record.lifecycle_status === 'resolved' ? 'good' : 'brand'}>{statusLabel(record.lifecycle_status, locale)}</Status></div>
      {!workspace && <><Link href={base} className="ag-case-continuity"><AgentMark small /><span>{words(locale, 'Your case, connected. Continue working with Ebarki.', 'আপনার ঘটনার প্রসঙ্গ রেখেই Ebarki-র সঙ্গে কাজ এগিয়ে নিন।')}</span><Glyph name="arrow" size={16} /></Link><nav className="ag-case-tabs" aria-label={words(locale, 'Case views', 'অভিযোগের অংশগুলো')}>{tabs.map(([suffix, en, bn]) => <Link href={base + suffix} key={suffix} aria-current={path === base + suffix ? 'page' : undefined}>{words(locale, en, bn)}</Link>)}</nav></>}
    </header>
    {resource.error && <ErrorPanel locale={locale} retry={resource.reload} />}
    <div className="ui-case-content">{children}</div>
  </CaseContext.Provider>;
}
