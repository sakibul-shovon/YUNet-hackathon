'use client';

import { useEffect, useRef, useState, type FormEvent } from 'react';
import Link from 'next/link';
import dynamic from 'next/dynamic';
import { AnimatePresence, MotionConfig, motion } from 'motion/react';
import { useCase } from '@/features/workspace/CaseShell';
import { apiFetch } from '@/lib/api';
import { request, send, uploadEvidence, useResource, type Assessment, type Evidence, type Fact } from '@/features/workspace/data';
import { factValue } from '@/features/workspace/Cases';
import { EvidenceVault } from '@/features/workspace/Evidence';
import { FactReview } from '@/features/workspace/Review';
import { Paths, QuestionBlock } from '@/features/workspace/Paths';
import { ActionStudio } from '@/features/workspace/Actions';
import { CaseActivity } from '@/features/workspace/Activity';
import { fieldLabel, issueLabel, originLabel, routeTone, statusLabel } from '@/features/workspace/labels';
import { Button, Empty, Glyph, Loading, Modal, Notice, Status, formatDate, money, words, type GlyphName } from '@/features/workspace/ui';
import { AgentMark } from './AgentMark';
import { CaseAIConsent } from './CaseAIConsent';
import { EvidenceLens } from './EvidenceLens';
import { TryChange } from './TryChange';
import { useAgentRun, type AgentRun, type AgentStage } from './useAgentRun';
import type { ConnectedRecords } from './experience-types';

const EvidenceStory = dynamic(() => import('./EvidenceStory').then(module => module.EvidenceStory));
const ReplyPreparation = dynamic(() => import('./ReplyPreparation').then(module => module.ReplyPreparation));
const FilingHandoff = dynamic(() => import('./FilingHandoff').then(module => module.FilingHandoff));

type Canvas = 'briefing' | 'evidence' | 'review' | 'paths' | 'whatif' | 'draft' | 'activity' | 'timeline' | 'reply' | 'handoff';
type Reconciliation = { narrated_amount_minor_units: number; linked_evidence_total_minor_units: number; discrepancy_minor_units: number; status: string; is_reconciled: boolean; reconciled_items: Array<{ evidence_id: string; filename: string; amount_minor_units: number; is_duplicate: boolean }>; unlinked_items: Array<{ evidence_id: string; filename: string; amount_minor_units: number }> };
const taskLabels: Record<string, [string, string]> = {
  case_understanding: ['Understand your situation', 'আপনার ঘটনা বোঝা'],
  text_extraction: ['Organize the important facts', 'দরকারি তথ্য গুছিয়ে নেওয়া'],
  evidence_review: ['Read your records', 'আপনার নথি পড়ে দেখা'],
  payment_reconciliation: ['Compare payment information', 'টাকার তথ্য মিলিয়ে দেখা'],
  source_retrieval: ['Find relevant references', 'প্রাসঙ্গিক সূত্র খোঁজা'],
  procedural_assessment: ['Check possible next steps', 'সম্ভাব্য করণীয় দেখা'],
  draft_preparation: ['Prepare your request', 'অনুরোধের খসড়া তৈরি'],
};
const planned = ['case_understanding', 'text_extraction', 'evidence_review', 'payment_reconciliation', 'source_retrieval', 'procedural_assessment'];
const canvasItems: Array<[Canvas, string, string, GlyphName]> = [
  ['briefing', 'Briefing', 'সারাংশ', 'home'], ['timeline', 'Evidence story', 'সূত্রসহ ঘটনা', 'files'],
  ['whatif', 'Try a change', 'বদলালে কী হয়', 'chart'], ['reply', 'Prepare a reply', 'উত্তর তৈরি', 'send'],
  ['draft', 'Draft', 'খসড়া', 'edit'], ['paths', 'Next steps', 'করণীয়', 'arrow'],
];
const taskCanvas: Record<string, Canvas> = { case_understanding: 'briefing', text_extraction: 'review', evidence_review: 'timeline', payment_reconciliation: 'briefing', source_retrieval: 'paths', procedural_assessment: 'paths', draft_preparation: 'draft' };

function Stage({ stage, locale, pending = false, onOpen, selected = false }: { stage: AgentStage; locale: string; pending?: boolean; onOpen?: () => void; selected?: boolean }) {
  const title = words(locale, ...(taskLabels[stage.stage_name] || ['Review your case', 'আপনার অভিযোগ দেখা']));
  return <motion.li layout className={`ag-task ag-task-${pending ? 'pending' : stage.status} ${selected ? 'ex-stage-active' : ''}`}>
    <span className="ag-task-node">{stage.status === 'completed' ? <Glyph name="check" size={13} /> : stage.status === 'running' ? <span className="ui-spinner" /> : <i />}</span>
    <div>{onOpen ? <button className="ex-step-button" onClick={onOpen}>{title}<Glyph name="arrow" size={12}/></button> : <strong>{title}</strong>}
      {!pending && stage.status === 'completed' && <p>{typeof stage.details.proposed_facts === 'number' ? words(locale, `${stage.details.proposed_facts} new facts proposed for review`, `${Number(stage.details.proposed_facts).toLocaleString('bn-BD')}টি নতুন তথ্য মিলিয়ে দেখার জন্য রাখা হয়েছে`) : typeof stage.details.files_reviewed === 'number' ? words(locale, `${stage.details.files_reviewed} records inspected`, `${Number(stage.details.files_reviewed).toLocaleString('bn-BD')}টি নথি দেখা হয়েছে`) : typeof stage.details.retrieved_count === 'number' ? words(locale, `${stage.details.retrieved_count} reference matches`, `${Number(stage.details.retrieved_count).toLocaleString('bn-BD')}টি সূত্র পাওয়া গেছে`) : stage.stage_name === 'payment_reconciliation' ? words(locale, stage.details.status === 'discrepancy' ? 'A difference needs your attention' : 'Comparison recorded', stage.details.status === 'discrepancy' ? 'একটি অমিল আপনার দেখা দরকার' : 'তুলনার ফল রাখা হয়েছে') : stage.stage_name === 'draft_preparation' ? words(locale, 'Saved as a reviewable draft', 'মিলিয়ে দেখার জন্য খসড়া রাখা হয়েছে') : words(locale, 'Result recorded', 'ফল রাখা হয়েছে')}</p>}
      {!pending && <details className="ag-task-detail"><summary>{words(locale, 'Execution detail', 'কাজের বিস্তারিত')}</summary><span>{stage.details.method ? String(stage.details.method) : stage.method}</span>{stage.duration_ms !== null && <span>{stage.duration_ms} ms</span>}<span>{formatDate(stage.started_at, locale, true)}</span></details>}
    </div>
  </motion.li>;
}

export function AgentWorkspace({ locale }: { locale: string }) {
  const { record, refresh } = useCase(); const caseId = record.id;
  const [canvas, setCanvas] = useState<Canvas>('briefing'); const [pinned, setPinned] = useState(false);
  const [lens, setLens] = useState<string | null>(null); const [replay, setReplay] = useState<AgentRun | null>(null);
  const [prompt, setPrompt] = useState(''); const [answer, setAnswer] = useState(''); const [asking, setAsking] = useState(false);
  const [notice, setNotice] = useState(''); const [error, setError] = useState(''); const [uploading, setUploading] = useState(false);
  const [showPlan, setShowPlan] = useState(false); const [showStory, setShowStory] = useState(false);
  const [confirming, setConfirming] = useState(false);
  const fileInput = useRef<HTMLInputElement>(null); const questionAbort = useRef<AbortController | null>(null);
  const autoStarted = useRef(false);
  const canvasRef = useRef<HTMLElement>(null);
  const connected = useResource<ConnectedRecords>(`cases/${caseId}/connected-records`);
  const facts = useResource<Fact[]>(`cases/${caseId}/facts`);
  const files = useResource<Evidence[]>(`cases/${caseId}/evidence`);
  const assessment = useResource<Assessment>(`cases/${caseId}/assessment`);
  const payments = useResource<Reconciliation>(`cases/${caseId}/evidence/reconciliation`);
  const events = useResource<Array<{ id: string; title: string; description: string; origin: string; created_at: string; decision_diff?: { is_decision_changed: boolean } }>>(`cases/${caseId}/activity/timeline`);
  function refreshWork() { facts.reload(); files.reload(); assessment.reload(); payments.reload(); events.reload(); connected.reload(); refresh(); }
  const agent = useAgentRun(caseId, locale, refreshWork);
  const run = agent.run;
  const readyFacts = facts.data || [];
  const needsReview = readyFacts.filter(fact => !['accepted', 'corrected'].includes(fact.review_outcome || ''));
  const moneyFact = readyFacts.find(fact => ['amount_paid', 'claimed_amount', 'transaction_amount'].includes(fact.field_name));
  const receiptTotal = payments.data?.linked_evidence_total_minor_units || 0;
  const discrepancy = !!payments.data && payments.data.status === 'discrepancy' && receiptTotal > 0;
  const currentStage = run?.stages.find(stage => stage.status === 'running');
  const summaryRun = [run, ...agent.history].find(item => item?.locale === locale && item.case_version === record.row_version && item.result.understanding);
  const understanding = (summaryRun?.result.understanding || { summary: record.story_narrative, model_executed: false, method: 'original_account' }) as { summary?: string; model_executed?: boolean; method?: string };
  const lastExternal = events.data?.find(event => event.origin === 'user_reported');
  const changed = !!lastExternal?.decision_diff?.is_decision_changed;
  const question = assessment.data?.next_best_question;
  const anyFiles = files.data?.filter(item => item.status === 'accepted') || [];
  const readCount = (run?.result.readings as unknown[] | undefined)?.length || 0;
  const workKey = `${run?.id}:${run?.stages.filter(stage => stage.status === 'completed').length}:${readCount}:${record.row_version}`;
  useEffect(() => { connected.reload(); }, [workKey]);
  useEffect(() => { const view = new URLSearchParams(window.location.search).get('view') as Canvas; if (['timeline', 'reply', 'handoff', 'briefing', 'draft', 'whatif', 'paths', 'review', 'evidence', 'activity'].includes(view)) { setCanvas(view); setPinned(true); } }, []);

  useEffect(() => () => questionAbort.current?.abort(), []);
  useEffect(() => {
    if (agent.loading || autoStarted.current) return;
    autoStarted.current = true;
    if (new URLSearchParams(window.location.search).get('start') === '1' && !agent.history.length && record.consent_status !== 'withdrawn') void agent.start('resolve');
  }, [agent.loading, agent.history.length]);
  useEffect(() => {
    if (pinned) return;
    if (currentStage?.stage_name === 'evidence_review') setCanvas('timeline');
    if (currentStage?.stage_name === 'payment_reconciliation') setCanvas('briefing');
    if (run?.operation === 'draft' && run.status === 'completed') setCanvas('draft');
  }, [currentStage?.stage_name, run?.status, run?.id, pinned]);
  function openCanvas(next: Canvas) { setCanvas(next); setPinned(true); setError(''); const url = new URL(window.location.href); url.searchParams.set('view', next); window.history.replaceState(null, '', url); if (window.matchMedia('(max-width: 700px)').matches) requestAnimationFrame(() => canvasRef.current?.scrollIntoView({ block: 'start', behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth' })); }
  async function start(operation = 'resolve') { setPinned(false); setAnswer(''); setNotice(''); await agent.start(operation); }
  async function addFiles(list: FileList | null) {
    if (!list?.length) return; setUploading(true); setError('');
    try {
      for (const file of Array.from(list)) { if (file.size > 20 * 1024 * 1024) throw new Error('size'); await uploadEvidence(caseId, file); }
      files.reload(); setPinned(false); await agent.start('resolve');
    } catch { setError(words(locale, 'A file could not be added. Check the 20 MB limit and try again from Records.', 'একটি ফাইল যোগ করা যায়নি। ২০ এমবির সীমা মিলিয়ে “নথি” থেকে আবার চেষ্টা করুন।')); }
    finally { setUploading(false); if (fileInput.current) fileInput.current.value = ''; }
  }
  async function addSamplePayment() {
    setUploading(true); setError('');
    try { await send(`cases/${caseId}/sample-payment`); files.reload(); await start('resolve'); }
    catch { setError(words(locale, 'The sample record could not be added. Try again.', 'নমুনার নথি যোগ করা যায়নি। আবার চেষ্টা করুন।')); }
    finally { setUploading(false); }
  }
  async function confirmDetails() {
    setConfirming(true); setError('');
    try {
      for (const fact of needsReview.slice(0, 5)) await send(`cases/${caseId}/facts/${fact.id}/review`, { review_outcome: 'accepted' });
      refreshWork();
      setNotice(words(locale, 'Your review is saved. The next step will use these confirmed details.', 'আপনার যাচাই রাখা হয়েছে। পরের ধাপে এই নিশ্চিত করা তথ্য ব্যবহার হবে।'));
    } catch { setError(words(locale, 'Some details could not be confirmed. Open Facts to check the latest status.', 'কিছু তথ্য নিশ্চিত করা যায়নি। “তথ্য” খুলে সর্বশেষ অবস্থা দেখুন।')); }
    finally { setConfirming(false); }
  }
  async function ask(event: FormEvent) {
    event.preventDefault(); if (!prompt.trim() || asking) return;
    setAsking(true); setError(''); const abort = new AbortController(); questionAbort.current = abort;
    try {
      const response = await request<{ reply_en: string; reply_bn: string }>('copilot/chat', { method: 'POST', body: JSON.stringify({ message: prompt, case_id: caseId, locale }), signal: abort.signal });
      setAnswer(words(locale, response.reply_en, response.reply_bn)); setPrompt('');
    } catch { if (!abort.signal.aborted) setError(words(locale, 'The explanation could not be prepared. Your saved work is still available.', 'ব্যাখ্যাটি এখন তৈরি করা যায়নি। সংরক্ষিত কাজ ঠিক আছে।')); }
    finally { setAsking(false); }
  }
  const markState = agent.running || asking || uploading ? 'working' : run?.status === 'failed' ? 'failed' : run?.status === 'cancelled' ? 'paused' : discrepancy || needsReview.length || question ? 'waiting' : run ? 'done' : 'ready';
  const agentSpeech = agent.running ? words(locale, 'I’m working through your records. You can inspect any part while I continue.', 'আপনার তথ্যগুলো ধাপে ধাপে দেখছি। এর মধ্যেও যেকোনো অংশ খুলে দেখতে পারেন।') : discrepancy ? words(locale, 'Your account and the payment records do not agree yet. Let’s clarify the difference before relying on the amount.', 'আপনার বক্তব্য আর নথিতে টাকার হিসাব মিলছে না। অঙ্কটি ব্যবহার করার আগে পার্থক্যটা পরিষ্কার করে নেওয়া যাক।') : needsReview.length ? words(locale, 'I’ve organized the recorded information. Please check these details so the next step uses what you confirm.', 'পাওয়া তথ্যগুলো গুছিয়ে রেখেছি। পরের ধাপে যাওয়ার আগে এগুলো ঠিক আছে কি না মিলিয়ে নিন।') : question ? words(locale, 'One detail can change the next step. I have a question for you.', 'একটি তথ্যের ওপর পরের করণীয় বদলাতে পারে। আপনার কাছে একটি প্রশ্ন আছে।') : run?.operation === 'draft' ? words(locale, 'Your draft is ready. Inspect the supporting information and make it your own before using it.', 'খসড়া তৈরি হয়েছে। ব্যবহারের আগে তথ্যের ভিত্তি দেখুন এবং দরকারমতো বদলে নিন।') : words(locale, 'Let’s work toward a clear next step. I can compare your records, check conditions, and prepare a request for your review.', 'পরের ধাপটা পরিষ্কার করে নেওয়া যাক। আপনার নথি মিলিয়ে, শর্ত দেখে, পর্যালোচনার জন্য খসড়া তৈরি করতে পারি।');
  const planKeys = run?.operation === 'draft' ? ['source_retrieval', 'procedural_assessment', 'draft_preparation'] : run?.operation === 'assess' ? ['source_retrieval', 'procedural_assessment'] : planned;

  return <MotionConfig reducedMotion="user"><div className={`ag-workspace ${agent.running ? 'ag-is-working' : ''}`}>
    <header className="ag-workspace-header"><div><span className="ag-eyebrow">{words(locale, 'YOUR RESOLUTION WORKSPACE', 'আপনার অভিযোগের অগ্রগতি')}</span></div><div className="ag-workspace-status"><AgentMark state={markState} small /><span>{words(locale, agent.running ? 'Working with your records' : agent.loading ? 'Opening your workspace' : markState === 'waiting' ? 'Your review is next' : markState === 'failed' ? 'Ready to try again' : 'Working beside you', agent.running ? 'আপনার তথ্য নিয়ে কাজ চলছে' : agent.loading ? 'আপনার তথ্য খোলা হচ্ছে' : markState === 'waiting' ? 'এবার আপনি মিলিয়ে নিন' : markState === 'failed' ? 'আবার চেষ্টা করতে পারেন' : 'আপনার সঙ্গে আছি')}</span></div></header>
    {record.is_demo && <div className="ag-demo-note"><Glyph name="play" size={15} /><span>{words(locale, 'Your own sample workspace. Change the information, inspect the work, and explore the result.', 'এটি আপনার আলাদা নমুনা। তথ্য বদলে, কাজের ধাপ খুলে, ফল দেখুন।')}</span><Link href={`/${locale}/scenarios`}>{words(locale, 'More samples', 'আরও নমুনা')}<Glyph name="arrow" size={13} /></Link></div>}
    <div className="ag-work-layout">
      <aside className={`ag-workstream ${showPlan ? 'ag-plan-expanded' : ''}`} aria-label={words(locale, 'Work with Ebarki', 'Ebarki-র সঙ্গে কাজ করুন')}>
        <div className="ag-agent-heading"><AgentMark state={markState} /><div><strong>Ebarki</strong><span>{words(locale, currentStage ? taskLabels[currentStage.stage_name]?.[0] || 'Working' : agent.running ? 'Getting started' : run?.status === 'cancelled' ? 'You stopped this run' : 'Your case assistant', currentStage ? taskLabels[currentStage.stage_name]?.[1] || 'কাজ চলছে' : agent.running ? 'শুরু হচ্ছে' : run?.status === 'cancelled' ? 'আপনি কাজটি থামিয়েছেন' : 'আপনার অভিযোগের সহকারী')}</span></div><button className="ag-mobile-plan" onClick={() => setShowPlan(!showPlan)} aria-expanded={showPlan}>{words(locale, showPlan ? 'Hide steps' : 'View steps', showPlan ? 'ধাপ আড়াল করুন' : 'ধাপ দেখুন')}</button></div>
        <p className="ag-agent-speech">{agentSpeech}</p>
        {connected.data&&!connected.data.capabilities.external_consent&&(connected.data.capabilities.image_reading||connected.data.capabilities.audio_transcription)&&record.consent_status!=='withdrawn'&&<CaseAIConsent caseId={caseId} locale={locale} disabled={agent.running} onEnabled={()=>{refreshWork();void start('resolve');}}/>}
        <div className="ag-task-list-wrap"><div className="ag-plan-label"><span>{words(locale, run ? 'WORK PLAN' : 'A PLAN FOR YOUR CASE', run ? 'কাজের ধাপ' : 'আপনার অভিযোগ নিয়ে যেভাবে এগোব')}</span>{run && <Status tone={run.status === 'failed' ? 'danger' : agent.running ? 'brand' : 'neutral'}>{statusLabel(run.status, locale)}</Status>}</div><ol className="ag-task-list">{planKeys.map(key => { const stage = run?.stages.find(item => item.stage_name === key); return <Stage key={key} locale={locale} stage={stage || { stage_name: key, method: '', status: 'pending', started_at: '', details: {}, duration_ms: null }} pending={!stage} onOpen={() => openCanvas(taskCanvas[key] || 'briefing')} selected={canvas === taskCanvas[key]} />; })}</ol></div>
        {(agent.error || error) && <Notice tone="danger">{error || words(locale, 'This operation could not be completed. Your saved case is available. Refresh or try the task again.', 'কাজটি শেষ করা যায়নি। সংরক্ষিত অভিযোগ ঠিক আছে। আবার তথ্য আনুন বা কাজটি চেষ্টা করুন।')}</Notice>}
        {notice && <Notice tone="good">{notice}</Notice>}
        {run?.status === 'failed' && <Notice tone="attention">{words(locale, 'A task stopped before finishing. Completed steps remain in the run history.', 'একটি ধাপ শেষ হওয়ার আগেই থেমেছে। শেষ হওয়া ধাপগুলো ইতিহাসে আছে।')}</Notice>}
        <AnimatePresence mode="wait">
          {!agent.running && <motion.div key={discrepancy ? 'conflict' : needsReview.length ? 'review' : question?.question_key || 'ready'} className="ag-intervention" initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}>
            {discrepancy ? <><span className="ag-eyebrow">{words(locale, 'LET’S CLEAR THIS UP', 'একটি বিষয় মিলিয়ে নিই')}</span><h3>{words(locale, 'Could there be another payment record?', 'টাকা দেওয়ার আরেকটি নথি আছে কি?')}</h3><p>{words(locale, 'Add the missing receipt, or review the amount you reported. The original account stays in your case.', 'বাকি রসিদ থাকলে যোগ করুন। অথবা আপনার জানানো অঙ্কটি মিলিয়ে নিন। আগের বক্তব্য থেকে যাবে।')}</p><Button onClick={() => fileInput.current?.click()} busy={uploading}><Glyph name="plus" size={15} />{words(locale, 'Add a record', 'আরেকটি নথি দিন')}</Button>{record.is_demo && <Button tone="secondary" onClick={addSamplePayment} busy={uploading}>{words(locale, 'Add the sample second payment', '\u09a8\u09ae\u09c1\u09a8\u09be\u09b0 \u09a6\u09cd\u09ac\u09bf\u09a4\u09c0\u09df \u09b0\u09b8\u09bf\u09a6 \u09a6\u09bf\u09a8')}</Button>}<Button tone="quiet" onClick={() => openCanvas('review')}>{words(locale, 'Review the reported amount', 'জানানো অঙ্কটি মিলিয়ে দেখুন')}</Button></> : needsReview.length ? <><span className="ag-eyebrow">{words(locale, 'YOUR REVIEW MATTERS', 'আপনি মিলিয়ে নিন')}</span><h3>{words(locale, `${needsReview.length} details need your review.`, `${needsReview.length.toLocaleString('bn-BD')}টি তথ্য মিলিয়ে দেখা দরকার।`)}</h3><p>{words(locale, 'Open a detail to inspect its origin. Confirm, correct, or leave it uncertain.', 'তথ্যটি কোথা থেকে এসেছে খুলে দেখুন। ঠিক থাকলে জানান, ভুল হলে বদলান বা অনিশ্চিত রাখুন।')}</p><Button onClick={() => openCanvas('review')}>{words(locale, 'Review the facts', 'তথ্য মিলিয়ে দেখুন')}<Glyph name="arrow" size={16} /></Button></> : question ? <QuestionBlock question={question} locale={locale} caseId={caseId} onAnswer={value => { assessment.setData(value); facts.reload(); refresh(); void start('assess'); }} /> : <><span className="ag-eyebrow">{words(locale, 'A USEFUL NEXT STEP', 'এবার কী করতে পারেন')}</span><h3>{words(locale, run ? 'Turn the information into a reviewed request.' : 'Let’s put the pieces together.', run ? 'তথ্যগুলো দিয়ে অনুরোধের খসড়া করা যাক।' : 'তথ্যগুলো একসঙ্গে দেখে নেওয়া যাক।')}</h3><Button onClick={() => start(run ? 'draft' : 'resolve')} busy={agent.starting}>{words(locale, run ? 'Prepare my request' : 'Work through my case', run ? 'অনুরোধের খসড়া করুন' : 'অভিযোগ নিয়ে কাজ শুরু করুন')}<Glyph name="arrow" size={16} /></Button></>}
          </motion.div>}
        </AnimatePresence>
        {agent.running ? <Button tone="secondary" onClick={agent.stop} disabled={run?.cancel_requested}><Glyph name="stop" size={15} />{words(locale, run?.cancel_requested ? 'Stopping at the next checkpoint…' : 'Stop this run', run?.cancel_requested ? 'চলতি ধাপের শেষে থামবে…' : 'এই কাজ থামান')}</Button> : <div className="ag-follow-up-actions"><button onClick={() => start('resolve')} disabled={agent.starting || record.consent_status === 'withdrawn'}><Glyph name="refresh" size={15} />{words(locale, 'Review the latest information', 'সর্বশেষ তথ্য আবার দেখুন')}</button><button onClick={() => openCanvas('whatif')}><Glyph name="chart" size={15} />{words(locale, 'Try a change', 'তথ্য বদলালে কী হয়')}</button></div>}
        <div className="ag-ask-area">{asking && <p role="status"><span className="ui-spinner" />{words(locale, 'Preparing an explanation…', 'সহজ করে ব্যাখ্যা তৈরি হচ্ছে…')}<button onClick={() => questionAbort.current?.abort()}>{words(locale, 'Stop', 'থামান')}</button></p>}{answer && <div className="ag-explanation"><span className="ag-eyebrow">{words(locale, 'EXPLANATION', 'সহজ করে বললে')}</span><p>{answer}</p></div>}<form onSubmit={ask}><label htmlFor="ag-prompt" className="sr-only">{words(locale, 'Ask about your case', 'অভিযোগ নিয়ে প্রশ্ন করুন')}</label><textarea id="ag-prompt" rows={2} required maxLength={2000} value={prompt} onChange={event => setPrompt(event.target.value)} placeholder={words(locale, 'Ask about this case…', 'এই অভিযোগ নিয়ে জানতে চান…')} /><button className="ag-send" disabled={asking || !prompt.trim()} aria-label={words(locale, 'Ask Ebarki', 'Ebarki-কে প্রশ্ন করুন')}><Glyph name="arrow" size={17} /></button></form><div className="ag-ask-foot"><button onClick={() => fileInput.current?.click()} disabled={uploading}><Glyph name="plus" size={14} />{words(locale, 'Add records', 'নথি দিন')}</button>{agent.history.length > 0 && <button onClick={() => setReplay(agent.history[0])}><Glyph name="clock" size={14} />{words(locale, 'Run history', 'কাজের ইতিহাস')}</button>}</div></div>
      </aside>
      <section ref={canvasRef} className="ag-canvas" aria-label={words(locale, 'Working canvas', 'কাজের জায়গা')}>
        <div className="ag-canvas-heading"><div><span className="ag-live-point" /><strong>{words(locale, 'Working canvas', 'কাজের জায়গা')}</strong><span className="ag-canvas-version">{words(locale, `Case v${record.row_version}`, `অভিযোগের সংস্করণ ${record.row_version}`)}</span></div>{pinned && agent.running && <button onClick={() => setPinned(false)}>{words(locale, 'Follow Ebarki', 'Ebarki-র কাজ দেখুন')}<Glyph name="arrow" size={13} /></button>}</div>
        <div className="ex-view-toolbar"><div className="ex-secondary-views"><select className="ex-more-views" aria-label={words(locale,'More case views','অভিযোগের অন্য অংশ')} value={['review','evidence','handoff','activity'].includes(canvas)?canvas:''} onChange={event=>{if(event.target.value)openCanvas(event.target.value as Canvas);}}><option value="">{words(locale,'More case views','অন্য অংশ')}</option>{[['review','Review facts','তথ্য মিলিয়ে দেখুন'],['evidence','Original records','মূল নথি'],['handoff','Filing handoff','জমা দেওয়ার প্রস্তুতি'],['activity','Case activity','ঘটনার নতুন খবর']].map(([view,en,bn])=><option value={view} key={view}>{words(locale,en,bn)}</option>)}</select></div><nav className="ag-canvas-tabs" aria-label={words(locale, 'Working views', 'কাজের অংশগুলো')}>{canvasItems.map(([key, en, bn, icon]) => <button key={key} onClick={() => openCanvas(key)} aria-current={canvas === key ? 'page' : undefined}><Glyph name={icon} size={15} />{words(locale, en, bn)}</button>)}</nav></div>
        <AnimatePresence mode="wait"><motion.div key={canvas} className={`ag-canvas-body ${['evidence', 'review', 'paths', 'draft', 'activity'].includes(canvas) ? 'ag-embedded' : ''}`} initial={{ opacity: 0, y: 9 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} transition={{ duration: .19 }}>
          {canvas === 'briefing' && <>
            <div className="ag-briefing-title"><span className="ag-eyebrow">{words(locale, 'THE PICTURE SO FAR', 'এখন পর্যন্ত যা জানা যাচ্ছে')}</span><h2>{discrepancy ? words(locale, 'One detail needs a closer look.', 'একটি তথ্য মিলিয়ে নেওয়া দরকার।') : changed ? words(locale, 'New information. A clearer next step.', 'নতুন তথ্য এসেছে। করণীয় আবার দেখুন।') : words(locale, 'Let’s make sense of what happened.', 'কী ঘটেছে, গুছিয়ে বোঝা যাক।')}</h2><p>{understanding?.summary || record.story_narrative || words(locale, 'Add your story and the records you have. Ebarki will work through them with you.', 'আপনার ঘটনা আর হাতে থাকা নথি দিন। Ebarki আপনার সঙ্গে তথ্যগুলো গুছিয়ে নেবে।')}</p>{understanding && !understanding.model_executed && <span className="ag-account-label">{words(locale, "Your original account, kept as written.", "আপনার মূল বক্তব্য, যেমন লিখেছেন।")}</span>}{understanding?.model_executed && <span className="ag-model-label"><AgentMark small />{words(locale, 'AI-assisted summary · check against your account', 'AI-এর সাহায্যে সারাংশ · মূল বক্তব্যের সঙ্গে মিলিয়ে নিন')}</span>}</div>
            <div className="ag-payment-comparison"><article className="ag-story-record"><span className="ag-eyebrow">{words(locale, 'YOUR ACCOUNT', 'আপনার বক্তব্য')}</span><Glyph name="file" size={25} /><p>{words(locale, 'Amount recorded in your case', 'অভিযোগে রাখা টাকার অঙ্ক')}</p><strong>{moneyFact ? factValue(moneyFact, locale) : words(locale, 'Not recorded', 'এখনো দেওয়া হয়নি')}</strong><button onClick={() => moneyFact ? setLens(moneyFact.id) : openCanvas('review')}>{words(locale, 'Inspect the information', 'তথ্যটি খুলে দেখুন')}<Glyph name="arrow" size={14} /></button></article><article className="ag-receipt-record"><span className="ag-eyebrow">{words(locale, 'LINKED PAYMENT RECORDS', 'যুক্ত করা টাকা দেওয়ার নথি')}</span><div className="ag-receipt-lines"><i /><i /><i /></div><p>{payments.loading ? words(locale, 'Checking records…', 'নথি দেখা হচ্ছে…') : words(locale, 'Total from linked receipts', 'যুক্ত করা রসিদে মোট অঙ্ক')}</p><strong>{receiptTotal > 0 ? money(receiptTotal / 100, locale) : words(locale, 'Needs a record', 'নথি যুক্ত করা দরকার')}</strong><button onClick={() => openCanvas('evidence')}>{words(locale, 'Open the originals', 'মূল নথিগুলো দেখুন')}<Glyph name="arrow" size={14} /></button></article></div>
            <div className="ag-evidence-thread" aria-hidden="true"><i /><span /><i /></div>
            <motion.div layout className={`ag-comparison-result ${discrepancy ? 'needs-attention' : ''}`}><div><AgentMark state={discrepancy ? 'waiting' : 'done'} small /><strong>{discrepancy ? words(locale, 'A difference to clarify', 'হিসাবের পার্থক্য পরিষ্কার করা দরকার') : payments.data?.is_reconciled && receiptTotal ? words(locale, 'Payment records agree', 'টাকার নথির হিসাব মিলেছে') : words(locale, 'Keep the records connected', 'তথ্যের সঙ্গে নথিও রাখুন')}</strong></div>{discrepancy && <span>{money(Math.abs(payments.data!.discrepancy_minor_units) / 100, locale)}</span>}<p>{discrepancy ? words(locale, 'Your account stays intact. Add another payment record or review the amount before using it.', 'আপনার বক্তব্য থেকে যাবে। অঙ্কটি ব্যবহারের আগে আরেকটি নথি দিন বা মিলিয়ে নিন।') : words(locale, 'A source link shows where information came from. You decide whether it is correct.', 'সূত্র থেকে তথ্যের উৎস বোঝা যায়। তথ্য ঠিক আছে কি না আপনি নিশ্চিত করবেন।')}</p></motion.div>
            <div className="ex-work-links"><button onClick={()=>openCanvas('timeline')}><span><Glyph name="link" size={19}/></span><div><strong>{words(locale,'Follow the evidence story','সূত্রসহ ঘটনাগুলো দেখুন')}</strong><small>{words(locale,'Messages, payments, and promises. Each linked to its original.','মেসেজ, টাকা ও প্রতিশ্রুতির কথা—মূল সূত্রের সাথেই।')}</small></div><Glyph name="arrow" size={17}/></button><button onClick={()=>openCanvas('reply')}><span><Glyph name="send" size={18}/></span><div><strong>{words(locale,'A seller replied. What comes next?','বিক্রেতা উত্তর দিয়েছেন। এবার কী বলবেন?')}</strong><small>{words(locale,'Compare their response with your records. Prepare your own reply.','তার কথার সাথে নিজের নথি মিলিয়ে উত্তর তৈরি করুন।')}</small></div><Glyph name="arrow" size={17}/></button><button onClick={()=>openCanvas('handoff')}><span><Glyph name="file" size={19}/></span><div><strong>{words(locale,'Prepare the official handoff','জমা দেওয়ার প্রস্তুতি নিন')}</strong><small>{words(locale,'Checked details. A reviewed draft. Your next step, ready.','মিলিয়ে দেখা তথ্য ও খসড়া নিয়ে পরের ধাপে।')}</small></div><Glyph name="arrow" size={17}/></button></div>
            {!!readyFacts.length && <section className="ag-findings"><div className="ag-section-heading"><span>{words(locale, 'THE IMPORTANT DETAILS', 'দরকারি তথ্যগুলো')}</span><button onClick={() => openCanvas('review')}>{words(locale, 'Review all', 'সব তথ্য দেখুন')}<Glyph name="arrow" size={14} /></button></div>{(needsReview.length ? needsReview : readyFacts).slice(0, 5).map(fact => <button className="ag-finding" key={fact.id} onClick={() => setLens(fact.id)}><span>{fieldLabel(fact.field_name, locale)}</span><strong>{factValue(fact, locale)}</strong><span className="ag-origin">{originLabel(fact.origin, locale)}<Glyph name="link" size={13} /></span></button>)}{needsReview.length > 0 && <div className="ag-confirm-facts"><Button tone="secondary" busy={confirming} onClick={confirmDetails}><Glyph name="check" size={15}/>{words(locale, 'These details look right', '\u09a6\u09c7\u0996\u09be\u09a8\u09cb \u09a4\u09a5\u09cd\u09af\u0997\u09c1\u09b2\u09cb \u09a0\u09bf\u0995 \u0986\u099b\u09c7')}</Button><button onClick={()=>openCanvas('review')}>{words(locale,'I need to correct something','\u0995\u09bf\u099b\u09c1 \u09a4\u09a5\u09cd\u09af \u09ac\u09a6\u09b2\u09be\u09a4\u09c7 \u099a\u09be\u0987')}</button></div>}</section>}
            {lastExternal && <section className="ag-change-briefing"><span className="ag-eyebrow">{words(locale, 'NEW INFORMATION, KEPT IN CONTEXT', 'নতুন তথ্য, আগের ঘটনার সঙ্গেই')}</span><h3>{words(locale, 'Your latest update', 'আপনার সর্বশেষ খবর')}</h3><p>{lastExternal.description}</p><span>{formatDate(lastExternal.created_at, locale, true)}</span><Button tone="secondary" onClick={() => openCanvas('activity')}>{words(locale, 'Inspect what changed', 'কী বদলেছে দেখুন')}<Glyph name="arrow" size={15} /></Button></section>}
            <div className="ag-next-step"><div><span className="ag-eyebrow">{words(locale, 'A CONSIDERED NEXT STEP', 'বুঝেশুনে পরের ধাপ')}</span><h3>{words(locale, 'See the conditions. Keep the final say.', 'শর্তগুলো দেখুন। সিদ্ধান্ত নিন নিজে।')}</h3></div><Button tone="secondary" onClick={() => openCanvas('paths')}>{words(locale, 'Explore next steps', 'করণীয় দেখুন')}<Glyph name="arrow" size={15} /></Button></div>
            <button className="ag-story-disclosure" onClick={() => setShowStory(!showStory)} aria-expanded={showStory}><Glyph name="file" size={16} />{words(locale, 'Your original story', 'আপনার মূল ঘটনা')}<span>{showStory ? '−' : '+'}</span></button>{showStory && <p className="ag-original-story">{record.story_narrative}</p>}
          </>}
          {canvas === 'evidence' && <EvidenceVault locale={locale} />}
          {canvas === 'timeline' && <EvidenceStory locale={locale} caseId={caseId} refreshKey={workKey} working={agent.running || uploading} onChanged={refreshWork} onRead={() => void start('resolve')} onAddFiles={() => fileInput.current?.click()} onVault={() => openCanvas('evidence')} onDraft={() => { void start('draft'); openCanvas('draft'); }} onReply={() => openCanvas('reply')} />}
          {canvas === 'reply' && <ReplyPreparation locale={locale} caseId={caseId} version={record.row_version} isDemo={record.is_demo} onChanged={refreshWork} onStory={() => openCanvas('timeline')} />}
          {canvas === 'handoff' && <FilingHandoff locale={locale} caseId={caseId} version={record.row_version} onFacts={() => openCanvas('review')} onDraft={() => openCanvas('draft')} />}
          {canvas === 'review' && <FactReview locale={locale} />}
          {canvas === 'paths' && <Paths locale={locale} />}
          {canvas === 'whatif' && <TryChange locale={locale} caseId={caseId} onApply={() => { refreshWork(); void start('assess'); }} />}
          {canvas === 'draft' && <ActionStudio locale={locale} initialTab="document" onHandoff={() => openCanvas('handoff')} />}
          {canvas === 'activity' && <CaseActivity locale={locale} />}
        </motion.div></AnimatePresence>
        <footer className="ag-canvas-footer"><Glyph name="shield" size={13} />{words(locale, 'Your records stay private. You review every external action.', 'আপনার নথি ব্যক্তিগত থাকে। বাইরের প্রতিটি পদক্ষেপ আগে আপনি দেখবেন।')}</footer>
      </section>
    </div>
    <input ref={fileInput} type="file" hidden multiple accept="image/*,application/pdf,audio/*" onChange={event => void addFiles(event.target.files)} aria-label={words(locale, 'Add evidence records', 'নথি ও প্রমাণ যোগ করুন')} />
    <EvidenceLens caseId={caseId} factId={lens} locale={locale} onClose={() => setLens(null)} />
    <Modal wide open={!!replay} onClose={() => setReplay(null)} title={words(locale, 'Recorded work, open to inspection', 'আগের কাজের রেকর্ড খুলে দেখুন')}><div className="ag-history-list">{agent.history.map(item => <button key={item.id} onClick={() => setReplay(item)} aria-pressed={replay?.id === item.id}><span>{formatDate(item.created_at, locale, true)}</span><Status>{statusLabel(item.status, locale)}</Status></button>)}</div>{replay && <><Notice>{words(locale, `Recorded execution · case version ${replay.case_version}. Opening this does not run it again.`, `কাজের রেকর্ড · অভিযোগের সংস্করণ ${replay.case_version}। এটি দেখলে কাজটি আবার চলবে না।`)}</Notice><ol className="ag-task-list">{replay.stages.map((stage, index) => <Stage key={index} stage={stage} locale={locale} />)}</ol></>}</Modal>
  </div></MotionConfig>;
}
