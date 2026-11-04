'use client';
import { useCallback, useEffect, useRef, useState } from 'react';
import { apiFetch } from '@/lib/api';
import { request, send } from '@/features/workspace/data';

export type AgentStage = {
  stage_name: string; method: string; status: string; started_at: string;
  finished_at?: string; duration_ms: number | null; details: Record<string, unknown>;
};
export type AgentRun = {
  id: string; operation: string; case_version: number; status: string;
  cancel_requested: boolean; created_at: string; finished_at?: string;
  stages: AgentStage[]; result: Record<string, unknown>; error_code?: string;
  events?: Array<{ id: string; sequence: number; type: string; task?: string; timestamp?: string }>;
};
const active = (run: AgentRun | null) => !!run && ['running', 'queued'].includes(run.status);

export function useAgentRun(caseId: string, locale: string, onComplete: () => void) {
  const [history, setHistory] = useState<AgentRun[]>([]);
  const [run, setRun] = useState<AgentRun | null>(null);
  const [loading, setLoading] = useState(true);
  const [starting, setStarting] = useState(false);
  const [error, setError] = useState('');
  const complete = useRef(onComplete);
  complete.current = onComplete;
  const notified = useRef(new Set<string>());

  const reload = useCallback(async () => {
    try {
      const records = await request<AgentRun[]>(`cases/${caseId}/runs`);
      setHistory(records); setRun(records[0] || null); setError('');
    } catch { setError('history'); }
    finally { setLoading(false); }
  }, [caseId]);
  useEffect(() => { void reload(); }, [reload]);

  useEffect(() => {
    if (!active(run)) return;
    const id = run!.id;
    const abort = new AbortController();
    let timer: ReturnType<typeof setTimeout> | undefined;
    function accept(next: AgentRun) {
      if (abort.signal.aborted) return true;
      setRun(next);
      if (!active(next)) {
        setHistory(items => [next, ...items.filter(item => item.id !== next.id)]);
        if (!notified.current.has(next.id)) { notified.current.add(next.id); complete.current(); }
        return true;
      }
      return false;
    }
    async function poll() {
      try {
        const next = await request<AgentRun>(`cases/${caseId}/runs/${id}`, { signal: abort.signal });
        if (!accept(next)) timer = setTimeout(poll, 1000);
      } catch { if (!abort.signal.aborted) timer = setTimeout(poll, 2000); }
    }
    async function connect() {
      try {
        const response = await apiFetch(`/api/v1/cases/${caseId}/runs/${id}/events`, { signal: abort.signal, cache: 'no-store' });
        if (!response.ok || !response.body) throw new Error('Stream unavailable');
        const reader = response.body.getReader(); const decoder = new TextDecoder(); let buffer = '';
        while (!abort.signal.aborted) {
          const part = await reader.read(); if (part.done) break;
          buffer += decoder.decode(part.value, { stream: true });
          const events = buffer.split('\n\n'); buffer = events.pop() || '';
          for (const event of events) {
            const data = event.split('\n').find(line => line.startsWith('data: '));
            if (event.includes('event: run') && data && accept(JSON.parse(data.slice(6)))) {
              await reader.cancel(); return;
            }
          }
        }
        if (!abort.signal.aborted) void poll();
      } catch { if (!abort.signal.aborted) void poll(); }
    }
    void connect();
    return () => { abort.abort(); if (timer) clearTimeout(timer); };
  }, [run?.id, run?.status, caseId]);

  const start = useCallback(async (operation = 'resolve', version?: number) => {
    setStarting(true); setError('');
    try {
      const next = await send<AgentRun>(`cases/${caseId}/runs`, { operation, locale, expected_version: version });
      setRun(next);
      if (!active(next) && !notified.current.has(next.id)) { notified.current.add(next.id); complete.current(); }
      return next;
    } catch { setError('start'); void reload(); return null; }
    finally { setStarting(false); }
  }, [caseId, locale, reload]);
  const stop = useCallback(async () => {
    if (!run || !active(run)) return;
    try { setRun(await send<AgentRun>(`cases/${caseId}/runs/${run.id}/cancel`)); }
    catch { setError('stop'); }
  }, [caseId, run]);
  return { run, history, loading, starting, error, start, stop, reload, running: active(run) };
}
