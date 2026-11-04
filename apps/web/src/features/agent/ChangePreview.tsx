'use client';
import { useState, type FormEvent } from 'react';
import { AnimatePresence, motion } from 'motion/react';
import { send, useResource, type Fact, type Route } from '@/features/workspace/data';
import { factValue } from '@/features/workspace/Cases';
import { SourceDrawer } from '@/features/workspace/Sources';
import { fieldLabel, issueLabel, routeTone, statusLabel } from '@/features/workspace/labels';
import { Button, Field, Glyph, Modal, Notice, Status, words } from '@/features/workspace/ui';
import { AgentMark } from './AgentMark';

type Trace = { fact?: string; node_type?: string; inspected_value?: unknown; outcome?: string; details?: string };
type Comparison = { case_version: number; baseline_routes: Route[]; simulated_routes: Route[]; route_diff: Array<{ route_id: string; issue_type: string; baseline_status: string; simulated_status: string; changed: boolean }>; is_material_change: boolean };
const examples = [['goods_delivered', 'The parcel arrived', 'পণ্যটি এসে গেছে'], ['refund_already_issued', 'A refund was received', 'টাকা ফেরত পেয়েছি'], ['provider_ticket_filed', 'A complaint was recorded', 'সেবাদাতাকে অভিযোগ করেছি']];
export function ChangePreview({ locale, caseId, onApply }: { locale: string; caseId: string; onApply: () => void }) {
  const facts = useResource<Fact[]>(`cases/${caseId}/facts`);
  const [field, setField] = useState('goods_delivered'); const [value, setValue] = useState('true'); const [result, setResult] = useState<Comparison | null>(null);
  const [busy, setBusy] = useState(false); const [error, setError] = useState(''); const [confirm, setConfirm] = useState(false); const [citation, setCitation] = useState<string | null>(null);
  const fields = ['goods_delivered', 'refund_already_issued', 'provider_ticket_filed', 'promised_delivery_date_passed', 'amount_paid'];
  const recorded = facts.data?.find(fact => fact.field_name === field);
  const assumed = field === 'amount_paid' ? `৳${Number(value || 0).toLocaleString(locale === 'bn' ? 'bn-BD' : 'en')}` : words(locale, value === 'true' ? 'Yes' : 'No', value === 'true' ? 'হ্যাঁ' : 'না');
  const overrides = { [field]: field === 'amount_paid' ? Math.round(Number(value) * 100) : value === 'true' };
  async function compare(event: FormEvent) { event.preventDefault(); setBusy(true); setError(''); try { setResult(await send<Comparison>(`cases/${caseId}/what-if`, { overrides })); } catch { setError(words(locale, 'This comparison could not be prepared. Your saved information is unchanged.', 'তুলনাটি তৈরি হয়নি। সংরক্ষিত তথ্য বদলায়নি।')); } finally { setBusy(false); } }
  function choose(next: string) { setField(next); setValue(next === 'amount_paid' ? '' : 'true'); setResult(null); setError(''); }
  function outcome(value: unknown) { return words(locale, value === 'TRUE' ? 'Condition met' : value === 'FALSE' ? 'Condition not met' : 'More information needed', value === 'TRUE' ? 'শর্ত মিলছে' : value === 'FALSE' ? 'শর্ত মিলছে না' : 'আরও তথ্য দরকার'); }
  return <section className="ex-change">
    <header className="ex-feature-heading"><div><span className="ag-eyebrow">{words(locale, 'CHANGE PREVIEW', 'তথ্য বদলালে প্রভাব দেখুন')}</span><h2>{words(locale, 'One change. See the ripple.', 'একটি তথ্য বদলালে কী হয়?')}</h2><p>{words(locale, 'Try an assumption. Follow the changed conditions before updating your case.', 'একটি তথ্য বদলে দেখে নিন। কোন শর্তের প্রভাব কোথায় পড়ছে বুঝে তারপর অভিযোগে রাখুন।')}</p></div><AgentMark state={busy ? 'working' : 'ready'} /></header>
    <div className="ex-change-examples">{examples.map(([key, en, bn]) => <button key={key} aria-pressed={field === key} onClick={() => choose(key)}><Glyph name={key === 'refund_already_issued' ? 'refresh' : key === 'goods_delivered' ? 'files' : 'file'} size={15} />{words(locale, en, bn)}</button>)}</div>
    <form className="ex-change-form" onSubmit={compare}>
      <Field label={words(locale, 'Change one detail', 'একটি তথ্য বদলে দেখুন')}><select value={field} onChange={event => choose(event.target.value)}>{fields.map(key => <option value={key} key={key}>{fieldLabel(key, locale)}</option>)}</select></Field>
      <fieldset className="ex-answer-field"><legend>{words(locale, 'Try this answer', 'এই উত্তর দিয়ে দেখুন')}</legend>
        {field === 'amount_paid' ? <input aria-label={words(locale, 'Amount in taka', 'টাকার পরিমাণ')} type="number" required min="0" max="1000000000" step=".01" placeholder={words(locale, 'Taka', 'টাকা')} value={value} onChange={event => { setValue(event.target.value); setResult(null); }} /> : <div className="ex-answer-toggle">{[['true', 'Yes', 'হ্যাঁ'], ['false', 'No', 'না']].map(([key, en, bn]) => <button type="button" key={key} aria-pressed={value === key} onClick={() => { setValue(key); setResult(null); }}>{words(locale, en, bn)}</button>)}</div>}
      </fieldset>
      <Button busy={busy} type="submit"><Glyph name="play" size={14} />{words(locale, 'Preview the effect', 'প্রভাব দেখুন')}</Button>
    </form>
    <div className="ex-assumption-thread"><div><span>{words(locale, 'YOUR RECORDED INFORMATION', 'এখন রাখা তথ্য')}</span><strong>{recorded ? factValue(recorded, locale) : words(locale, 'Not recorded', 'দেওয়া হয়নি')}</strong></div><span className="ex-change-arrow"><Glyph name="arrow" size={20} /></span><div><span>{words(locale, 'THE ASSUMPTION TO TEST', 'যে উত্তর দিয়ে দেখছেন')}</span><strong>{assumed}</strong><Status>{words(locale, 'Preview only', 'শুধু পরীক্ষা')}</Status></div></div>
    {error && <Notice tone="danger">{error}</Notice>}
    <AnimatePresence mode="wait">{result && <motion.div key={`${field}:${value}:${result.case_version}`} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="ex-change-result"><div className="ex-change-result-heading"><div><span className="ag-eyebrow">{words(locale, 'THE EFFECT, EXPLAINED', 'কী প্রভাব পড়ল দেখুন')}</span><h3>{words(locale, result.is_material_change ? 'The possible next steps changed.' : 'The recorded rules lead to the same next steps.', result.is_material_change ? 'সম্ভাব্য করণীয় বদলেছে।' : 'রাখা নিয়ম অনুযায়ী করণীয় একই আছে।')}</h3></div><span>{words(locale, 'Your saved case is unchanged.', 'সংরক্ষিত তথ্য বদলায়নি।')}</span></div>
      <div className="ex-change-route-labels"><span>{words(locale, 'Possible route', 'সম্ভাব্য করণীয়')}</span><span>{words(locale, 'Before', 'আগে')}</span><span>{words(locale, 'With this change', 'বদলালে')}</span></div>
      {result.route_diff.map(item => {
        const before = result.baseline_routes.find(route => route.route_id === item.route_id); const after = result.simulated_routes.find(route => route.route_id === item.route_id);
        const previous = (before?.condition_trace || []) as Trace[]; const next = (after?.condition_trace || []) as Trace[];
        const changes = next.filter((trace, index) => { const old = previous[index]; return trace.fact && (trace.outcome !== old?.outcome || JSON.stringify(trace.inspected_value) !== JSON.stringify(old?.inspected_value)); });
        const citations = after?.statutory_citations || before?.statutory_citations || [];
        return <section className={`ex-change-route ${item.changed ? 'is-changed' : ''}`} key={item.route_id}><div><strong>{issueLabel(item.issue_type, locale)}{item.changed && <small>{words(locale, 'Updated', 'বদলেছে')}</small>}</strong><Status tone={routeTone(item.baseline_status)}>{statusLabel(item.baseline_status, locale)}</Status><Status tone={routeTone(item.simulated_status)}>{statusLabel(item.simulated_status, locale)}</Status></div>{!!changes.length && <div className="ex-condition-changes">{changes.map((trace, index) => <div key={index}><span><i />{fieldLabel(trace.fact || field, locale)}</span><strong>{outcome(previous.find(old => old.fact === trace.fact)?.outcome)}<Glyph name="arrow" size={13} />{outcome(trace.outcome)}</strong></div>)}<p>{words(locale, 'These inspected conditions changed with your assumption. Other requirements still apply.', 'পরীক্ষার উত্তরে এই শর্তগুলোর অবস্থা বদলেছে। অন্য শর্তগুলোও প্রযোজ্য থাকে।')}</p>{citations.map(source => <button key={source} className="ex-text-action" onClick={() => setCitation(source)}><Glyph name="file" size={13} />{words(locale, 'Inspect the reference', 'সূত্রটি দেখুন')}<Glyph name="external" size={12} /></button>)}</div>}</section>;
      })}
      <footer className="ex-change-result-footer"><div><AgentMark small /><span>{words(locale, 'Keep this as a preview, or record it if it really happened.', 'পরীক্ষা হিসেবে রাখুন, অথবা সত্যি ঘটে থাকলে অভিযোগে দিন।')}</span></div><Button tone="secondary" onClick={() => setConfirm(true)}>{words(locale, 'This actually happened', 'সত্যিই এমন হয়েছে')}<Glyph name="arrow" size={14} /></Button></footer>
    </motion.div>}</AnimatePresence>
    <Modal open={confirm} onClose={() => setConfirm(false)} title={words(locale, 'Keep this change in your case?', 'অভিযোগে এই পরিবর্তন রাখবেন?')}><div className="ex-apply-review"><p>{words(locale, 'Confirm only if this describes what happened. Your earlier information remains in the case history.', 'সত্যিই এমন হয়ে থাকলে নিশ্চিত করুন। আগের তথ্য ইতিহাসে থাকবে।')}</p><div><span>{fieldLabel(field, locale)}</span><strong>{assumed}</strong></div><Button busy={busy} onClick={async () => { setBusy(true); try { await send(`cases/${caseId}/what-if/apply`, { overrides, expected_version: result?.case_version }); setConfirm(false); setResult(null); facts.reload(); onApply(); } catch { setConfirm(false); setError(words(locale, 'Your case changed or this could not be saved. Compare again before applying.', 'অভিযোগের তথ্য বদলেছে, অথবা পরিবর্তনটি রাখা যায়নি। আবার তুলনা করে তারপর রাখুন।')); } finally { setBusy(false); } }}><Glyph name="check" size={15} />{words(locale, 'Confirm & update my case', 'নিশ্চিত করে অভিযোগে রাখুন')}</Button></div></Modal>
    <SourceDrawer source={null} citation={citation} locale={locale} onClose={() => setCitation(null)} />
  </section>;
}
