// types/budget.ts

// Equivalent of MoneyDTO
import type  { Category } from './category'
import type {  Money } from './money'

export interface BudgetStrategy {
  type: 'monthly' | 'yearly' | string; // Allow string for flexibility
  recurring: boolean;
}

// Equivalent of BudgetDTO from API
export interface BudgetDTO {
  id: string; // UUID
  user_id: string; // UUID
  total_limit: Money;
  currency: string;
  start_date: string; // ISO 8601 date string
  end_date: string; // ISO 8601 date string
  strategy: BudgetStrategy;
  name: string;
  deactivation_date: string | null; // ISO 8601 date string or null
  categories: unknown[]; // Categories are not needed in this view
}

// Equivalent of PaginatedItemDTO<BudgetDTO> from API
export interface PaginatedBudgetsDTO {
  items: BudgetDTO[];
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

// Budget type corresponding to BudgetDTO and implementation plan needs
export interface Budget {
  id: string // UUID
  // user_id: string // Included in DTO, but maybe not needed directly in frontend type?
  name: string
  total_limit: Money // Renamed from limit in plan to match DTO
  start_date: string // Keep as string for simplicity, parse if needed
  end_date: string // Keep as string for simplicity, parse if needed
  currency: string
  categories: Category[]
  is_active: boolean // Added based on plan (deactivation logic)
  // strategy: BudgetStrategyDTO // Not detailed in plan, omit for now
  // deactivation_date: string | null // Included in DTO, add if needed for UI
}
