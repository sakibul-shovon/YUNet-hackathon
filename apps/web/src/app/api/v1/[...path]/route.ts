import { NextRequest, NextResponse } from 'next/server';

const BACKEND_API_URL = process.env.BACKEND_API_URL || 'http://127.0.0.1:8000';
const DEMO_CASE_UUID = '1887c4ed-99d6-44f2-9fb4-0c15e9d3287e';

async function handleProxy(req: NextRequest, { params }: { params: Promise<{ path: string[] }> }) {
  const { path } = await params;

  // Map known synthetic demo slug 'case_demo_phone' to its seeded UUID fixture
  const mappedPath = path.map((segment) => (segment === 'case_demo_phone' ? DEMO_CASE_UUID : segment));
  const targetPath = mappedPath.join('/');

  // If path begins with 'auth/', route directly to /auth/ (identity router root)
  const prefix = targetPath.startsWith('auth/') ? '' : '/v1/';
  const targetUrl = new URL(`${prefix}${targetPath}${req.nextUrl.search}`, BACKEND_API_URL);

  const headers = new Headers(req.headers);
  headers.set('host', new URL(BACKEND_API_URL).host);

  const correlationId = req.headers.get('x-correlation-id') || crypto.randomUUID();
  headers.set('x-correlation-id', correlationId);

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

    const res = new NextResponse(body, {
      status: backendRes.status,
      statusText: backendRes.statusText,
      headers: responseHeaders,
    });

    // Forward Set-Cookie headers properly in Next.js
    const setCookieHeaders = backendRes.headers.getSetCookie
      ? backendRes.headers.getSetCookie()
      : [backendRes.headers.get('set-cookie')].filter(Boolean);

    for (const cookieStr of setCookieHeaders) {
      if (cookieStr) {
        res.headers.append('set-cookie', cookieStr);
      }
    }

    return res;
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
