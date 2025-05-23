import { z } from 'zod'
import { MoneySchema } from './moneySchema' // Assuming moneySchema.ts is in the same directory

// Use z.enum with the actual string values for TransactionType
export const TransactionTypeSchema = z.enum(['INCOME', 'EXPENSE'])

// Zod schema for validating Transaction objects from API
export const TransactionSchema = z.object({
  id: z.string().uuid(),
  amount: MoneySchema,
  transaction_type: TransactionTypeSchema,
  occurred_date: z.string().datetime({
    local: true
  }),
  category_id: z.string().uuid(),
  user_id: z.string().uuid(),
})
