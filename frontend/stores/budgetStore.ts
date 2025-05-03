// stores/budgetStore.ts
import { ref, computed, watch } from 'vue'
import { defineStore } from 'pinia'
import { useQuery } from '@/composables/useQuery'
import { useCommand } from '@/composables/useCommand'
import { BudgetService } from '@/services/BudgetService'
import type {
    BudgetFilterValue,
    BudgetSortOption,
    BudgetListItemViewModel,
    Budget // Import Budget type itself
} from '@/types/budget'
import type {
    CreateBudgetRequestPayload,
    PaginatedItems, // Import PaginatedItems from dtos
    DomainError
} from '@/types/dtos'

// Mapping function remains largely the same, using Budget type
function mapBudgetToViewModel(budget: Budget): BudgetListItemViewModel {
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const endDate = new Date(budget.endDate);
    const deactivationDate = budget.deactivationDate ? new Date(budget.deactivationDate) : null;

    let status: 'active' | 'expired' | 'inactive';
    let statusLabel: string;

    if (deactivationDate && deactivationDate <= today) {
        status = 'inactive';
        statusLabel = 'Inactive';
    }
    else if (endDate < today) {
        status = 'expired';
        statusLabel = 'Expired';
    }
    else {
        status = 'active';
        statusLabel = 'Active';
    }

    return {
        id: budget.id,
        name: budget.name,
        status: status,
        statusLabel: statusLabel,
        dateRange: `${budget.startDate.split('T')[0]} - ${budget.endDate.split('T')[0]}`, // Basic range string
        limitFormatted: `${budget.totalLimit.amount} ${budget.totalLimit.currency}`, // Basic amount string
        currency: budget.currency,
        startDate: budget.startDate,
        endDate: budget.endDate,
    };
}

export const useBudgetStore = defineStore('budgetStore', () => {
    // State Refs for filters, pagination, sorting
    const currentPage = ref<number>(1);
    const itemsPerPage = ref<number>(10);
    const currentFilter = ref<BudgetFilterValue>('all');
    const currentSort = ref<BudgetSortOption>({ sortBy: 'name', sortOrder: 'asc' });

    // Instantiate BudgetService
    const budgetService = new BudgetService();

    // --- useQuery for fetching budgets ---
    const queryKey = computed(() => {
        return `budgets-list-${currentPage.value}-${itemsPerPage.value}-${currentFilter.value}-${currentSort.value.sortBy}-${currentSort.value.sortOrder}`;
    });

    const fetcherParams = computed(() => ({
        page: currentPage.value,
        limit: itemsPerPage.value,
        status: currentFilter.value,
        sort: `${currentSort.value.sortOrder === 'desc' ? '-' : ''}${currentSort.value.sortBy}`,
    }));

    // Provide unknown as the second type argument
    const { data: paginatedBudgetsData, pending: isLoading, error: queryError, refresh: refreshBudgets } = useQuery<PaginatedItems<Budget>, unknown>(
        queryKey,
        () => budgetService.listBudgets(fetcherParams.value),
        {
            lazy: false,
        },
         [currentPage, itemsPerPage, currentFilter, currentSort] // Pass refs directly
    );

    // Computed values derived from useQuery data
    const budgets = computed(() => paginatedBudgetsData.value?.items.map(mapBudgetToViewModel) ?? []);
    const totalBudgets = computed(() => paginatedBudgetsData.value?.total ?? 0);
    const error = ref<string | null>(null);

    // Watch for query errors and update the local error ref
    watch(queryError, (newError) => {
        error.value = newError ? newError.message : null;
    });

    // --- Methods to change state (trigger useQuery refresh via watched refs) ---
    function setFilter(filter: BudgetFilterValue) {
        if (currentFilter.value !== filter) {
            currentFilter.value = filter;
            currentPage.value = 1;
        }
    }

    function setPage(page: number) {
        if (page > 0 && currentPage.value !== page) {
            currentPage.value = page;
        }
    }

    function setItemsPerPage(size: number) {
        if (size > 0 && itemsPerPage.value !== size) {
            itemsPerPage.value = size;
            currentPage.value = 1;
        }
    }

    function setSort(sortOption: BudgetSortOption) {
        if (currentSort.value.sortBy !== sortOption.sortBy || currentSort.value.sortOrder !== sortOption.sortOrder) {
            currentSort.value = sortOption;
            currentPage.value = 1;
        }
    }

    // --- useCommand for creating a budget ---
    const { execute: executeCreateBudget, loading: isCreating, error: createError } = useCommand<CreateBudgetRequestPayload>(
        (payload) => budgetService.createBudget(payload),
        {
            onSuccess: async () => {
                console.log('Budget created successfully, refreshing list...');
                currentPage.value = 1;
                await refreshBudgets();
            },
            onError: (err: DomainError) => {
                error.value = `Failed to create budget: ${err.message}. Please check input.`;
                console.error('Error creating budget:', err);
            }
        }
    );

    async function createBudget(payload: CreateBudgetRequestPayload): Promise<void> {
       error.value = null;
       await executeCreateBudget(payload);
    }

     watch(createError, (newError) => {
         if (newError && !error.value) {
             error.value = `Failed to create budget: ${newError.message}`;
         }
     });

    return {
        budgets,
        totalBudgets,
        currentPage,
        itemsPerPage,
        currentFilter,
        currentSort,
        isLoading,
        isCreating,
        error,
        fetchBudgets: refreshBudgets,
        setFilter,
        setPage,
        setItemsPerPage,
        setSort,
        createBudget,
    };
});
