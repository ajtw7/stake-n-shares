import React, { useEffect, useState } from "react";
import { fetchCompareHistory } from "../api/compare";

export default function ComparisonHistory() {
  const [items, setItems] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    fetchCompareHistory().then(data => {
      setItems(data);
    }).catch(e => setErr(e.message || String(e))).finally(() => setLoading(false));
  }, []);

  return (
    <div className="panel">
      <h3>Recent Comparisons</h3>
      {loading && <div className="muted">Loading…</div>}
      {err && <div className="alert error">{err}</div>}
      {!loading && items.length === 0 && <div className="muted">No history yet.</div>}
      <ul style={{ listStyle: "none", padding: 0 }}>
        {items.map(it => (
          <li key={it.id} style={{ padding: 12, borderBottom: "1px solid #eef2f6" }}>
            <div style={{ fontSize: 13, color: "#6b7280" }}>{new Date(it.created_at).toLocaleString()}</div>
            <div style={{ fontWeight: 700 }}>{it.payload.equity_symbol} — {it.payload.starting_capital}</div>
            <div style={{ fontSize: 13, color: "#475569" }}>Combined: {it.result.combined_final} — ROI: {it.result.roi_pct}%</div>
            <details style={{ marginTop: 6 }}>
              <summary style={{ cursor: "pointer" }}>Details</summary>
              <pre style={{ maxHeight: 200, overflow: "auto" }}>{JSON.stringify(it, null, 2)}</pre>
            </details>
          </li>
        ))}
      </ul>
    </div>
  );
}