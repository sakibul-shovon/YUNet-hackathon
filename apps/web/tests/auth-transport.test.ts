import { beforeEach, expect, it, vi } from 'vitest';

const token = `test.${btoa(JSON.stringify({ exp: Date.now()/1000 + 3600 }))}.test`;
const json = (data: unknown) => new Response(JSON.stringify(data), { status: 200 });
beforeEach(() => { vi.resetModules(); localStorage.clear(); vi.unstubAllGlobals(); });

it.each(['login', 'admin-login', 'register'])('never guest-bootstraps or retries a failed %s credential submission', async endpoint => {
  const fetch = vi.fn().mockResolvedValue(new Response(null, { status: 401 })); vi.stubGlobal('fetch', fetch);
  const { apiFetch } = await import('@/lib/api');
  expect((await apiFetch(`/api/v1/auth/${endpoint}`, { method: 'POST' })).status).toBe(401);
  expect(fetch).toHaveBeenCalledTimes(1);
});

it('waits for a pending guest bootstrap before revoking its cookie and never restores its token', async () => {
  let resolveGuest!: (response: Response) => void;
  const fetch = vi.fn((path: string) => path.endsWith('/guest') ? new Promise<Response>(resolve => { resolveGuest = resolve; }) : Promise.resolve(new Response(null, { status: 204 })));
  vi.stubGlobal('fetch', fetch);
  const { getClientSessionToken, logoutClientSession } = await import('@/lib/api');
  const bootstrap = getClientSessionToken(); const logout = logoutClientSession();
  expect(fetch).toHaveBeenCalledTimes(1);
  resolveGuest(json({ access_token: token, principal_id: 'fictional-guest' }));
  expect(await bootstrap).toBe(''); await logout;
  expect(fetch.mock.calls.map(call => call[0])).toEqual(['/api/v1/auth/guest', '/api/v1/auth/logout']);
  expect(localStorage.getItem('ebarki_token')).toBeNull();
});

it('rejects a private response arriving after logout', async () => {
  localStorage.setItem('ebarki_token', token);
  let resolvePrivate!: (response: Response) => void;
  const fetch = vi.fn((path: string) => path.endsWith('/cases') ? new Promise<Response>(resolve => { resolvePrivate = resolve; }) : Promise.resolve(new Response(null, { status: 204 })));
  vi.stubGlobal('fetch', fetch);
  const { apiFetch, logoutClientSession } = await import('@/lib/api');
  const pending = apiFetch('/api/v1/cases');
  const rejected = expect(pending).rejects.toMatchObject({ name: 'AbortError' });
  await vi.waitFor(() => expect(resolvePrivate).toBeDefined());
  await logoutClientSession(); resolvePrivate(json({ private: 'Fictional private case' })); await rejected;
});

it('deduplicates concurrent logout clicks', async () => {
  const fetch = vi.fn().mockResolvedValue(new Response(null, { status: 204 })); vi.stubGlobal('fetch', fetch);
  const { logoutClientSession } = await import('@/lib/api');
  await Promise.all([logoutClientSession(), logoutClientSession()]); expect(fetch).toHaveBeenCalledTimes(1);
});

it('does not send a queued private request after its bootstrap is overtaken by logout', async () => {
  let resolveGuest!: (response: Response) => void;
  const fetch = vi.fn((path: string) => path.endsWith('/guest') ? new Promise<Response>(resolve => { resolveGuest = resolve; }) : Promise.resolve(new Response(null, { status: 204 })));
  vi.stubGlobal('fetch', fetch);
  const { apiFetch, logoutClientSession } = await import('@/lib/api');
  const pending = apiFetch('/api/v1/cases');
  const rejected = expect(pending).rejects.toMatchObject({ name: 'AbortError' });
  const logout = logoutClientSession();
  resolveGuest(json({ access_token: token, principal_id: 'fictional-guest' }));
  await logout; await rejected;
  expect(fetch.mock.calls.map(call => call[0])).toEqual(['/api/v1/auth/guest', '/api/v1/auth/logout']);
});
