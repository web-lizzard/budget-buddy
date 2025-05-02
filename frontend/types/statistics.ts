import type { Money } from './money'

/**
 * Frontend representation of category statistics with consistent camelCase naming
 */
export interface CategoryStatistics {
  categoryId: string
  currentBalance: Money
  dailyAvailableAmount: Money
  dailyAverage: Money
  usedLimit: Money
}

/**
 * Frontend representation of budget statistics with consistent camelCase naming
 */
export interface BudgetStatistics {
  currentBalance: Money
  dailyAvailableAmount: Money
  dailyAverage: Money
  usedLimit: Money
  categoriesStatistics: CategoryStatistics[]
}
