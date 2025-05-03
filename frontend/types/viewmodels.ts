import type { Money } from './money'
import type { TransactionType } from './transaction'

/**
 * ViewModel for displaying a category in the list.
 * Combines data from Category and CategoryStatistics.
 */
export interface CategoryListItemViewModel {
  id: string
  name: string
  limit: Money | null
  currentBalance?: Money | null // Current balance from stats
  usedLimit?: Money | null // Used limit from stats
  progressPercentage: number // Calculated progress towards limit
}

/**
 * ViewModel for displaying a transaction in the recent transactions table.
 * Transforms raw Transaction data for presentation.
 */
export interface TransactionViewModel {
  id: string
  date: Date
  categoryName: string // Derived from categoryMap
  type: TransactionType
  amount: Money
}

/**
 * ViewModel structure required by the chart library (e.g., Chart.js Doughnut).
 */

export interface ChartDatasetViewModel {
  data: number[]
  backgroundColor?: string | string[] // Optional background colors
  label?: string // Optional dataset label
}

export interface ChartDataViewModel {
  labels: string[]
  datasets: ChartDatasetViewModel[]
}

// --- Budget Detail ViewModels ---

// Represents basic budget info for summary display
export interface BudgetSummaryViewModel {
  id: string
  name: string
  startDate: Date
  endDate: Date
  totalLimit: Money | null
  currency: string
  isActive: boolean
}

// --- Add/Edit Transaction Modal ViewModels ---

export interface CategoryViewModel {
  id: string;
  name: string;
}

export interface TransactionDataViewModel {
  id: string;
  categoryId: string;
  amount: number; // Note: In the form, we handle this as number | null initially
  currency: string; // For verification, form uses budgetCurrency
  type: 'INCOME' | 'EXPENSE';
  occurredDate: string; // ISO string from API
  description?: string;
}
