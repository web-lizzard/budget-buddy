import { z } from 'zod'
import { MoneySchema, type Money } from './money'

// Transaction type enum based on plan
export type TransactionType = 'Expense' | 'Income'

export const TransactionTypeSchema = z.enum(['Expense', 'Income'])

// Transaction type corresponding to TransactionDTO and plan needs
export interface Transaction {
  id: string // UUID
  amount: Money
  type: TransactionType
  date: string // Keep as string, parse to Date in ViewModel
  category_id: string // UUID
  budget_id: string // UUID
  // Add other fields from DTO if needed (e.g., description, payee)
}

// Zod schema for validating Transaction objects from API
export const TransactionSchema = z.object({
  id: z.string().uuid(),
  amount: MoneySchema,
  type: TransactionTypeSchema,
  date: z.string().datetime(), // Validate as ISO 8601 date string
  category_id: z.string().uuid(),
  budget_id: z.string().uuid(),
})
