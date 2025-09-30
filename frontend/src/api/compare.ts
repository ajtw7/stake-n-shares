import type { CompareRequest, CompareResponse } from '../types/compare';
import { API_BASE } from '../config';

const BASE = API_BASE;

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

export async function fetchCompareHistory(limit = 50, offset = 0) {
  ensureBase();
  const qs = new URLSearchParams({ limit: String(limit), offset: String(offset) });
  const res = await fetch(`${BASE}/api/v1/compare/history?${qs}`, { method: 'GET' });
  if (!res.ok) throw new Error(await res.text());
  return (await res.json()) as any[];
}