/**
 * Client-side authenticated fetch utility for ClaimCraft BD.
 *
 * Ensures every browser visitor has a stable anonymous guest token
 * persisted across navigations, tabs, and reloads in localStorage and HttpOnly cookies,
 * with proactive JWT expiration checks and automatic 401 retry.
 */

let guestSessionRequest: Promise<string> | null = null;

function parseJwtExp(token: string): number | null {
  try {
    const parts = token.split('.');
    if (parts.length < 2) return null;
    const base64 = parts[1].replace(/-/g, '+').replace(/_/g, '/');
    const jsonStr = decodeURIComponent(
      atob(base64)
        .split('')
        .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    );
    const payload = JSON.parse(jsonStr);
    return typeof payload.exp === 'number' ? payload.exp : null;
  } catch {
    return null;
  }
}

export async function getClientSessionToken(forceRefresh = false): Promise<string> {
  if (typeof window === 'undefined') return '';

  if (!forceRefresh) {
    const storedToken = localStorage.getItem('ebarki_token') || localStorage.getItem('cc_token');
    if (storedToken) {
      const exp = parseJwtExp(storedToken);
      // Valid if remaining lifetime > 30 seconds
      if (exp && exp > Math.floor(Date.now() / 1000) + 30) {
        return storedToken;
      }
    }
  }

  if (guestSessionRequest) return guestSessionRequest;
  guestSessionRequest = createGuestSession();
  try { return await guestSessionRequest; } finally { guestSessionRequest = null; }
}

async function createGuestSession(): Promise<string> {
  try {
    const res = await fetch('/api/v1/auth/guest', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
    });
    if (res.ok) {
      const data = await res.json();
      if (data.access_token) {
        localStorage.setItem('cc_token', data.access_token);
        localStorage.setItem('cc_principal_id', data.principal_id);
        localStorage.setItem('ebarki_token', data.access_token);
        localStorage.setItem('ebarki_principal_id', data.principal_id);
        return data.access_token;
      }
    }
  } catch (err) {
    console.error('Failed to establish guest session:', err);
  }

  return localStorage.getItem('ebarki_token') || localStorage.getItem('cc_token') || '';
}

export async function apiFetch(input: RequestInfo | URL, init?: RequestInit): Promise<Response> {
  let token = await getClientSessionToken();
  const headers = new Headers(init?.headers);

  if (token && !headers.has('Authorization')) {
    headers.set('Authorization', `Bearer ${token}`);
  }

  let res = await fetch(input, {
    ...init,
    headers,
    credentials: 'include',
  });

  // If 401 Unauthorized, token might have expired or principal was recreated.
  // Refresh token once and retry.
  if (res.status === 401 && typeof window !== 'undefined') {
    const freshToken = await getClientSessionToken(true);
    if (freshToken) {
      headers.set('Authorization', `Bearer ${freshToken}`);
      res = await fetch(input, {
        ...init,
        headers,
        credentials: 'include',
      });
    }
  }

  return res;
}
