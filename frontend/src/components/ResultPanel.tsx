import type { CompareResponse } from '../types/compare';
import { fmtCurrency, fmtPercent, fmtNumber } from '../utils/format';
import { tokens } from '../styles/tokens';

interface Props {
  data: CompareResponse;
  onReset?: () => void;
}

export function ResultPanel({ data, onReset }: Props) {
  const { equity, bet, combined_final, roi_pct, odds_meta } = data;
  const snapshotLabel = odds_meta.snapshot_timestamp
    ? `Snapshot: ${odds_meta.snapshot_timestamp}`
    : 'Live / explicit odds';

  return (
    <div style={{
      marginTop:16,
      padding:16,
      border: `1px solid ${tokens.color.border}`,
      borderRadius:8,
      background: tokens.color.bgPanel
    }}>
      <div style={{display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:8}}>
        <h3 style={{margin:0, fontSize:18}}>Result</h3>
        {onReset && (
          <button onClick={onReset} style={{fontSize:12}}>Clear</button>
        )}
      </div>

      <div style={{display:'grid', gap:6}}>
        <div>
          <strong>Total Final:</strong> {fmtCurrency(combined_final)} &nbsp;
          <span style={{color: roi_pct >= 0 ? '#4caf50' : '#e53935'}}>
            ROI {fmtPercent(roi_pct)}
          </span>
        </div>

        <div style={{display:'flex', gap:24, flexWrap:'wrap'}}>
          <div>
            <strong>Equity {equity.symbol}</strong><br/>
            Alloc: {fmtCurrency(equity.allocated)} &nbsp;
            PnL: <span style={{color: equity.pnl >= 0 ? '#4caf50' : '#e53935'}}>
              {fmtCurrency(equity.pnl)}
            </span><br/>
            Final: {fmtCurrency(equity.final)}
          </div>
          <div>
            <strong>Bet</strong><br/>
            Alloc: {fmtCurrency(bet.allocated)} &nbsp;
            PnL: <span style={{color: bet.pnl >= 0 ? '#4caf50' : '#e53935'}}>
              {fmtCurrency(bet.pnl)}
            </span><br/>
            Final: {fmtCurrency(bet.final)}
          </div>
        </div>

        <div style={{marginTop:4}}>
          <strong>Odds Used:</strong> {fmtNumber(odds_meta.resolved_odds)}{' '}
          <span style={{fontSize:12, opacity:0.8}}>({snapshotLabel})</span>{' '}
          {odds_meta.fallback_used && (
            <span
              data-testid="fallback-badge"
              style={{
                background:'#ff980033',
                color:'#ffb74d',
                padding:'2px 6px',
                borderRadius:4,
                fontSize:11,
                marginLeft:6
              }}
            >
              Fallback
            </span>
          )}
        </div>
      </div>

      <details style={{marginTop:12}}>
        <summary style={{cursor:'pointer', fontSize:13}}>Raw JSON</summary>
        <pre style={{fontSize:11, overflowX:'auto', background:'#000', color:'#6aff6a', padding:8, borderRadius:4}}>
{JSON.stringify(data, null, 2)}
        </pre>
      </details>
    </div>
  );
}