'use client';
import { useEffect, useRef, useState } from 'react';
import { send } from '@/features/workspace/data';
import { Button, Field, Glyph, Modal, Notice, words } from '@/features/workspace/ui';
import { AgentMark } from './AgentMark';

type Recognition = { lang: string; continuous: boolean; interimResults: boolean; start: () => void; stop: () => void; abort: () => void; onresult: ((event: { resultIndex: number; results: ArrayLike<{ isFinal: boolean; 0: { transcript: string } }> }) => void) | null; onerror: (() => void) | null; onend: (() => void) | null; onstart: (() => void) | null };
export type ComposeSource = { mode: 'message' | 'voice' | 'transcript'; evidenceId?: string; filename?: string };

export function SourceComposer({ compose, locale, caseId, version, onClose, onSaved }: { compose: ComposeSource | null; locale: string; caseId: string; version: number; onClose: () => void; onSaved: () => void }) {
  const [text, setText] = useState(''); const [label, setLabel] = useState(''); const [interim, setInterim] = useState('');
  const [listening, setListening] = useState(false); const [busy, setBusy] = useState(false); const [error, setError] = useState('');
  const recognition = useRef<Recognition | null>(null); const spoken = useRef('');
  useEffect(() => { if (compose) { setText(''); setLabel(compose.filename || words(locale, compose.mode === 'voice' ? 'My spoken account' : 'Messages I provided', compose.mode === 'voice' ? 'আমার মুখে বলা ঘটনা' : 'আমার দেওয়া মেসেজ')); setError(''); setInterim(''); } return () => recognition.current?.abort(); }, [compose, locale]);
  function listen() {
    if (listening) { recognition.current?.stop(); return; }
    const Speech = (window as unknown as { SpeechRecognition?: new () => Recognition; webkitSpeechRecognition?: new () => Recognition }).SpeechRecognition || (window as unknown as { webkitSpeechRecognition?: new () => Recognition }).webkitSpeechRecognition;
    if (!Speech) { setError(words(locale, 'Voice typing is unavailable in this browser. You can write or paste your account below.', 'এই browser-এ মুখে বলে লেখা যাচ্ছে না। নিচে ঘটনা লিখে বা paste করে দিন।')); return; }
    spoken.current = text; const instance = new Speech(); instance.lang = locale === 'bn' ? 'bn-BD' : 'en-US'; instance.continuous = true; instance.interimResults = true;
    instance.onstart = () => { setListening(true); setError(''); };
    instance.onresult = event => { let partial = ''; for (let i = event.resultIndex; i < event.results.length; i++) { const result = event.results[i]; if (result.isFinal) spoken.current = `${spoken.current} ${result[0].transcript}`.trim(); else partial += result[0].transcript; } setText(spoken.current); setInterim(partial); };
    instance.onerror = () => { setListening(false); setError(words(locale, 'Voice typing stopped. Check microphone permission or continue by typing.', 'মুখে বলে লেখা থেমে গেছে। মাইক্রোফোনের অনুমতি দেখুন, অথবা লিখে এগিয়ে যান।')); };
    instance.onend = () => { setListening(false); setInterim(''); }; recognition.current = instance;
    try { instance.start(); } catch { setError(words(locale, 'The microphone could not start. Your text is still here.', 'মাইক্রোফোন চালু হয়নি। আপনার লেখাটি ঠিক আছে।')); }
  }
  async function save() {
    recognition.current?.stop(); setBusy(true); setError('');
    try { await send(`cases/${caseId}/connected-records/sources`, { text: text.trim(), label, source_type: compose?.mode === 'voice' ? 'voice_dictation' : compose?.mode === 'transcript' ? 'manual_transcript' : 'pasted_message', evidence_id: compose?.evidenceId || null, expected_version: version }); onSaved(); onClose(); }
    catch { setError(words(locale, 'This could not be saved. If your case changed, close this window and refresh before trying again.', 'লেখাটি রাখা যায়নি। অভিযোগের তথ্য বদলে থাকলে এই window বন্ধ করে নতুন তথ্য আনুন, তারপর আবার চেষ্টা করুন।')); }
    finally { setBusy(false); }
  }
  return <Modal open={!!compose} onClose={onClose} title={words(locale, compose?.mode === 'voice' ? 'Tell it in your own words.' : compose?.mode === 'transcript' ? 'Add what you can read.' : 'Bring the conversation into view.', compose?.mode === 'voice' ? 'নিজের ভাষায় ঘটনা বলুন।' : compose?.mode === 'transcript' ? 'যা পড়তে পারছেন, লিখে দিন।' : 'মেসেজগুলো একসঙ্গে দেখুন।')} wide>
    <div className="ex-compose"><div className="ex-compose-intro"><AgentMark state={listening ? 'working' : 'ready'} /><p>{words(locale, compose?.mode === 'voice' ? 'Speak naturally. Check the words, names, dates, and amounts before keeping them.' : 'Preserve the wording and any dates shown. Ebarki will connect the important moments for your review.', compose?.mode === 'voice' ? 'যেভাবে স্বচ্ছন্দ লাগে সেভাবেই বলুন। রাখার আগে লেখা, নাম, তারিখ আর টাকার অঙ্ক মিলিয়ে নিন।' : 'মূল কথাগুলো ও সঙ্গে থাকা তারিখ লিখুন। Ebarki গুরুত্বপূর্ণ ঘটনাগুলো একসঙ্গে সাজিয়ে দেখাবে।')}</p></div>
      {compose?.mode === 'voice' && <div className={`ex-dictation ${listening ? 'is-listening' : ''}`}><Button tone={listening ? 'danger' : 'secondary'} onClick={listen}><Glyph name={listening ? 'stop' : 'mic'} size={18} />{words(locale, listening ? 'Stop voice typing' : 'Start voice typing', listening ? 'বলা শেষ করুন' : 'মুখে বলে লিখুন')}</Button><span role="status">{words(locale, listening ? 'Listening. Your words appear below.' : 'Uses your browser’s speech service, which may process audio online. Microphone permission is required.', listening ? 'শুনছি। আপনার কথা নিচে লেখা হবে।' : 'ব্রাউজারের speech service ব্যবহার হবে; কথা অনলাইনে প্রসেস হতে পারে। মাইক্রোফোন ব্যবহারের অনুমতি লাগবে।')}</span></div>}
      <Field label={words(locale, 'A name for this source', 'এই লেখাটির নাম')}><input value={label} onChange={event => setLabel(event.target.value)} maxLength={180} /></Field>
      <Field label={words(locale, 'Original words', 'মূল কথাগুলো')}><textarea autoFocus={compose?.mode !== 'voice'} value={text} onChange={event => setText(event.target.value)} rows={8} maxLength={10000} placeholder={words(locale, 'Keep dates and who said what, if they are shown in your record.', 'নথিতে তারিখ ও কে কী বলেছেন থাকলে সেগুলোও লিখুন।')} /></Field>
      {interim && <p className="ex-interim" aria-live="polite">{interim}</p>}{error && <Notice tone="attention">{error}</Notice>}
      <footer><span>{words(locale, 'Saved as information you provided. You can review each linked moment.', 'আপনার দেওয়া তথ্য হিসেবে রাখা হবে। প্রতিটি ঘটনা পরে মিলিয়ে দেখতে পারবেন।')}</span><Button busy={busy} disabled={listening || text.trim().length < 4 || label.trim().length < 2} onClick={save}>{words(locale, 'Keep & connect the moments', 'রেখে ঘটনাগুলো সাজান')}<Glyph name="arrow" size={16} /></Button></footer>
    </div>
  </Modal>;
}
