import type { APIRoute } from "astro";

import { proxyToBackend } from "../../lib/server/backendProxy";


export const ALL = (async ({ params, request }) => proxyToBackend(request, "api", params.path)) satisfies APIRoute;
