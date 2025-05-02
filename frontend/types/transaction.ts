import { z } from 'zod'
import type { Money } from './money'

/**
 * Represents the type of a transaction, used across different layers.
 */
export type TransactionType = 'INCOME' | 'EXPENSE'

export const TransactionTypeSchema = z.enum(['INCOME', 'EXPENSE'])

// Transaction type corresponding to TransactionDTO and plan needs
export interface Transaction {
  id: string // UUID
  category_id: string // UUID of the associated category
  user_id: string // UUID of the user
  amount: Money
  type: TransactionType
  date: string // ISO datetime string (e.g., "2023-10-27T10:00:00Z")
  description?: string | null
}

// Zod schema for validating Transaction objects from API
export const TransactionSchema = z.object({
  id: z.string().uuid(),
  amount: MoneySchema,
  type: TransactionTypeSchema,
  date: z.string().datetime(), // Validate as ISO 8601 date string
  category_id: z.string().uuid(),
  user_id: z.string().uuid(),
})

// --- API Payloads for Transactions ---

// Payload definition for Amount used in transaction payloads
export interface AmountPayload {
  amount: number;
}

// Type for transaction type used in payloads (same as TransactionType)
export type TransactionTypePayload = TransactionType;

// Payload for creating a new transaction (POST /budgets/{id}/transactions)
export interface CreateTransactionPayload {
  category_id: string; // UUID
  amount: AmountPayload;
  transaction_type: TransactionTypePayload;
  occurred_date: string; // ISO Date string (e.g., YYYY-MM-DDTHH:mm:ssZ)
  description?: string;
}

// Payload for updating an existing transaction (PUT /budgets/{id}/transactions/{tid})
export interface UpdateTransactionPayload {
  category_id: string; // UUID
  amount: AmountPayload;
  transaction_type: TransactionTypePayload;
  occurred_date: string; // ISO Date string
  description?: string;
}
