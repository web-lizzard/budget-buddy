import type { Money } from './money'

// Category Statistics type corresponding to CategoryStatisticsRecordDTO
export interface CategoryStatistics {
  // id: string // Not needed per plan, but present in DTO
  category_id: string // UUID
  current_balance: Money
  daily_available_amount: Money
  daily_average: Money
  used_limit: Money
}


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
