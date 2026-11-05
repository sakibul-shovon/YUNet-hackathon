import { beforeEach, describe, expect, it, vi } from 'vitest';
import { act, render, screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import type { ReactNode } from 'react';
import { AuthSessionProvider } from '@/features/agent/AuthSession';
import { AccountMenu, LogoutButton } from '@/features/agent/AuthControls';
import { Access } from '@/features/agent/Access';
import { AdminConsole } from '@/features/workspace/Admin';
import { AppShell } from '@/features/workspace/AppShell';
import { AdminDashboardClient } from '@/app/[locale]/admin/AdminDashboardClient';
import { SESSION_EVENT } from '@/lib/api';

const navigation = vi.hoisted(() => ({ replace: vi.fn(), refresh: vi.fn(), push: vi.fn() }));
vi.mock('next/navigation', () => ({ useRouter: () => navigation, usePathname: () => '/en/cases' }));
vi.mock('next/image', () => ({ default: ({ priority: _priority, ...props }: Record<string, unknown>) => <img {...props} /> }));
vi.mock('@/features/agent/AgentMark', () => ({ AgentMark: () => <span /> }));

const consumer = { logged_in: true, principal_id: 'fictional-consumer', full_name: 'Fictional Buyer', email: 'buyer@example.test', roles: ['consumer'] };
const guest = { ...consumer, logged_in: false, roles: [], principal_id: 'fictional-guest' };
let profile = consumer;
let logoutStatus = 204;
let profileStatus = 200;
let requested: string[];
const json = (value: unknown, status = 200) => new Response(JSON.stringify(value), { status, headers: { 'Content-Type': 'application/json' } });
function mount(children: ReactNode, locale = 'en') { return render(<AuthSessionProvider locale={locale}>{children}</AuthSessionProvider>); }

beforeEach(() => {
  vi.clearAllMocks(); localStorage.clear(); profile = consumer; logoutStatus = 204; profileStatus = 200; requested = [];
  localStorage.setItem('ebarki_token', `test.${btoa(JSON.stringify({ exp: Date.now()/1000 + 3600 }))}.test`);
  vi.stubGlobal('fetch', vi.fn(async (input: RequestInfo | URL) => {
    const path = String(input); requested.push(path);
    if (path.endsWith('/auth/me')) return json(profile, profileStatus);
    if (path.endsWith('/auth/logout')) return new Response(null, { status: logoutStatus });
    if (path.endsWith('/auth/admin-login')) return json({ detail: 'Forbidden' }, 403);
    if (path.endsWith('/admin/stats')) return json({ metrics: { total_cases: 37, active_cases: 11 }, system_health: { database_engine: 'Query completed' } });
    if (path.endsWith('/knowledge/release')) return json({ release_id: 'fictional-release' });
    return json([]);
  }));
});

describe('Ebarki login route', () => {
  it.each([false, true])('redirects a signed-in consumer from login/register (register=%s)', async register => {
    mount(<Access locale="en" register={register} />);
    expect(screen.queryByLabelText('Email address')).not.toBeInTheDocument();
    await waitFor(() => expect(navigation.replace).toHaveBeenCalledWith('/en/cases'));
    expect(screen.queryByLabelText('Email address')).not.toBeInTheDocument();
  });
  it('redirects staff from ordinary and admin login to their portal', async () => {
    profile = { ...consumer, roles: ['admin'] };
    const view = mount(<Access locale="en" />);
    await waitFor(() => expect(navigation.replace).toHaveBeenCalledWith('/en/admin'));
    view.unmount(); navigation.replace.mockClear();
    mount(<Access locale="en" admin />);
    await waitFor(() => expect(navigation.replace).toHaveBeenCalledWith('/en/admin'));
  });
  it('shows a guest the normal login options after session resolution', async () => {
    profile = guest; mount(<Access locale="en" />);
    expect(await screen.findByLabelText('Email address')).toBeVisible();
    expect(screen.getByRole('link', { name: /Admin login\s*Authorized staff/ })).toHaveAttribute('href', '/en/admin/login');
    expect(navigation.replace).not.toHaveBeenCalled();
  });
  it('shows an error and retry when session lookup fails instead of claiming logged out', async () => {
    profileStatus = 503; mount(<Access locale="en" />);
    expect(await screen.findByRole('alert')).toBeVisible();
    expect(screen.queryByLabelText('Email address')).not.toBeInTheDocument();
    profileStatus = 200; profile = guest;
    await userEvent.click(screen.getByRole('button', { name: 'Try again' }));
    expect(await screen.findByLabelText('Email address')).toBeVisible();
  });
  it('lets a consumer try authorized staff login and truthfully reports forbidden access', async () => {
    mount(<Access locale="en" admin />);
    await userEvent.type(await screen.findByLabelText('Email address'), 'staff@example.test');
    await userEvent.type(screen.getByLabelText('Password'), 'fictional-password');
    await userEvent.click(screen.getByRole('button', { name: 'Log in' }));
    expect(await screen.findByRole('alert')).toHaveTextContent('Administrative access is not permitted');
    expect(requested.filter(path => path.includes('/auth/admin-login'))).toHaveLength(1);
    expect(requested.some(path => path.includes('/auth/guest'))).toBe(false);
    expect(navigation.replace).not.toHaveBeenCalled();
  });
  it('renders Judge Admin 1-Click Access and credentials autofill on the admin login page', async () => {
    profile = guest;
    mount(<Access locale="en" admin />);
    expect(await screen.findByRole('button', { name: /Judge Admin 1-Click Access/i })).toBeVisible();
    const autoFillBtn = screen.getByRole('button', { name: /Auto-fill password/i });
    expect(autoFillBtn).toBeVisible();
    await userEvent.click(autoFillBtn);
    expect(screen.getByLabelText('Email address')).toHaveValue('admin@claimcraft.bd');
    expect(screen.getByLabelText('Password')).toHaveValue('8sUb9caTA_s1sQ-8gY0L-Z5ePB3YYlUCl7n4zLsUI9s');
  });
});

describe('Ebarki visible logout', () => {
  it('opens an account menu, logs out on the server, clears credentials and redirects', async () => {
    localStorage.setItem('cc_token', 'legacy'); localStorage.setItem('ebarki_principal_id', consumer.principal_id);
    mount(<AccountMenu locale="en" />);
    await userEvent.click(await screen.findByLabelText('Your account'));
    expect(screen.getByRole('link', { name: 'Settings' })).toBeVisible();
    await userEvent.click(screen.getByRole('button', { name: 'Log out' }));
    await waitFor(() => expect(navigation.replace).toHaveBeenCalledWith('/en/login'));
    expect(requested).toContain('/api/v1/auth/logout');
    for (const key of ['ebarki_token', 'cc_token', 'ebarki_principal_id', 'cc_principal_id']) expect(localStorage.getItem(key)).toBeNull();
    expect(screen.queryByLabelText('Your account')).not.toBeInTheDocument();
  });
  it('keeps the session and offers retry when logout fails', async () => {
    logoutStatus = 503; mount(<LogoutButton locale="en" />);
    await userEvent.click(await screen.findByRole('button', { name: 'Log out' }));
    expect(await screen.findByRole('alert')).toHaveTextContent('You are still signed in');
    expect(localStorage.getItem('ebarki_token')).not.toBeNull(); expect(navigation.replace).not.toHaveBeenCalled();
    logoutStatus = 204; await userEvent.click(screen.getByRole('button', { name: 'Log out' }));
    await waitFor(() => expect(navigation.replace).toHaveBeenCalledWith('/en/login'));
  });
  it('shows Bangla logout copy', async () => {
    mount(<LogoutButton locale="bn" />, 'bn');
    expect(await screen.findByRole('button', { name: 'লগ আউট করুন' })).toBeVisible();
  });
  it('returns focus to the account control when Escape closes the menu', async () => {
    mount(<AccountMenu locale="en" />);
    const summary = await screen.findByLabelText('Your account');
    await userEvent.click(summary);
    await userEvent.tab();
    await userEvent.keyboard('{Escape}');
    expect(summary.closest('details')).not.toHaveAttribute('open');
    expect(summary).toHaveFocus();
  });
  it('places logout in the workspace sidebar and the account menu', async () => {
    render(<AppShell locale="en"><p>Fictional private workspace</p></AppShell>);
    const account = await screen.findByLabelText('Your account');
    expect(within(document.querySelector('aside.ui-rail') as HTMLElement).getByRole('button', { name: 'Log out' })).toBeVisible();
    await userEvent.click(account);
    expect(screen.getAllByRole('button', { name: 'Log out' })).toHaveLength(2);
  });
  it('clears mounted private UI state when a local sign-out event arrives', async () => {
    mount(<AccountMenu locale="en" />); await screen.findByLabelText('Your account');
    act(() => window.dispatchEvent(new CustomEvent(SESSION_EVENT, { detail: { type: 'signed_out' } })));
    expect(screen.queryByText('Fictional Buyer')).not.toBeInTheDocument();
  });
});

describe('Ebarki administration permissions', () => {
  it('uses the same guarded portal through the legacy entry', async () => {
    profile = guest; mount(<AdminDashboardClient locale="en" />);
    await waitFor(() => expect(navigation.replace).toHaveBeenCalledWith('/en/admin/login'));
    expect(requested.some(path => path.includes('/admin/'))).toBe(false);
  });
  it('shows actual overview values to an administrator', async () => {
    profile = { ...consumer, roles: ['admin'] }; mount(<AdminConsole locale="en" />);
    expect(await screen.findByText('37')).toBeVisible();
    expect(screen.getByText('11')).toBeVisible();
    expect(screen.queryByRole('button', { name: 'Source review' })).not.toBeInTheDocument();
  });
  it.each([['reviewer', '/api/v1/admin/source-candidates', 'Source review'], ['publisher', '/api/v1/knowledge/release', 'Knowledge release']])('opens the permitted first panel for %s without a forbidden stats call', async (role, path, label) => {
    profile = { ...consumer, roles: [role] }; mount(<AdminConsole locale="en" />);
    await waitFor(() => expect(requested).toContain(path));
    expect(screen.getByRole('button', { name: label })).toHaveAttribute('aria-current', 'page');
    expect(requested).not.toContain('/api/v1/admin/stats');
  });
  it('does not offer forbidden panels to an operator-only account', async () => {
    profile = { ...consumer, roles: ['operator'] }; mount(<AdminConsole locale="en" />);
    expect(await screen.findByText(/no permissions for the available administration panels/)).toBeVisible();
    expect(requested.some(path => path.includes('/admin/'))).toBe(false);
  });
  it('denies a consumer while providing a staff login route', async () => {
    mount(<AdminConsole locale="en" />);
    expect(await screen.findByRole('link', { name: 'Staff sign in' })).toHaveAttribute('href', '/en/admin/login');
    expect(requested.some(path => path.includes('/admin/'))).toBe(false);
  });
  it('redirects a guest to the dedicated admin login', async () => {
    profile = guest; mount(<AdminConsole locale="en" />);
    await waitFor(() => expect(navigation.replace).toHaveBeenCalledWith('/en/admin/login'));
    expect(requested.some(path => path.includes('/admin/'))).toBe(false);
  });
});
