import { NextRequest, NextResponse } from 'next/server';

const BACKEND_API_URL = process.env.BACKEND_API_URL || 'http://127.0.0.1:8000';
const DEMO_CASE_UUID = '1887c4ed-99d6-44f2-9fb4-0c15e9d3287e';

async function handleProxy(req: NextRequest, { params }: { params: Promise<{ path: string[] }> }) {
  const { path } = await params;

  // Map known synthetic demo slug 'case_demo_phone' to its seeded UUID fixture
  const mappedPath = path.map((segment) => (segment === 'case_demo_phone' ? DEMO_CASE_UUID : segment));
  const targetPath = mappedPath.join('/');

  // Forward to /v1/...
  const targetUrl = new URL(`/v1/${targetPath}${req.nextUrl.search}`, BACKEND_API_URL);

  const headers = new Headers(req.headers);
  headers.set('host', new URL(BACKEND_API_URL).host);

  const correlationId = req.headers.get('x-correlation-id') || crypto.randomUUID();
  headers.set('x-correlation-id', correlationId);

  // Auto-bootstrap guest session if client has neither Authorization header nor session cookie
  let guestCookieToSet: string | null = null;
  const hasAuth = headers.get('authorization');
  const hasCookie = headers.get('cookie')?.includes('claimcraft_session');

  if (!hasAuth && !hasCookie) {
    try {
      const guestRes = await fetch(`${BACKEND_API_URL}/auth/guest`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      });
      if (guestRes.ok) {
        const guestData = await guestRes.json();
        if (guestData.access_token) {
          headers.set('authorization', `Bearer ${guestData.access_token}`);
        }
        const setCookie = guestRes.headers.get('set-cookie');
        if (setCookie) {
          guestCookieToSet = setCookie;
        }
      }
    } catch {
      // Proceed without guest bootstrap
    }
  }

  try {
    const fetchOptions: RequestInit = {
      method: req.method,
      headers,
      cache: 'no-store',
    };

    if (req.method !== 'GET' && req.method !== 'HEAD') {
      fetchOptions.body = await req.arrayBuffer();
    }

    const backendRes = await fetch(targetUrl.toString(), fetchOptions);
    const body = await backendRes.arrayBuffer();

    const responseHeaders = new Headers(backendRes.headers);
    responseHeaders.set('x-correlation-id', correlationId);
    if (guestCookieToSet) {
      responseHeaders.append('set-cookie', guestCookieToSet);
    }

    return new NextResponse(body, {
      status: backendRes.status,
      statusText: backendRes.statusText,
      headers: responseHeaders,
    });
  } catch (err: any) {
    return NextResponse.json(
      {
        error: {
          code: 'BACKEND_UNAVAILABLE',
          message: 'Backend resolution service is temporarily unreachable.',
          correlation_id: correlationId,
        },
      },
      { status: 503 }
    );
  }
}

export const GET = handleProxy;
export const POST = handleProxy;
export const PUT = handleProxy;
export const PATCH = handleProxy;
export const DELETE = handleProxy;
