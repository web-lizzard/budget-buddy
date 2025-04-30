// stores/budgetStore.ts
import { ref } from 'vue'; // Removed unused computed import
import { defineStore } from 'pinia';
import type {
  BudgetFilterValue,
  BudgetSortOption,
  PaginatedBudgetsDTO, // Updated type name
  BudgetDTO,           // Updated type name
  BudgetListItemViewModel,
} from '@/types/budget';
import type { CreateBudgetRequestPayload } from '~/types/api'; // Import API payload type

// Keep the mapping function separate or move to utils
// Updated to use BudgetDTO
function mapBudgetDTOToViewModel(dto: BudgetDTO): BudgetListItemViewModel {
  const today = new Date();
  today.setHours(0, 0, 0, 0); // Normalize today to the start of the day for accurate comparison
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const startDate = new Date(dto.start_date); // Keep for potential future use or clarity, suppress unused var warning
  const endDate = new Date(dto.end_date);
  const deactivationDate = dto.deactivation_date ? new Date(dto.deactivation_date) : null;

  let status: 'active' | 'expired' | 'inactive';
  let statusLabel: string; // Label will be determined based on status

  // 1. Check for inactive status first (explicitly deactivated)
  if (deactivationDate && deactivationDate <= today) {
    status = 'inactive';
    statusLabel = 'Inactive';
  }
  // 2. Check for expired status (end date is in the past)
  else if (endDate < today) {
    status = 'expired';
    statusLabel = 'Expired';
  }
  // 3. Otherwise, consider it active (covers cases where start date is today or in the past, and end date is today or in the future)
  // Note: Budgets starting in the future are also marked active based on previous logic. Adjust if needed.
  else {
    status = 'active';
    statusLabel = 'Active';
  }

  // Prepare data for the view model
  // Formatting (dateRange, limitFormatted) is best done in the component using Intl
  // Pass raw data or minimally processed data where possible

  // Example: Pass raw dates for potential use in the component
  // const dateRange = `${dto.start_date.substring(0, 10)} - ${dto.end_date.substring(0, 10)}`;

  // Example: Pass raw amount and currency for formatting in component
  // const limitFormatted = `${dto.total_limit.amount} ${dto.total_limit.currency}`; // Let component handle formatting

  return {
    id: dto.id,
    name: dto.name,
    status: status,
    statusLabel: statusLabel, // Keep label for potential direct use or i18n key
    // Provide raw data that might be needed for display logic or formatting in the component
    dateRange: `${dto.start_date.split('T')[0]} - ${dto.end_date.split('T')[0]}`, // Basic range string, component can format better
    limitFormatted: `${dto.total_limit.amount} ${dto.total_limit.currency}`, // Basic amount string, component should format
    currency: dto.currency,
    startDate: dto.start_date, // Keep original ISO string for sorting
    endDate: dto.end_date,     // Add original ISO string for formatting
  };
}

export const useBudgetStore = defineStore('budgetStore', () => {
  const budgets = ref<BudgetListItemViewModel[]>([]);
  const totalBudgets = ref<number>(0);
  const currentPage = ref<number>(1);
  const itemsPerPage = ref<number>(10); // Default items per page
  const currentFilter = ref<BudgetFilterValue>('all');
  const currentSort = ref<BudgetSortOption>({ sortBy: 'name', sortOrder: 'asc' }); // Default sort
  const isLoading = ref<boolean>(false);
  const error = ref<string | null>(null);

  async function fetchBudgets() {
    isLoading.value = true;
    error.value = null;
    console.log('Fetching budgets...', { page: currentPage.value, limit: itemsPerPage.value, filter: currentFilter.value, sort: currentSort.value });
    try {
      const params: Record<string, string | number> = {
        page: currentPage.value,
        limit: itemsPerPage.value,
        ...(currentFilter.value !== 'all' && { status: currentFilter.value }),
        sort: `${currentSort.value.sortOrder === 'desc' ? '-' : ''}${currentSort.value.sortBy}`,
      };

      // TODO: Replace '/api/budgets' with actual API endpoint from config/env
      const response = await $fetch<PaginatedBudgetsDTO>('/api/v0/budgets/', {
        method: 'GET', // Ensure method is GET
        params: params,
      });

      budgets.value = response.items.map(mapBudgetDTOToViewModel);
      totalBudgets.value = response.total;

    } catch (err: unknown) {
      console.error('Error fetching budgets:', err);
      error.value = 'Failed to fetch budgets. Please try again.';
      budgets.value = [];
      totalBudgets.value = 0;
    } finally {
      isLoading.value = false;
    }
  }

  function setFilter(filter: BudgetFilterValue) {
    if (currentFilter.value !== filter) {
      currentFilter.value = filter;
      currentPage.value = 1; // Reset page when filter changes
      fetchBudgets(); // Refetch data
    }
  }

  function setPage(page: number) {
    if (page > 0 && currentPage.value !== page) {
      currentPage.value = page;
      fetchBudgets(); // Refetch data
    }
  }

  function setItemsPerPage(size: number) {
    if (size > 0 && itemsPerPage.value !== size) {
      itemsPerPage.value = size;
      currentPage.value = 1; // Reset page when limit changes
      fetchBudgets(); // Refetch data
    }
  }

  function setSort(sortOption: BudgetSortOption) {
    if (currentSort.value.sortBy !== sortOption.sortBy || currentSort.value.sortOrder !== sortOption.sortOrder) {
      currentSort.value = sortOption;
      fetchBudgets();
    }
  }

  async function createBudget(payload: CreateBudgetRequestPayload): Promise<void> {
    isLoading.value = true;
    error.value = null;
    try {
      console.log('Sending create budget request:', payload);
      const response = await $fetch('/api/v0/budgets/', {
        method: 'POST',
        body: payload,
      });
      console.log('Create budget response:', response);
      currentPage.value = 1;
      await fetchBudgets();
    } catch (err: unknown) {
      console.error('Error creating budget:', err);
      let apiError = 'An unexpected error occurred.';
      // Refined Type guard for $fetch errors (ofetch)
      if (typeof err === 'object' && err !== null) {
        if ('data' in err && typeof err.data === 'object' && err.data !== null) {
          const errorData = err.data as { message?: string; detail?: string };
          apiError = errorData.message || errorData.detail || apiError;
        } else if ('message' in err && typeof err.message === 'string') {
          // Handle generic Error objects
          apiError = err.message;
        }
      }
      error.value = `Failed to create budget: ${apiError} Please check your input and try again.`;
    } finally {
      isLoading.value = false;
    }
  }

  return {
    budgets,
    totalBudgets,
    currentPage,
    itemsPerPage,
    currentFilter,
    currentSort,
    isLoading,
    error,
    fetchBudgets,
    setFilter,
    setPage,
    setItemsPerPage,
    setSort,
    createBudget,
  };
});
