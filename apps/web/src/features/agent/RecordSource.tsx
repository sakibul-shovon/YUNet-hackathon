'use client';
import { useEffect, useRef, useState } from 'react';
import { motion } from 'motion/react';
import { apiFetch } from '@/lib/api';
import { useResource } from '@/features/workspace/data';
import { Button, ErrorPanel, Glyph, Loading, Modal, Notice, words } from '@/features/workspace/ui';
import type { ConnectedRecords, ConnectedSource, RecordLocator } from './experience-types';

export function sourceMethod(source: ConnectedSource, locale: string) {
  if (source.is_demo) return words(locale, 'Fictional conversation · demo only', 'নমুনার কথোপকথন');
  const labels: Record<string, [string, string]> = {
    native_pdf: ['Read from the PDF', 'PDF থেকে পড়া'], gemini_vision: ['AI reading · review needed', 'AI দিয়ে পড়া · মিলিয়ে দেখুন'], groq_vision: ['AI reading · review needed', 'AI দিয়ে পড়া · মিলিয়ে দেখুন'],
    groq_transcription: ['AI transcript · review needed', 'AI-এর transcript · মিলিয়ে দেখুন'], user_account: ['Your original account', 'আপনার মূল বক্তব্য'],
    pasted_text: ['Text you provided', 'আপনার দেওয়া লেখা'], pasted_message: ['Message you provided', 'আপনার দেওয়া মেসেজ'],
    voice_dictation: ['Your spoken account', 'আপনার মুখে বলা ঘটনা'], manual_transcript: ['Transcript you provided', 'আপনার দেওয়া transcript'],
    manual_required: ['Open for your review', 'নিজে পড়ে দেখুন'], not_read: ['Ready to read', 'পড়ার অপেক্ষায়'],
  };
  return words(locale, ...(labels[source.method] || ['Original record', 'মূল নথি']));
}
function time(value: number) { return `${Math.floor(value / 60)}:${Math.floor(value % 60).toString().padStart(2, '0')}`; }

export function RecordSource({ source, locator, caseId, locale }: { source: ConnectedSource; locator?: RecordLocator | null; caseId: string; locale: string }) {
  const [url, setUrl] = useState(''); const [error, setError] = useState(false); const [original, setOriginal] = useState(false);
  const [bars, setBars] = useState<number[]>([]); const [position, setPosition] = useState(0);
  const audio = useRef<HTMLAudioElement>(null); const page = locator?.page || 1;
  const fileId = source.evidence_id || source.id;
  const isFile = source.mime_type !== 'text/plain';
  const pdf = source.mime_type === 'application/pdf'; const isAudio = source.mime_type.startsWith('audio/');
  useEffect(() => { setOriginal(false); }, [source.id]);
  useEffect(() => {
    setUrl(''); setError(false); setBars([]); if (!isFile) return;
    const abort = new AbortController(); let objectUrl = '';
    const endpoint = pdf && !original ? `cases/${caseId}/evidence/${fileId}/page-preview?page=${page}` : `cases/${caseId}/evidence/${fileId}/preview`;
    apiFetch(`/api/v1/${endpoint}`, { signal: abort.signal, cache: 'no-store' }).then(async response => {
      if (!response.ok) throw new Error(); return response.blob();
    }).then(async blob => {
      if (abort.signal.aborted) return;
      objectUrl = URL.createObjectURL(blob); setUrl(objectUrl);
      if (isAudio) {
        try {
          const context = new AudioContext();
          try {
            const buffer = await context.decodeAudioData(await blob.arrayBuffer());
            const channel = buffer.getChannelData(0); const size = Math.max(1, Math.floor(channel.length / 64));
            const levels = Array.from({ length: 64 }, (_, i) => { let peak = 0; for (let j = i * size; j < Math.min(channel.length, (i + 1) * size); j += 20) peak = Math.max(peak, Math.abs(channel[j])); return peak; });
            const maximum = Math.max(.01, ...levels);
            if (!abort.signal.aborted) setBars(levels.map(level => Math.max(.04, level / maximum)));
          } finally { await context.close(); }
        } catch { /* The playable original remains available if waveform decoding is unsupported. */ }
      }
    }).catch(() => { if (!abort.signal.aborted) setError(true); });
    return () => { abort.abort(); if (objectUrl) URL.revokeObjectURL(objectUrl); };
  }, [caseId, fileId, source.id, page, original, pdf, isFile, isAudio]);
  useEffect(() => { if (audio.current && typeof locator?.start === 'number') { audio.current.currentTime = locator.start; setPosition(locator.start); } }, [locator?.start, url]);
  const box = locator?.box;
  return <section className="ex-source" aria-label={words(locale, 'Original source', 'মূল সূত্র')}>
    <header className="ex-source-heading"><Glyph name={isAudio ? 'mic' : 'file'} size={19} /><div><strong>{source.id === 'account' ? words(locale, 'Your original account', 'আপনার মূল বক্তব্য') : source.filename}</strong><span>{sourceMethod(source, locale)}</span></div>{locator?.page && <span className="ex-page">{words(locale, 'P.', 'পৃষ্ঠা')} {locator.page.toLocaleString(locale === 'bn' ? 'bn-BD' : 'en')}</span>}</header>
    <div className="ex-source-body">
      {isFile ? error ? <Notice tone="attention">{words(locale, 'The preview is unavailable. You can try the original file.', 'Preview এখন খোলা যাচ্ছে না। মূল ফাইলটি খুলে দেখতে পারেন।')}<Button tone="quiet" onClick={() => setOriginal(true)}>{words(locale, 'Open original', 'মূল ফাইল খুলুন')}</Button></Notice> : !url ? <Loading locale={locale} /> : isAudio ? <>
        {!!bars.length && <div className="ex-waveform" aria-hidden="true">{bars.map((bar, index) => <i key={index} style={{ height: `${bar * 80}%` }} />)}</div>}
        <audio ref={audio} src={url} controls preload="metadata" onTimeUpdate={event => setPosition(event.currentTarget.currentTime)} />
        <div className="ex-audio-segments">{source.lines?.filter(line => typeof line.start === 'number').map((line, index) => <button key={index} className={position >= line.start! && position < line.end! ? 'is-playing' : ''} onClick={() => { if (audio.current) { audio.current.currentTime = line.start!; void audio.current.play().catch(() => {}); } }}><span>{time(line.start!)}</span><p>{line.text}</p><Glyph name="play" size={13} /></button>)}</div>
      </> : pdf && original ? <iframe className="ex-pdf-original" src={`${url}#page=${page}`} title={source.filename} /> : <div className="ex-source-image"><img src={url} alt={source.filename} />{box?.length === 4 && <motion.span key={`${source.id}:${locator?.quote}`} className="ex-source-highlight" initial={{ opacity: 0 }} animate={{ opacity: 1 }} style={{ left: `${box[0] * 100}%`, top: `${box[1] * 100}%`, width: `${(box[2] - box[0]) * 100}%`, height: `${(box[3] - box[1]) * 100}%` }} />}</div> : <div className={`ex-source-text ${source.method === 'pasted_message' ? 'is-conversation' : ''}`}>{source.text.split(/\n|(?<=[.!?।])\s+/).filter(Boolean).map((line, index) => <p key={index} className={locator?.quote && line.includes(locator.quote) ? 'is-linked' : ''}>{line}</p>)}</div>}
    </div>
    {locator?.quote && <motion.blockquote key={locator.quote} className="ex-linked-quote" initial={{ opacity: 0, y: 5 }} animate={{ opacity: 1, y: 0 }}><span><i />{words(locale, 'THE LINKED PASSAGE', 'যে অংশ থেকে তথ্যটি এসেছে')}</span><p>{locator.quote}</p></motion.blockquote>}
    {pdf && !original && !error && <button className="ex-text-action" onClick={() => setOriginal(true)}>{words(locale, 'Open full PDF', 'পুরো PDF খুলুন')}<Glyph name="external" size={13} /></button>}
    {isFile&&source.text&&<details className="ex-extracted-text"><summary>{words(locale,'Read the extracted text','পড়া লেখাটি দেখুন')}</summary><p>{source.text}</p></details>}
    <p className="ex-source-footnote">{words(locale, 'This shows where the statement came from. Review its meaning and accuracy.', 'বক্তব্যটি কোথা থেকে এসেছে এখানে দেখুন। অর্থ ও তথ্য ঠিক আছে কি না মিলিয়ে নিন।')}</p>
  </section>;
}

export function RecordSourceModal({ caseId, locator, locale, onClose }: { caseId: string; locator: RecordLocator | null; locale: string; onClose: () => void }) {
  const records = useResource<ConnectedRecords>(locator ? `cases/${caseId}/connected-records` : null);
  const source = records.data?.sources.find(item => item.id === locator?.source_id);
  return <Modal open={!!locator} onClose={onClose} title={words(locale, 'Follow the source', 'মূল সূত্র খুলে দেখুন')} wide>{records.loading ? <Loading locale={locale} /> : records.error ? <ErrorPanel locale={locale} retry={records.reload} /> : source ? <RecordSource source={source} locator={locator} caseId={caseId} locale={locale} /> : <Notice>{words(locale, 'This source is no longer available in the case.', 'এই সূত্রটি এখন অভিযোগের সঙ্গে নেই।')}</Notice>}</Modal>;
}
