import { useState } from 'react';
import { postCompare } from '../api/compare';
import type { CompareResponse } from '../types/compare';

export function CompareTester() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<CompareResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function run() {
    setError(null);
    setResult(null);
    setLoading(true);
    try {
      const eventId = '0123456789abcdef0123456789abcdef';
      const r = await postCompare(
        {
          starting_capital: 1000,
            equity_symbol: 'AAPL',
            equity_weight: 0.7,
            bet: {
              league: 'NFL',
              event_id: eventId,
              stake: 100,
              odds: 150,
              outcome: 'win'
            }
        },
        { start: '2025-01-01', end: '2025-02-01' }
      );
      setResult(r);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{marginTop: '1rem'}}>
      <button onClick={run} disabled={loading}>
        {loading ? 'Running...' : 'Test Compare'}
      </button>
      {error && (
        <pre style={{color:'red', whiteSpace:'pre-wrap'}}>{error}</pre>
      )}
      {result && (
        <pre
          style={{
            textAlign: 'left',
            background: '#111',
            color: '#0f0',
            padding: 12,
            fontSize: 12,
            overflowX: 'auto'
          }}
        >
{JSON.stringify(result, null, 2)}
        </pre>
      )}
    </div>
  );
}