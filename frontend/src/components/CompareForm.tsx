import React, { useState } from "react";
import { postCompare } from '../api/compare';
import type { CompareRequest, CompareResponse } from '../types/compare';
import { ResultPanel } from './ResultPanel';
import { compareFormSchema, type CompareFormValues } from '../validation/compare';
import { tokens } from '../styles/tokens';

type FormState = Record<keyof CompareFormValues, string>;

const initial: FormState = {
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
};

type Props = {
  onSubmit: (payload: any, params: { start: string; end: string; odds_date?: string }) => Promise<void>;
  submitting?: boolean;
};

export function CompareForm({ onSubmit, submitting }: Props) {
  const [form, setForm] = useState<FormState>(initial);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<CompareResponse | null>(null);
  const [fieldErrors, setFieldErrors] = useState<Record<string,string>>({});

  function update<K extends keyof FormState>(k: K, v: FormState[K]) {
    setForm(f => ({ ...f, [k]: v }));
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setResult(null);
    setFieldErrors({});

    // Build raw object (strings) mapped to schema expectation
    const raw = { ...form };
    const parsed = compareFormSchema.safeParse(raw);

    if (!parsed.success) {
      const fe: Record<string,string> = {};
      parsed.error.issues.forEach(issue => {
        const k = issue.path[0];
        if (k && !fe[k as string]) fe[k as string] = issue.message;
      });
      setFieldErrors(fe);
      setError('Fix validation errors.');
      return;
    }

    try {
      const v = parsed.data;
      const payload: CompareRequest = {
        starting_capital: v.starting_capital,
        equity_symbol: v.equity_symbol,
        equity_weight: v.equity_weight,
        bet: {
          league: v.league,
          event_id: v.event_id,
          stake: v.stake,
          odds: v.odds,
          outcome: v.outcome
        }
      };
      const params = {
        start: v.start,
        end: v.end,
        ...(v.odds_date ? { odds_date: v.odds_date } : {})
      };
      await onSubmit(payload, params);
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Request failed';
      setError(msg);
    }
  }

  function FE(key: keyof FormState) {
    const msg = fieldErrors[key];
    if (!msg) return null;
    return <div style={{color:tokens.color.danger, fontSize:11, marginTop:2}}>{msg}</div>;
  }

  return (
    <div style={{marginTop:'1.5rem', textAlign:'left', maxWidth:640, backgroundColor:tokens.color.bgPanel}}>
      <h2 style={{marginBottom:8}}>Compare Scenario</h2>
      <form onSubmit={handleSubmit} style={{display:'grid', gap:'0.75rem'}}>
        <div style={{display:'flex', gap:12}}>
          <label style={{flex:1}}>
            Starting Capital
            <input
              type="number"
              value={form.starting_capital}
              onChange={e=>update('starting_capital', e.target.value)}
            />
            {FE('starting_capital')}
          </label>
          <label style={{flex:1}}>
            Equity Symbol
            <input
              value={form.equity_symbol}
              onChange={e=>update('equity_symbol', e.target.value)}
            />
            {FE('equity_symbol')}
          </label>
          <label style={{flex:1}}>
            Equity Weight
            <input
              type="number"
              step="0.01"
              value={form.equity_weight}
              onChange={e=>update('equity_weight', e.target.value)}
            />
            {FE('equity_weight')}
          </label>
        </div>

        <div style={{display:'flex', gap:12}}>
          <label style={{flex:1}}>
            League
            <input
              value={form.league}
              onChange={e=>update('league', e.target.value)}
            />
            {FE('league')}
          </label>
          <label style={{flex:2}}>
            Event ID
            <input
              value={form.event_id}
              onChange={e=>update('event_id', e.target.value)}
            />
            {FE('event_id')}
          </label>
          <label style={{flex:1}}>
            Stake
            <input
              type="number"
              value={form.stake}
              onChange={e=>update('stake', e.target.value)}
            />
            {FE('stake')}
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
            {FE('odds')}
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
            {FE('start')}
          </label>
            <label style={{flex:1}}>
            End Date
            <input
              type="date"
              value={form.end}
              onChange={e=>update('end', e.target.value)}
            />
            {FE('end')}
          </label>
        </div>

        <div style={{display:'flex', gap:12, alignItems:'center'}}>
          <button type="submit" className="btn primary" disabled={submitting}>
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