
function OddsMeta({ meta }: { meta: any }) {
  if (!meta) return null;
  return (
    <div className="meta">
      <div><strong>Odds snapshot:</strong> {meta.snapshot_timestamp ?? "none (live/default)"}</div>
      <div><strong>Resolved odds:</strong> {meta.resolved_odds}</div>
      <div className={`badge ${meta.fallback_used ? "warn" : "ok"}`}>{meta.fallback_used ? "Fallback used" : "Odds resolved"}</div>
    </div>
  );
}

export default function ResultCard({ data }: { data: any }) {
  const eq = data.equity;
  const bet = data.bet;
  return (
    <div className="result-card">
      <div className="row">
        <div className="box">
          <h3>Equity</h3>
          <div className="big">{eq.symbol}</div>
          <div>Allocated: ${eq.allocated}</div>
          <div>PnL: ${eq.pnl}</div>
          <div>Final: ${eq.final}</div>
        </div>

        <div className="box">
          <h3>Bet</h3>
          <div className="big">{bet.event}</div>
          <div>Allocated: ${bet.allocated}</div>
          <div>PnL: ${bet.pnl}</div>
          <div>Final: ${bet.final}</div>
        </div>
      </div>

      <div className="summary">
        <div className="big">Combined: ${data.combined_final}</div>
        <div>ROI: {data.roi_pct}%</div>
      </div>

      <OddsMeta meta={data.odds_meta} />
    </div>
  );
}
