const DEFAULT_BACKEND_BASE_URL = "http://api:8787";
const HOP_BY_HOP_HEADERS = new Set([
  "connection",
  "content-length",
  "host",
  "keep-alive",
  "proxy-authenticate",
  "proxy-authorization",
  "te",
  "trailer",
  "transfer-encoding",
  "upgrade",
]);

export async function proxyToBackend(request: Request, prefix: string, path: string | undefined): Promise<Response> {
  const origin = process.env.INTERNAL_API_BASE_URL ?? DEFAULT_BACKEND_BASE_URL;
  const requestUrl = new URL(request.url);
  const targetPath = path ? `${prefix}/${path}` : prefix;
  const targetUrl = new URL(targetPath, ensureTrailingSlash(origin));
  targetUrl.search = requestUrl.search;

  const upstream = await fetch(targetUrl, {
    method: request.method,
    headers: filterHeaders(request.headers),
    body: allowsBody(request.method) ? await request.arrayBuffer() : undefined,
  });

  return new Response(upstream.body, {
    status: upstream.status,
    statusText: upstream.statusText,
    headers: filterHeaders(upstream.headers),
  });
}

function filterHeaders(headers: Headers): Headers {
  const nextHeaders = new Headers(headers);
  for (const header of HOP_BY_HOP_HEADERS) {
    nextHeaders.delete(header);
  }
  return nextHeaders;
}

function ensureTrailingSlash(value: string): string {
  return value.endsWith("/") ? value : `${value}/`;
}

function allowsBody(method: string): boolean {
  return !["GET", "HEAD"].includes(method.toUpperCase());
}
