import { z } from 'zod'
import { MoneySchema, type Money } from './money'

// Category Statistics type corresponding to CategoryStatisticsRecordDTO
export interface CategoryStatistics {
  // id: string // Not needed per plan, but present in DTO
  category_id: string // UUID
  current_balance: Money
  daily_available_amount: Money
  daily_average: Money
  used_limit: Money
}

// Zod schema for validating CategoryStatistics objects
export const CategoryStatisticsSchema = z.object({
  id: z.string().uuid(), // Keep for validation
  category_id: z.string().uuid(),
  current_balance: MoneySchema,
  daily_available_amount: MoneySchema,
  daily_average: MoneySchema,
  used_limit: MoneySchema,
})

// Budget Statistics type corresponding to StatisticsRecordDTO
export interface BudgetStatistics {
  // id: string // Not needed per plan, but present in DTO
  // user_id: string // Not needed per plan, but present in DTO
  // budget_id: string // Not needed per plan, but present in DTO
  current_balance: Money
  daily_available_amount: Money
  daily_average: Money
  used_limit: Money
  // creation_date: string // Not needed per plan, but present in DTO
  categories_statistics: CategoryStatistics[]
}

// Zod schema for validating BudgetStatistics objects from API
export const BudgetStatisticsSchema = z.object({
  id: z.string().uuid(), // Keep for validation
  user_id: z.string().uuid(), // Keep for validation
  budget_id: z.string().uuid(), // Keep for validation
  current_balance: MoneySchema,
  daily_available_amount: MoneySchema,
  daily_average: MoneySchema,
  used_limit: MoneySchema,
  creation_date: z.string().datetime(), // Keep for validation
  categories_statistics: z.array(CategoryStatisticsSchema).default([]),
})
