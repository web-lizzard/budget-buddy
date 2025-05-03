import { z } from 'zod'
import { MoneySchema } from './moneySchema' // Assuming moneySchema.ts is in the same directory

// Zod schema for validating CategoryStatistics objects
// Renaming to avoid conflict if CategoryStatisticsSchema is also defined here
export const CategoryStatisticsSchema = z.object({
  id: z.string().uuid(),
  category_id: z.string().uuid(),
  current_balance: MoneySchema,
  daily_available_amount: MoneySchema,
  daily_average: MoneySchema,
  used_limit: MoneySchema,
})

// Zod schema for validating BudgetStatistics objects from API
export const BudgetStatisticsSchema = z.object({
  id: z.string().uuid(),
  user_id: z.string().uuid(),
  budget_id: z.string().uuid(),
  current_balance: MoneySchema,
  daily_available_amount: MoneySchema,
  daily_average: MoneySchema,
  used_limit: MoneySchema,
  creation_date: z.string().datetime({
    local: true
  }),
  categories_statistics: z.array(CategoryStatisticsSchema).default([]),
})
