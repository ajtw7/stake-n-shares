export interface CompareRequestBet {
  league: string;
  event_id: string;            // 32-char hex
  stake: number;
  odds: number | null;         // null => let backend resolve/fallback
  outcome: 'win' | 'loss';
}

export interface CompareRequest {
  starting_capital: number;
  equity_symbol: string;
  equity_weight: number;       // 0..1
  bet: CompareRequestBet;
}

export interface CompareResponse {
  starting_capital: number;
  equity: {
    symbol: string;
    allocated: number;
    pnl: number;
    final: number;
  };
  bet: {
    event: string;
    allocated: number;
    pnl: number;
    final: number;
  };
  combined_final: number;
  roi_pct: number;
  odds_meta: {
    snapshot_timestamp: string | null;
    resolved_odds: number;
    fallback_used: boolean;
    // fallback_reason?: string; (future)
  };
}