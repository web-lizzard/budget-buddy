// stores/budgetStore.ts
import { defineStore } from 'pinia';
import type {
  BudgetStoreState,
  BudgetFilterValue,
  BudgetSortOption,
  PaginatedBudgetsDTO_API,
  BudgetDTO_API,
  BudgetListItemViewModel
} from '@/types/budget';

// TODO: Implement actual mapping function
function mapBudgetDTOToViewModel(dto: BudgetDTO_API): BudgetListItemViewModel {
  // Placeholder implementation - needs real logic based on requirements
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const startDate = new Date(dto.start_date);
  const endDate = new Date(dto.end_date);
  const deactivationDate = dto.deactivation_date ? new Date(dto.deactivation_date) : null;

  let status: 'active' | 'expired' | 'inactive' = 'active';
  let statusLabel: string = 'Active'; // Using English for labels in code

  if (deactivationDate && deactivationDate <= today) {
    status = 'inactive';
    statusLabel = 'Inactive';
  } else if (endDate < today) {
    status = 'expired';
    statusLabel = 'Expired';
  } else if (startDate > today) {
    // Assuming budgets starting in the future are also considered 'active' in a sense
    // but perhaps should have a different status like 'upcoming' or handled differently?
    // Sticking to plan's definition for now.
    status = 'active';
    statusLabel = 'Active';
  }

  // Placeholder formatting - use Intl.NumberFormat and Intl.DateTimeFormat in the component or a dedicated util
  // Keep raw values in the store/ViewModel where possible, format at the last step (in the template)
  const limitFormatted = `${dto.total_limit.amount.toLocaleString('en-US')} ${dto.total_limit.currency}`; // Example formatting
  const dateRange = `${startDate.toLocaleDateString('en-CA')} - ${endDate.toLocaleDateString('en-CA')}`; // ISO-like format example

  return {
    id: dto.id,
    name: dto.name,
    status: status,
    statusLabel: statusLabel, // This might be better handled by i18n later
    dateRange: dateRange, // Raw dates might be more useful
    limitFormatted: limitFormatted, // Raw amount might be more useful
    currency: dto.currency,
    startDate: dto.start_date, // Keep original for sorting
  };
}


export const useBudgetStore = defineStore('budgetStore', {
  state: (): BudgetStoreState => ({
    budgets: [],
    totalBudgets: 0,
    currentPage: 1,
    itemsPerPage: 10, // Default items per page
    currentFilter: 'all',
    currentSort: { sortBy: 'start_date', sortOrder: 'desc' }, // Default sort
    isLoading: false,
    error: null,
  }),
  actions: {
    async fetchBudgets() {
      this.isLoading = true;
      this.error = null;
      console.log(`Fetching budgets with params: page=${this.currentPage}, limit=${this.itemsPerPage}, filter=${this.currentFilter}, sort=${this.currentSort.sortBy}(${this.currentSort.sortOrder})`);
      try {
        const params: Record<string, string | number> = {
          page: this.currentPage,
          limit: this.itemsPerPage,
          // Map state filter to API parameter
          ...(this.currentFilter !== 'all' && { status: this.currentFilter }),
          // Map state sort to API parameter (e.g., 'start_date' or '-start_date')
          // Ensure the API actually supports this format
          sort: `${this.currentSort.sortOrder === 'desc' ? '-' : ''}${this.currentSort.sortBy}`,
        };

        // Using Nuxt 3's useFetch/ofetch implicitly available via $fetch
        // Replace '/api/budgets' with the actual endpoint from environment variable or config
        // Consider adding base URL from runtime config
        const response = await $fetch<PaginatedBudgetsDTO_API>('/api/v0/budgets', { // TODO: Replace with actual API endpoint
          method: 'GET'
          params: params,
          // Add headers like Authorization if needed
          // headers: { ... }
          // Add error handling interceptors if needed globally
        });

        // Apply the mapping function
        this.budgets = response.items.map(mapBudgetDTOToViewModel);
        this.totalBudgets = response.total;
        console.log(`Fetched ${response.items.length} budgets, total: ${response.total}`);

      } catch (err: any) {
        console.error("Failed to fetch budgets:", err);
        // Try to extract a meaningful error message
        const message = err.data?.message || err.statusMessage || err.message || 'Failed to load budgets. Please try again.';
        this.error = message;
        this.budgets = []; // Clear budgets on error
        this.totalBudgets = 0;
      } finally {
        this.isLoading = false;
      }
    },

    setFilter(filter: BudgetFilterValue) {
      if (this.currentFilter !== filter) {
        console.log(`Setting filter to: ${filter}`);
        this.currentFilter = filter;
        this.currentPage = 1; // Reset page when filter changes
        this.fetchBudgets(); // Refetch data
      }
    },

    setPage(page: number) {
      if (page > 0 && this.currentPage !== page) {
          // Optional: Check if page is valid given totalBudgets and itemsPerPage
          // const maxPage = Math.ceil(this.totalBudgets / this.itemsPerPage);
          // if (page > maxPage) page = maxPage;
          console.log(`Setting page to: ${page}`);
          this.currentPage = page;
          this.fetchBudgets(); // Refetch data
      }
    },

    setItemsPerPage(limit: number) {
        if (limit > 0 && this.itemsPerPage !== limit) {
            console.log(`Setting itemsPerPage to: ${limit}`);
            this.itemsPerPage = limit;
            this.currentPage = 1; // Reset page when limit changes
            this.fetchBudgets(); // Refetch data
        }
    },

    setSort(sortOption: BudgetSortOption) {
      if (this.currentSort.sortBy !== sortOption.sortBy || this.currentSort.sortOrder !== sortOption.sortOrder) {
        console.log(`Setting sort to: ${sortOption.sortBy} (${sortOption.sortOrder})`);
        this.currentSort = sortOption;
        // Reset page to 1 when sorting changes? Common practice.
        // this.currentPage = 1;
        this.fetchBudgets(); // Refetch data
      }
    },
  },
});
