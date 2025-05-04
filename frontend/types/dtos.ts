import type { Money } from './money'

/**
 * DTO types from API using snake_case naming convention
 */

// DTO types related to Budget
export interface BudgetDTO {
  id: string
  user_id: string
  name: string
  total_limit: Money
  currency: string
  start_date: string
  end_date: string
  strategy: BudgetStrategyDTO
  deactivation_date: string | null
  categories: CategoryDTO[]
}

export interface BudgetStrategyDTO {
  type: 'monthly' | 'yearly' | string
  recurring: boolean
}

export interface PaginatedItems<T> {
  items: T[]
  total: number
  skip: number
  limit: number
}

// DTO types related to Transaction
export interface TransactionDTO {
  id: string
  category_id: string
  user_id: string
  amount: Money
  type: 'INCOME' | 'EXPENSE'
  date: string
  description?: string | null
}

// DTO types related to Category
export interface CategoryDTO {
  id: string
  name: string
  limit: Money
}

// DTO types related to API Payloads
export interface AmountPayload {
  amount: number
}

export interface CreateTransactionPayload {
  category_id: string
  amount: AmountPayload
  transaction_type: 'INCOME' | 'EXPENSE'
  occurred_date: Date
  description?: string
}

export interface UpdateTransactionPayload {
  category_id: string
  amount: AmountPayload
  transaction_type: 'INCOME' | 'EXPENSE'
  occurred_date: string
  description?: string
}

export interface MoneyPayload {
  amount: number
  currency: string
}

export interface StrategyPayload {
  budget_strategy_type: 'monthly' | 'yearly'
  parameters: Record<string, unknown>
}

export interface CreateCategoryRequestPayload {
  name: string
  limit: MoneyPayload
}

export interface CreateBudgetRequestPayload {
  name: string
  total_limit: MoneyPayload
  start_date: Date
  categories: CreateCategoryRequestPayload[]
  strategy: StrategyPayload
}

// DTO types related to Statistics
export interface CategoryStatisticsDTO {
  category_id: string
  current_balance: Money
  daily_available_amount: Money
  daily_average: Money
  used_limit: Money
}

export interface BudgetStatisticsDTO {
  current_balance: Money
  daily_available_amount: Money
  daily_average: Money
  used_limit: Money
  categories_statistics: CategoryStatisticsDTO[]
}

export interface DomainError {
    status: string; // Domain error type
    message: string; // User-friendly error message
  }
