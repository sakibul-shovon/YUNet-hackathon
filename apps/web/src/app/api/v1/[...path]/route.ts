import { NextRequest, NextResponse } from 'next/server';

const BACKEND_API_URL = process.env.BACKEND_API_URL || 'http://127.0.0.1:8000';

async function handleProxy(req: NextRequest, { params }: { params: Promise<{ path: string[] }> }) {
  const { path } = await params;
  const targetPath = path.join('/');
  // Forward to /v1/... or /api/v1/...
  const targetUrl = new URL(`/v1/${targetPath}${req.nextUrl.search}`, BACKEND_API_URL);

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

