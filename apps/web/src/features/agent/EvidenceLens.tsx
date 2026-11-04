'use client';
import { useEffect, useState } from 'react';
import { apiFetch } from '@/lib/api';
import { useResource, type Fact } from '@/features/workspace/data';
import { factValue } from '@/features/workspace/Cases';
import { fieldLabel, originLabel } from '@/features/workspace/labels';
import { Button, ErrorPanel, Glyph, Loading, Modal, Notice, Status, words } from '@/features/workspace/ui';

type Link = { id: string; source_type: string; span_start?: number; span_end?: number; quote?: string; page_number?: number; normalized_box?: number[]; evidence?: { id: string; filename: string; mime_type: string } };
type Provenance = { fact: Fact; links: Link[]; narrative: string; case_version: number };

export function EvidenceLens({ caseId, factId, locale, onClose }: { caseId: string; factId: string | null; locale: string; onClose: () => void }) {
  const source = useResource<Provenance>(factId ? `cases/${caseId}/facts/${factId}/provenance` : null);
  const [selected, setSelected] = useState(0); const [url, setUrl] = useState(''); const [previewError, setPreviewError] = useState(false);
  const link = source.data?.links[selected];
  useEffect(() => { setSelected(0); }, [factId]);
  useEffect(() => {
    const abort = new AbortController(); let objectUrl = ''; setUrl(''); setPreviewError(false);
    if (link?.evidence) apiFetch(`/api/v1/cases/${caseId}/evidence/${link.evidence.id}/preview`, { signal: abort.signal, cache: 'no-store' })
      .then(async response => { if (!response.ok) throw new Error(); return response.blob(); })
      .then(blob => { if (!abort.signal.aborted) { objectUrl = URL.createObjectURL(blob); setUrl(objectUrl); } })
      .catch(() => { if (!abort.signal.aborted) setPreviewError(true); });
    return () => { abort.abort(); if (objectUrl) URL.revokeObjectURL(objectUrl); };
  }, [link?.evidence?.id, caseId]);
  const box = link?.normalized_box;
  const start = link?.span_start; const end = link?.span_end; const story = source.data?.narrative || '';
  const validSpan = typeof start === 'number' && typeof end === 'number' && start >= 0 && end > start && end <= story.length;
  return <Modal open={!!factId} onClose={onClose} title={words(locale, 'Evidence Lens', 'তথ্যের ভিত্তি দেখুন')} wide>
    {source.loading ? <Loading locale={locale} /> : source.error ? <ErrorPanel locale={locale} retry={source.reload} /> : source.data && <div className="ag-lens">
      <div className="ag-lens-finding"><span>{fieldLabel(source.data.fact.field_name, locale)}</span><strong>{factValue(source.data.fact, locale)}</strong><Status>{originLabel(source.data.fact.origin, locale)}</Status></div>
      <div className="ag-lens-thread" aria-hidden="true"><i /><span /><i /></div>
      {source.data.links.length > 1 && <div className="ag-lens-tabs">{source.data.links.map((item, index) => <button key={item.id} onClick={() => setSelected(index)} aria-pressed={index === selected}>{item.evidence?.filename || words(locale, 'Your account', 'আপনার বক্তব্য')} <span>{index + 1}</span></button>)}</div>}
      {link?.evidence ? <><div className="ag-lens-source-heading"><Glyph name="file" size={18} /><strong>{link.evidence.filename}</strong>{link.page_number && <span>{words(locale, 'Page', 'পৃষ্ঠা')} {link.page_number}</span>}</div>{previewError ? <Notice tone="attention">{words(locale, 'This original could not be opened. The saved source reference is shown below.', 'মূল নথিটি এখন খোলা যাচ্ছে না। সংরক্ষিত তথ্যসূত্র নিচে দেখানো হয়েছে।')}</Notice> : !url ? <Loading locale={locale} /> : link.evidence.mime_type.startsWith('image/') ? <div className="ag-lens-image"><img src={url} alt={link.evidence.filename} />{box?.length === 4 && <span style={{ left: `${box[0] * 100}%`, top: `${box[1] * 100}%`, width: `${(box[2] - box[0]) * 100}%`, height: `${(box[3] - box[1]) * 100}%` }} />}</div> : link.evidence.mime_type === 'application/pdf' ? <iframe className="ag-lens-pdf" src={`${url}#page=${link.page_number || 1}`} title={link.evidence.filename} /> : <audio src={url} controls />}{link.quote && <blockquote className="ag-lens-quote"><span>{words(locale, 'Linked passage', 'যুক্ত করা অংশ')}</span><p>{link.quote}</p></blockquote>}</> : <section className="ag-lens-story"><span className="ui-eyebrow">{words(locale, 'YOUR ORIGINAL ACCOUNT', 'আপনার মূল বক্তব্য')}</span><p>{validSpan ? <>{story.slice(0, start)}<mark>{story.slice(start, end)}</mark>{story.slice(end)}</> : source.data.fact.original_text || story}</p></section>}
      {!source.data.links.length && <Notice>{words(locale, 'This value is recorded in your case. No document passage is linked yet. You can link one from Evidence.', 'তথ্যটি আপনার অভিযোগে রাখা আছে। এখনো কোনো নথির অংশ যুক্ত নেই। “নথি ও প্রমাণ” থেকে যুক্ত করতে পারবেন।')}</Notice>}
      <p className="ag-small">{words(locale, 'A linked source explains where a statement came from. It does not independently verify the claim.', 'সূত্র থেকে তথ্যটি কোথা থেকে এসেছে বোঝা যায়। এতে বক্তব্যটি স্বাধীনভাবে যাচাই করা হয়েছে বলা হয় না।')}</p>
    </div>}
  </Modal>;
}
