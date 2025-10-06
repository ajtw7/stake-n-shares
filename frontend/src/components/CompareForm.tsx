import React, { useState } from "react";
import Tooltip from "./Tooltip";
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

  const inputStyle: React.CSSProperties = {
    width: '100%',
    boxSizing: 'border-box',
    padding: '8px 10px',
    border: '1px solid #d1d7e0',
    borderRadius: 6,
    fontSize: 14,
    background: '#ffffff',
    outline: 'none'
  };

  const labelStyle: React.CSSProperties = {
    display: 'block',
    flex: 1
  };

  return (
    <div
      style={{
        marginTop: '1.5rem',
        textAlign: 'left',
        width: '100%',            // ensure full width so parent can stack
        boxSizing: 'border-box',
        backgroundColor: '#fbfdff',   // lighter panel instead of black
        padding: 16,                  // visual padding
        borderRadius: 8,
        border: '1px solid #e6ecf2'
      }}
    >
      <h2 style={{ marginBottom: 8 }}>Compare Scenario</h2>
      <form onSubmit={handleSubmit} style={{ display: 'grid', gap: '0.75rem', width: '100%' }}>
        <div style={{ display: 'flex', gap: 12 }}>
          <label style={labelStyle}>
            <Tooltip text="Total starting capital you will allocate across equity + bets. Must be > 0.">
              <span>Starting Capital</span>
            </Tooltip>
            <input
              type="number"
              value={form.starting_capital}
              onChange={e => update('starting_capital', e.target.value)}
              style={inputStyle}
            />
            {FE('starting_capital')}
          </label>

          <label style={labelStyle}>
            <Tooltip text="Ticker symbol for the equity (e.g. AAPL). Will be converted to uppercase.">
              <span>Equity Symbol</span>
            </Tooltip>
            <input
              value={form.equity_symbol}
              onChange={e => update('equity_symbol', e.target.value)}
              style={inputStyle}
            />
            {FE('equity_symbol')}
          </label>

          <label style={labelStyle}>
            <Tooltip text="Fraction of capital allocated to the equity. Value between 0 and 1 (e.g. 0.5 = 50%).">
              <span>Equity Weight</span>
            </Tooltip>
            <input
              type="number"
              step="0.01"
              value={form.equity_weight}
              onChange={e => update('equity_weight', e.target.value)}
              style={inputStyle}
            />
            {FE('equity_weight')}
          </label>
        </div>

        <div style={{ display: 'flex', gap: 12 }}>
          <label style={labelStyle}>
            <Tooltip text="League to use when resolving odds (currently only NFL supported).">
              <span>League</span>
            </Tooltip>
            <input
              value={form.league}
              onChange={e => update('league', e.target.value)}
              style={inputStyle}
            />
            {FE('league')}
          </label>

          <label style={{ flex: 2, display: 'block' }}>
            <Tooltip text="Event identifier (32-character hex). Identifies the game/event to fetch odds for.">
              <span>Event ID</span>
            </Tooltip>
            <input
              value={form.event_id}
              onChange={e => update('event_id', e.target.value)}
              style={inputStyle}
            />
            {FE('event_id')}
          </label>

          <label style={labelStyle}>
            <Tooltip text="Stake amount for the bet (must be > 0).">
              <span>Stake</span>
            </Tooltip>
            <input
              type="number"
              value={form.stake}
              onChange={e => update('stake', e.target.value)}
              style={inputStyle}
            />
            {FE('stake')}
          </label>
        </div>

        <div style={{ display: 'flex', gap: 12 }}>
          <label style={labelStyle}>
            <Tooltip text="Optional fixed odds to use for the bet. If omitted, historical or live odds will be fetched. Must be > 1.">
              <span>Odds (blank = fetch)</span>
            </Tooltip>
            <input
              value={form.odds}
              onChange={e => update('odds', e.target.value)}
              placeholder="e.g. 150"
              style={inputStyle}
            />
            {FE('odds')}
          </label>

          <label style={labelStyle}>
            <Tooltip text="Outcome to simulate: 'win' or 'loss'.">
              <span>Outcome</span>
            </Tooltip>
            <select
              value={form.outcome}
              onChange={e => update('outcome', e.target.value as 'win'|'loss')}
              style={{ ...inputStyle, paddingTop: 8, paddingBottom: 8 }}
            >
              <option value="win">win</option>
              <option value="loss">loss</option>
            </select>
          </label>

          <label style={labelStyle}>
            <Tooltip text="Optional snapshot timestamp for historical odds. Provide YYYY-MM-DD or full ISO timestamp.">
              <span>Odds Snapshot</span>
            </Tooltip>
            <input
              type="datetime-local"
              value={form.odds_date}
              onChange={e => update('odds_date', e.target.value)}
              style={inputStyle}
            />
          </label>
        </div>

        <div style={{ display: 'flex', gap: 12 }}>
          <label style={labelStyle}>
            <Tooltip text="Start date for the equity price range (YYYY-MM-DD).">
              <span>Start Date</span>
            </Tooltip>
            <input
              type="date"
              value={form.start}
              onChange={e => update('start', e.target.value)}
              style={inputStyle}
            />
            {FE('start')}
          </label>

          <label style={labelStyle}>
            <Tooltip text="End date for the equity price range (YYYY-MM-DD).">
              <span>End Date</span>
            </Tooltip>
            <input
              type="date"
              value={form.end}
              onChange={e => update('end', e.target.value)}
              style={inputStyle}
            />
            {FE('end')}
          </label>
        </div>

        <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
          <button type="submit" className="btn primary" disabled={submitting}>
            {submitting ? 'Running...' : 'Run Comparison'}
          </button>
          {submitting && <span style={{ fontSize: 12, opacity: 0.7 }}>Processing...</span>}
        </div>
      </form>

      {error && (
        <div style={{ marginTop: 12 }}>
          <pre style={{ color: 'red', whiteSpace: 'pre-wrap' }}>{error}</pre>
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