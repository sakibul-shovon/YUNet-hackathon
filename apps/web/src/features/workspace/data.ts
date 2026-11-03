'use client';

import { useCallback, useEffect, useRef, useState } from 'react';
import { apiFetch } from '@/lib/api';

export class RequestError extends Error { constructor(message: string, public status: number) { super(message); } }
export async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await apiFetch(`/api/v1/${path.replace(/^\//, '')}`, { cache: 'no-store', ...init, headers: { ...(init?.body && typeof init.body === 'string' ? { 'Content-Type': 'application/json' } : {}), ...init?.headers } });
  if (!response.ok) { let message = `Request failed (${response.status})`; try { const data = await response.json(); const detail = data.detail ?? data.error; if (typeof detail === 'string') message = detail; else if (detail?.error?.message) message = detail.error.message; else if (detail?.message) message = detail.message; else if (Array.isArray(detail)) message = detail.map((item: { msg: string }) => item.msg).join('; '); } catch {} throw new RequestError(message, response.status); }
  if (response.status === 204) return undefined as T;
  return response.json();
}
export const send = <T,>(path: string, body?: unknown, method = 'POST') => request<T>(path, { method, ...(body !== undefined ? { body: JSON.stringify(body) } : {}) });
export function useResource<T>(path: string | null) {
  const [data, setData] = useState<T | null>(null); const [loading, setLoading] = useState(Boolean(path)); const [error, setError] = useState<RequestError | null>(null); const [revision, setRevision] = useState(0); const generation = useRef(0);
  const reload = useCallback(() => setRevision(value => value + 1), []);
  useEffect(() => { const run = ++generation.current; const controller = new AbortController(); setError(null); setData(null); if (!path) { setLoading(false); return; } setLoading(true); request<T>(path, { signal: controller.signal }).then(value => { if (generation.current === run) setData(value); }).catch(reason => { if (!controller.signal.aborted && generation.current === run) setError(reason); }).finally(() => { if (generation.current === run) setLoading(false); }); return () => controller.abort(); }, [path, revision]);
  return { data, setData, loading, error, reload };
}

export type CaseRecord = { id: string; title: string; display_reference: string; principal_id: string; lifecycle_status: string; row_version: number; merchant_name: string | null; story_narrative: string | null; incident_date: string | null; desired_outcomes: string[]; is_demo: boolean; created_at: string; updated_at: string; consent_status: string };
export type Fact = { id: string; field_name: string; field_type: string; typed_value: unknown; original_text: string; origin: string; is_active: boolean; created_case_version: number };
export type Evidence = { id: string; original_filename: string; detected_mime_type?: string; declared_mime_type: string; byte_size: number; status: string; rejection_reason?: string; rejection_code?: string; is_retryable?: boolean; guidance_en?: string; guidance_bn?: string; created_at: string; sha256_hash?: string };
export type Route = { route_id: string; rule_id: string; issue_type: string; status: string; reasons: string[]; source_dependencies: string[]; statutory_citations: string[]; allowed_actions: string[]; condition_trace: Array<Record<string, unknown>>; supported_remedies: string[]; unsupported_remedy_warnings: string[] };
export type Question = { question_key: string; fact_field: string; prompt_en: string; prompt_bn: string; question_type: string; options?: Array<{ value: string; label_en?: string; label_bn?: string; label?: string }>; relevance_rationale: string };
export type Assessment = { case_id: string; overall_status: string; primary_action: string; primary_action_title_en: string; primary_action_title_bn: string; routes: Route[]; next_best_question?: Question; source_cards: Array<Record<string, unknown>>; limitation_warning_en?: string; limitation_warning_bn?: string; days_remaining_in_limitation?: number; is_deadline_uncertain?: boolean };
export type Profile = { logged_in: boolean; principal_id: string; email: string; full_name: string; phone?: string; roles: string[]; access_token?: string; is_demo_judge?: boolean };
export type DocumentAST = { document_id: string; document_type: string; title: string; locale: string; created_at: string; sections: Array<{ section_id: string; section_title_en: string; section_title_bn: string; sentences: Array<{ sentence_id: string; text: string; statement_type: string; supporting_fact_id?: string; supporting_citation?: string; is_user_edited: boolean }> }>; evidence_index: Array<{ filename: string; mime_type: string }>; preparation_checklist: string[] };
export async function uploadEvidence(caseId: string, file: File) { const intent = await send<{ intent_id: string; upload_token: string }>('uploads/init', { case_id: caseId, declared_filename: file.name, declared_mime_type: file.type || 'application/octet-stream', declared_byte_size: file.size }); await request(`uploads/${intent.intent_id}/raw?token=${encodeURIComponent(intent.upload_token)}`, { method: 'PUT', body: file }); return send<Evidence>(`uploads/${intent.intent_id}/complete`); }
