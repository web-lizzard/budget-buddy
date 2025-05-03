import type { Money } from './money'

/**
 * Represents the type of a transaction, used across different layers.
 */
export type TransactionType = 'INCOME' | 'EXPENSE'

/**
 * Frontend representation of a transaction with consistent camelCase naming
 */
export interface Transaction {
  id: string
  categoryId: string
  userId: string
  amount: Money
  type: TransactionType
  date: string
  description?: string | null
}
