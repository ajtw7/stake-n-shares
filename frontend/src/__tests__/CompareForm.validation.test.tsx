import { render, screen, fireEvent } from '@testing-library/react';
import { vi, describe, test, expect } from 'vitest';
import { CompareForm } from '../components/CompareForm';

vi.mock('../api/compare', () => ({
  postCompare: vi.fn()
}));

describe('CompareForm validation', () => {
  test('invalid event_id shows validation message', async () => {
    render(<CompareForm />);
    const eventInput = screen.getByLabelText(/Event ID/i);
    fireEvent.change(eventInput, { target: { value: 'bad' }});
    fireEvent.click(screen.getByRole('button', { name: /Run Comparison/i }));
    expect(await screen.findByText(/event_id must be 32-char lowercase hex/i)).toBeInTheDocument();
  });
});