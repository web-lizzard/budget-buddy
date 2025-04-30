import { z } from 'zod'
import { CategorySchema } from './categorySchema' // Assuming categorySchema.ts is in the same directory
import { MoneySchema } from './moneySchema' // Assuming moneySchema.ts is in the same directory

// Zod schema for validating Budget objects from API
export const BudgetSchema = z.object({
  id: z.string().uuid(),
  user_id: z.string().uuid(),
  name: z.string().min(1),
  total_limit: MoneySchema,
  start_date: z.string().datetime(),
  end_date: z.string().datetime(),
  currency: z.string().length(3),
  // strategy: BudgetStrategySchema, // Define if needed
  deactivation_date: z.string().datetime().nullable().optional(),
  categories: z.array(CategorySchema).default([]),
})
