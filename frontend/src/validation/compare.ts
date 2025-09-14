import { z } from 'zod';

export const hex32 = /^[0-9a-f]{32}$/;

const oddsSchema = z.union([
  z.literal('').transform(() => null),
  z.string()
    .trim()
    .regex(/^-?\d+(\.\d+)?$/, 'Odds must be numeric')
    .transform(s => Number(s))
]);

export const compareFormSchema = z.object({
  starting_capital: z.coerce.number().positive('Starting capital must be > 0'),
  equity_symbol: z.string().trim().min(1, 'Equity symbol required'),
  equity_weight: z.coerce.number().min(0, 'Equity weight >= 0').max(1, 'Equity weight <= 1'),
  league: z.string().trim().min(1, 'League required'),
  event_id: z.string().regex(hex32, 'event_id must be 32-char lowercase hex'),
  stake: z.coerce.number().positive('Stake must be > 0'),
  odds: oddsSchema,          // number | null
  outcome: z.enum(['win', 'loss']),
  start: z.string().min(1, 'Start date required'),
  end: z.string().min(1, 'End date required'),
  odds_date: z.string().optional().default('')
}).superRefine((data, ctx) => {
  if (data.start && data.end && data.start > data.end) {
    ctx.addIssue({
      code: z.ZodIssueCode.custom,
      path: ['end'],
      message: 'End date must be >= start date'
    });
  }
});

export type CompareFormValues = z.infer<typeof compareFormSchema>;