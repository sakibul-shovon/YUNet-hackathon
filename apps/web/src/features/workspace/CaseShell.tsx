'use client';

import { createContext, useContext, type ReactNode } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useResource, type CaseRecord } from './data';
import { Button, ErrorPanel, Glyph, Loading, Status, words } from './ui';
import { statusLabel } from './labels';
import { WorkspaceAgentHUD } from './WorkspaceAgentHUD';

const CaseContext = createContext<{ record: CaseRecord; refresh: () => void } | null>(null);
export const useCase = () => { const value = useContext(CaseContext); if (!value) throw new Error('Case workspace is unavailable'); return value; };
export function CaseShell({ locale, caseId, children }: { locale: string; caseId: string; children: ReactNode }) {
  const resource = useResource<CaseRecord>(`cases/${caseId}`); const path = usePathname();
  if (resource.loading) return <Loading locale={locale} />;
  if (resource.error || !resource.data) return <ErrorPanel locale={locale} retry={resource.reload} />;
  const record = resource.data; const base = `/${locale}/cases/${caseId}`;
  const tabs = [['', 'Overview', 'এক নজরে'], ['/evidence', 'Evidence', 'নথি ও প্রমাণ'], ['/review', 'Review facts', 'তথ্য মিলিয়ে দেখুন'], ['/paths', 'Possible paths', 'কী করতে পারেন'], ['/actions', 'Action studio', 'খসড়া ও প্রস্তুতি'], ['/activity', 'Activity', 'ঘটনাক্রম']];
  return <CaseContext.Provider value={{ record, refresh: resource.reload }}><WorkspaceAgentHUD locale={locale} /><div className="ui-case-header"><div className="ui-case-breadcrumb"><Link href={`/${locale}/cases`}><Glyph name="back" size={14} />{words(locale, 'All cases', 'সব অভিযোগ')}</Link><span>/</span><span>{record.display_reference}</span></div><div className="ui-case-heading"><div><span className="ui-eyebrow">{words(locale, record.is_demo ? 'SYNTHETIC CASE · YOUR OWN COPY' : 'PRIVATE CASE DESK', record.is_demo ? 'নমুনা অভিযোগ · আপনার আলাদা কপি' : 'শুধু আপনার জন্য সংরক্ষিত')}</span><h1>{record.title}</h1><p>{record.merchant_name || words(locale, 'Seller or provider not added yet', 'বিক্রেতা বা সেবাদাতার নাম এখনো দেওয়া হয়নি')}</p></div><div><Status tone={record.lifecycle_status === 'resolved' ? 'good' : 'brand'}>{statusLabel(record.lifecycle_status, locale)}</Status><span className="ui-version">{words(locale, `Version ${record.row_version}`, `সংস্করণ ${record.row_version}`)}</span></div></div><nav className="ui-case-tabs" aria-label={words(locale, 'Case sections', 'অভিযোগের অংশগুলো')}>{tabs.map(([suffix, en, bn], i) => <Link key={suffix} href={base + suffix} aria-current={path === base + suffix ? 'page' : undefined}><span>0{i + 1}</span>{words(locale, en, bn)}</Link>)}</nav></div><div className="ui-case-content">{record.is_demo && <div className="ui-sample-strip"><Glyph name="play" size={13} />{words(locale, 'Fictional scenario. Changes affect only your copy; no complaint is submitted.', 'এটি কাল্পনিক নমুনা। পরিবর্তন শুধু আপনার কপিতেই থাকবে; কোথাও অভিযোগ জমা হবে না।')}</div>}{children}</div></CaseContext.Provider>;
}
