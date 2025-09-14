import { useState } from 'react';
import { postCompare } from '../api/compare';
import type { CompareRequest, CompareResponse } from '../types/compare';
import { ResultPanel } from './ResultPanel';

interface FormState {
  starting_capital: string;
  equity_symbol: string;
  equity_weight: string;
  league: string;
  event_id: string;
  stake: string;
  odds: string;
  outcome: 'win' | 'loss';
  start: string;
  end: string;
  odds_date: string;
}

const HEX32 = /^[0-9a-f]{32}$/;

export function CompareForm() {
  const [form, setForm] = useState<FormState>({
    starting_capital: '1000',
    equity_symbol: 'AAPL',
    equity_weight: '0.7',
    league: 'NFL',
    event_id: '0123456789abcdef0123456789abcdef',
    stake: '100',
    odds: '150',
    outcome: 'win',
    start: '2025-01-01',
    end: '2025-02-01',
    odds_date: ''
  });
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<CompareResponse | null>(null);

  function update<K extends keyof FormState>(k: K, v: FormState[K]) {
    setForm(f => ({ ...f, [k]: v }));
  }

  function validate(): string | null {
    if (!form.start || !form.end) return 'Start and End dates required';
    if (!form.starting_capital || Number(form.starting_capital) <= 0) return 'Starting capital must be > 0';
    const w = Number(form.equity_weight);
    if (isNaN(w) || w < 0 || w > 1) return 'Equity weight must be between 0 and 1';
    if (!HEX32.test(form.event_id)) return 'event_id must be 32-char lowercase hex';
    if (!form.league) return 'League required';
    if (!form.stake || Number(form.stake) <= 0) return 'Stake must be > 0';
    if (form.odds.trim() !== '') {
      const o = Number(form.odds);
      if (isNaN(o)) return 'Odds must be numeric (or blank)';
    }
    return null;
  }

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setResult(null);
    const v = validate();
    if (v) {
      setError(v);
      return;
    }
    setSubmitting(true);
    try {
      const payload: CompareRequest = {
        starting_capital: Number(form.starting_capital),
        equity_symbol: form.equity_symbol.trim(),
        equity_weight: Number(form.equity_weight),
        bet: {
          league: form.league.trim(),
          event_id: form.event_id.trim(),
          stake: Number(form.stake),
          odds: form.odds.trim() === '' ? null : Number(form.odds),
          outcome: form.outcome
        }
      };
      const params = {
        start: form.start,
        end: form.end,
        ...(form.odds_date ? { odds_date: form.odds_date } : {})
      };
      const resp = await postCompare(payload, params);
      setResult(resp);
    } catch (err: any) {
      setError(err.message || 'Request failed');
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div style={{marginTop:'1.5rem', textAlign:'left', maxWidth:640}}>
      <h2 style={{marginBottom:8}}>Compare Scenario</h2>
      <form onSubmit={submit} style={{display:'grid', gap:'0.75rem'}}>
        <div style={{display:'flex', gap:12}}>
          <label style={{flex:1}}>
            Starting Capital
            <input
              type="number"
              value={form.starting_capital}
              onChange={e=>update('starting_capital', e.target.value)}
            />
          </label>
          <label style={{flex:1}}>
            Equity Symbol
            <input
              value={form.equity_symbol}
              onChange={e=>update('equity_symbol', e.target.value)}
            />
          </label>
          <label style={{flex:1}}>
            Equity Weight
            <input
              type="number"
              step="0.01"
              value={form.equity_weight}
              onChange={e=>update('equity_weight', e.target.value)}
            />
          </label>
        </div>

        <div style={{display:'flex', gap:12}}>
          <label style={{flex:1}}>
            League
            <input
              value={form.league}
              onChange={e=>update('league', e.target.value)}
            />
          </label>
          <label style={{flex:2}}>
            Event ID
            <input
              value={form.event_id}
              onChange={e=>update('event_id', e.target.value)}
            />
          </label>
          <label style={{flex:1}}>
            Stake
            <input
              type="number"
              value={form.stake}
              onChange={e=>update('stake', e.target.value)}
            />
          </label>
        </div>

        <div style={{display:'flex', gap:12}}>
          <label style={{flex:1}}>
            Odds (blank = fetch)
            <input
              value={form.odds}
              onChange={e=>update('odds', e.target.value)}
              placeholder="e.g. 150"
            />
          </label>
          <label style={{flex:1}}>
            Outcome
            <select
              value={form.outcome}
              onChange={e=>update('outcome', e.target.value as 'win'|'loss')}
            >
              <option value="win">win</option>
              <option value="loss">loss</option>
            </select>
          </label>
          <label style={{flex:1}}>
            Odds Snapshot
            <input
              type="datetime-local"
              value={form.odds_date}
              onChange={e=>update('odds_date', e.target.value)}
            />
          </label>
        </div>

        <div style={{display:'flex', gap:12}}>
          <label style={{flex:1}}>
            Start Date
            <input
              type="date"
              value={form.start}
              onChange={e=>update('start', e.target.value)}
            />
          </label>
            <label style={{flex:1}}>
            End Date
            <input
              type="date"
              value={form.end}
              onChange={e=>update('end', e.target.value)}
            />
          </label>
        </div>

        <div style={{display:'flex', gap:12, alignItems:'center'}}>
          <button type="submit" disabled={submitting}>
            {submitting ? 'Running...' : 'Run Comparison'}
          </button>
          {submitting && <span style={{fontSize:12, opacity:0.7}}>Processing...</span>}
        </div>
      </form>

      {error && (
        <div style={{marginTop:12}}>
          <pre style={{color:'red', whiteSpace:'pre-wrap'}}>{error}</pre>
        </div>
      )}

      {result && (
        <ResultPanel
          data={result}
          onReset={() => { setResult(null); setError(null); }}
        />
      )}
    </div>
  );
}