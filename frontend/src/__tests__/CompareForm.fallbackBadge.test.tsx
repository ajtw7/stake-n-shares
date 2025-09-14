import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi, describe, test, expect, afterEach } from 'vitest';
import { CompareForm } from '../components/CompareForm';
import type { CompareResponse } from '../types/compare';
import { postCompare } from '../api/compare';

vi.mock('../api/compare', () => ({
  postCompare: vi.fn()
}));

afterEach(() => {
  vi.clearAllMocks();
});

describe('CompareForm fallback badge', () => {
  test('shows Fallback badge', async () => {
    const fallbackResp: CompareResponse = {
      starting_capital: 1000,
      equity: { symbol: 'AAPL', allocated: 700, pnl: -10, final: 690 },
      bet: { event: '0123456789abcdef0123456789abcdef', allocated: 300, pnl: 0, final: 300 },
      combined_final: 990,
      roi_pct: -1,
      odds_meta: {
        snapshot_timestamp: '2025-01-01T12:00:00Z',
        resolved_odds: 145,
        fallback_used: true
      }
    };

    (postCompare as unknown as ReturnType<typeof vi.fn>).mockResolvedValueOnce(fallbackResp);

    render(<CompareForm />);
    fireEvent.click(screen.getByRole('button', { name: /Run Comparison/i }));
    await waitFor(() => expect(screen.getByTestId('fallback-badge')).toBeInTheDocument());
    expect(screen.getByText(/145\.00/)).toBeInTheDocument();
  });
});