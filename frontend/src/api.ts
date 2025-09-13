export async function postCompare(body: any, query: { start: string; end: string; odds_date?: string }) {
  const base = import.meta.env.VITE_API_BASE;
  const qs = new URLSearchParams({ start: query.start, end: query.end, ...(query.odds_date ? { odds_date: query.odds_date } : {}) });
  const res = await fetch(`${base}/api/v1/compare?${qs}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}