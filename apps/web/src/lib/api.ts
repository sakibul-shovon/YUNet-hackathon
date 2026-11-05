/** Ebarki authenticated transport and coordinated browser-session transitions. */
export const SESSION_EVENT = 'ebarki:session-changed';
export const SESSION_STORAGE_EVENT = 'ebarki_session_event';
const SESSION_KEYS = ['ebarki_token', 'cc_token', 'ebarki_principal_id', 'cc_principal_id'];
let guestSessionRequest: Promise<string> | null = null;
let logoutRequest: Promise<void> | null = null;
let changingSession = false;
let generation = 0;

type SessionCredentials = { access_token?: string | null; principal_id: string };
export function invalidateSessionRequests() { generation += 1; }
function storedToken() { return localStorage.getItem('ebarki_token') || localStorage.getItem('cc_token') || ''; }
function storeCredentials(session: SessionCredentials) {
  if (session.access_token) for (const key of ['ebarki_token', 'cc_token']) localStorage.setItem(key, session.access_token);
  for (const key of ['ebarki_principal_id', 'cc_principal_id']) localStorage.setItem(key, session.principal_id);
}
function announceSession(type: 'signed_in' | 'signed_out') {
  const detail = { type, nonce: crypto.randomUUID() };
  localStorage.setItem(SESSION_STORAGE_EVENT, JSON.stringify(detail));
  window.dispatchEvent(new CustomEvent(SESSION_EVENT, { detail }));
}
export function rememberClientSession(session: SessionCredentials) {
  invalidateSessionRequests();
  storeCredentials(session);
  announceSession('signed_in');
}
export async function logoutClientSession(): Promise<void> {
  if (logoutRequest) return logoutRequest;
  changingSession = true;
  invalidateSessionRequests();
  logoutRequest = (async () => {
    // A pending bootstrap can set a cookie even if its response is ignored.
    // Finish it before the logout request so that cookie is revoked as well.
    await guestSessionRequest?.catch(() => '');
    const token = storedToken();
    const response = await fetch('/api/v1/auth/logout', {
      method: 'POST', credentials: 'include', cache: 'no-store',
      signal: AbortSignal.timeout(15000),
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    });
    if (!response.ok) throw new Error('Ebarki could not end the session. Try logging out again.');
    for (const key of SESSION_KEYS) localStorage.removeItem(key);
    announceSession('signed_out');
  })();
  try { await logoutRequest; }
  finally { logoutRequest = null; changingSession = false; }
}
function parseJwtExp(token: string): number | null {
  try {
    const part = token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/');
    const data = JSON.parse(atob(part));
    return typeof data.exp === 'number' ? data.exp : null;
  } catch { return null; }
}
export async function getClientSessionToken(forceRefresh = false): Promise<string> {
  if (typeof window === 'undefined' || changingSession) return '';
  if (!forceRefresh) {
    const token = storedToken();
    const expiry = token && parseJwtExp(token);
    if (expiry && expiry > Date.now()/1000 + 30) return token;
  }
  if (guestSessionRequest) return guestSessionRequest;
  const current = generation;
  guestSessionRequest = (async () => {
    const response = await fetch('/api/v1/auth/guest', {
      method: 'POST', credentials: 'include', headers: { 'Content-Type': 'application/json' },
      signal: AbortSignal.timeout(15000),
    });
    if (!response.ok) return '';
    const session = await response.json() as SessionCredentials;
    if (generation !== current || changingSession || !session.access_token) return '';
    storeCredentials(session);
    return session.access_token;
  })();
  try { return await guestSessionRequest; }
  finally { guestSessionRequest = null; }
}
function credentialsEndpoint(input: RequestInfo | URL) {
  const value = typeof input === 'string' ? input : input instanceof URL ? input.href : input.url;
  return /\/auth\/(?:login|admin-login|register|judge-demo|judge-admin-demo|guest|logout)(?:[?#]|$)/.test(value);
}
export async function apiFetch(input: RequestInfo | URL, init?: RequestInit): Promise<Response> {
  if (changingSession) throw new DOMException('Ebarki session is changing.', 'AbortError');
  const started = generation;
  const credentialRequest = credentialsEndpoint(input);
  let token = credentialRequest ? '' : await getClientSessionToken();
  if (changingSession || started !== generation) throw new DOMException('Ebarki session is changing.', 'AbortError');
  const current = generation;
  const headers = new Headers(init?.headers);
  if (token && !headers.has('Authorization')) headers.set('Authorization', `Bearer ${token}`);
  let response = await fetch(input, { ...init, headers, credentials: 'include' });
  if (generation !== current || changingSession) throw new DOMException('Ebarki session changed.', 'AbortError');
  // A failed credential submission must never bootstrap a guest or retry a password.
  if (response.status === 401 && !credentialRequest && typeof window !== 'undefined') {
    token = await getClientSessionToken(true);
    if (token && generation === current && !changingSession) {
      headers.set('Authorization', `Bearer ${token}`);
      response = await fetch(input, { ...init, headers, credentials: 'include' });
    }
  }
  if (generation !== current || changingSession) throw new DOMException('Ebarki session changed.', 'AbortError');
  return response;
}
