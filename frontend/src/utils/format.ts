const currencyFmt = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' });

export function fmtCurrency(v: number): string {
  return currencyFmt.format(v);
}

export function fmtNumber(v: number, digits = 2): string {
  return v.toFixed(digits);
}

export function fmtPercent(v: number, digits = 2): string {
  return `${v.toFixed(digits)}%`;
}