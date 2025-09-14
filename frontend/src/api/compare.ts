import type { CompareRequest, CompareResponse } from '../types/compare';

const BASE = import.meta.env.VITE_API_BASE;

function ensureBase() {
  if (!BASE) {
    throw new Error('VITE_API_BASE not set');
  }
}

export async function postCompare(
  payload: CompareRequest,
  params: { start: string; end: string; odds_date?: string }
): Promise<CompareResponse> {
  ensureBase();
  const qs = new URLSearchParams({
    start: params.start,
    end: params.end,
    ...(params.odds_date ? { odds_date: params.odds_date } : {})
  });
  const res = await fetch(`${BASE}/api/v1/compare?${qs}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  let body: any;
  try {
    body = await res.json();
  } catch {
    body = await res.text();
  }
  if (!res.ok) {
    throw new Error(
      typeof body === 'string'
        ? body
        : body?.detail
          ? JSON.stringify(body.detail)
          : 'Compare request failed'
    );
  }
  return body as CompareResponse;
}