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

describe('CompareForm success', () => {
  test('renders result panel on success', async () => {
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

    render(<CompareForm />);
    fireEvent.click(screen.getByRole('button', { name: /Run Comparison/i }));
    await waitFor(() => expect(screen.getByText(/Result/i)).toBeInTheDocument());
    // Accept 17.50% (formatted to 2 decimals)
    expect(
      screen.getByText((content) => /ROI\s+17\.50%/i.test(content))
    ).toBeInTheDocument();
  });
});