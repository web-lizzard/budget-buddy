// types/budget.ts

// Equivalent of MoneyDTO
import type { Category } from './category'
import type { Money } from './money'

export interface BudgetStrategy {
  type: 'monthly' | 'yearly' | string; // Allow string for flexibility
  recurring: boolean;
}

/**
 * Frontend representation of a budget with consistent camelCase naming
 */
export interface Budget {
  id: string;
  userId: string;
  name: string;
  totalLimit: Money;
  startDate: string;
  endDate: string;
  currency: string;
  categories: Category[];
  isActive: boolean;
  strategy?: BudgetStrategy;
  deactivationDate?: string | null;
}

// Equivalent of PaginatedItemDTO<BudgetDTO> from API
export interface PaginatedBudgetsDTO {
  items: Budget[];
  total: number;
  skip: number;
  limit: number;
}

// ViewModel for the Budget List Item in the UI
export interface BudgetListItemViewModel {
  id: string;
  name: string;
  status: 'active' | 'expired' | 'inactive'; // 'inactive' if deactivated
  statusLabel: string; // e.g., "Active", "Expired", "Inactive"
  dateRange: string; // e.g., "2024-01-01 - 2024-01-31"
  limitFormatted: string; // e.g., "1,000.00 PLN"
  currency: string; // e.g., "PLN"
  startDate: string; // Original start date (ISO string) for sorting
  endDate: string;   // Add end date (ISO string) for formatting
  // usageProgress?: number; // Optional, if API provides data
}

// State structure for the Pinia Store
export interface BudgetStoreState {
  budgets: BudgetListItemViewModel[];
  totalBudgets: number;
  currentPage: number;
  itemsPerPage: number;
  currentFilter: BudgetFilterValue; // Use the type alias
  currentSort: BudgetSortOption; // Use the type alias
  isLoading: boolean;
  error: string | null;
}

// Type alias for filter values for better readability
export type BudgetFilterValue = 'all' | 'active' | 'expired';

// Type alias for sorting options for better readability
export interface BudgetSortOption {
  sortBy: string; // Corresponds to API field name, e.g., 'start_date', 'name'
  sortOrder: 'asc' | 'desc';
}
