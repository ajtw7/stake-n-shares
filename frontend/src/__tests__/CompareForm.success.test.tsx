import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi, describe, test, expect, afterEach } from 'vitest';
import App from '../App';
import type { CompareResponse } from '../types/compare';
import { postCompare, fetchCompareHistory } from '../api/compare';

vi.mock('../api/compare', () => ({
  postCompare: vi.fn(),
  fetchCompareHistory: vi.fn().mockResolvedValue([])
}));

afterEach(() => {
  vi.clearAllMocks();
});

describe('CompareForm success', () => {
  test('renders result card on success', async () => {
    const mockResp: CompareResponse = {
      starting_capital: 1000,
      equity: { symbol: 'AAPL', allocated: 700, pnl: 25, final: 725 },
      bet: { event: '0123456789abcdef0123456789abcdef', allocated: 300, pnl: 150, final: 450 },
      combined_final: 1175,
      roi_pct: 17.5,
      odds_meta: {
        snapshot_timestamp: null,
        resolved_odds: 150,
        fallback_used: false
      }
    };

    (postCompare as unknown as ReturnType<typeof vi.fn>).mockResolvedValueOnce(mockResp);

    render(<App />);
    fireEvent.click(screen.getByRole('button', { name: /Run Comparison/i }));
    await waitFor(() => expect(postCompare).toHaveBeenCalledTimes(1));
    await waitFor(() => expect(screen.getByText(/ROI: 17\.5%/)).toBeInTheDocument());
  });
});