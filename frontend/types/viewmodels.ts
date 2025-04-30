import type { Money } from './money'
import type { TransactionType } from './transaction'

/**
 * ViewModel for displaying a category in the list.
 * Combines data from Category and CategoryStatistics.
 */
export interface CategoryListItemViewModel {
  id: string
  name: string
  limit: Money
  currentBalance?: Money // Optional, based on availability of stats
  usedLimit?: Money // Optional, based on availability of stats
  progressPercentage: number // Calculated value (0-100+)
}

/**
 * ViewModel for displaying a transaction in the recent transactions table.
 * Transforms raw Transaction data for presentation.
 */
export interface TransactionViewModel {
  id: string
  date: Date // Converted to Date object for easier formatting
  categoryName: string // Fetched or mapped based on category_id
  type: TransactionType
  amount: Money
}


/**
 * ViewModel structure required by the chart library (e.g., Chart.js Doughnut).
 */

export interface CharDataset {
  data: number[]
  backgroundColor: string[] // Colors for each category slice
}


export interface ChartDataViewModel {
  labels: string[]
  datasets: CharDataset[]
}
