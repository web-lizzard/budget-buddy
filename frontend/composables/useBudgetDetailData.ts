import { computed } from 'vue'
import { useQuery } from './useQuery' // Import useQuery
import { BudgetService } from '@/services/BudgetService' // Import BudgetService
import { TransactionService } from '@/services/TransactionService' // Import TransactionService
import type { BudgetStatistics } from '@/types/statistics'
import type { DomainError, PaginatedItems } from '@/types/dtos'
import type { Budget } from '@/types/budget'
import type { Transaction } from '@/types/transaction'

// Interface for the combined data structure
interface BudgetDetailCoreData {
    budget: Budget;
    transactions: PaginatedItems<Transaction>;
}

// Helper function to aggregate errors - you might want a more sophisticated strategy
function aggregateErrors(...errors: (DomainError | null)[]): DomainError | null {
    for (const error of errors) {
        if (error) {
            // Return the first encountered error
            // You could customize this: combine messages, prioritize certain types, etc.
            return error;
        }
    }
    return null;
}

// Simplified budgetId input - assuming it's stable per component instance
export const useBudgetDetailData = (budgetId: string) => {
    const budgetService = new BudgetService();
    const transactionService = new TransactionService(budgetId);

    // --- Core Data Fetching (Budget + Transactions) ---
    const fetchCoreData = async (): Promise<BudgetDetailCoreData> => {
        const budgetPromise = budgetService.getBudgetById(budgetId);
        const transactionsPromise = transactionService.getRecentTransactions(3);
        const [budget, transactions] = await Promise.all([budgetPromise, transactionsPromise]);
        return { budget, transactions };
    };

    const {
        data: coreData,
        pending: pendingCore,
        error: errorCore,
        refresh: refreshCoreData, // Renamed refresh function
    } = useQuery<BudgetDetailCoreData, string>(
        `budget-core-${budgetId}`,
        fetchCoreData,
        { lazy: false, server: true } // Fetch eagerly
    );

    // --- Statistics Data Fetching (Lazy and Manual) ---
    const {
        data: statisticsData,
        pending: pendingStats,
        error: errorStats,
        refresh: refreshStats,
    } = useQuery<BudgetStatistics | null, BudgetDetailCoreData | null>(
        `budget-stats-${budgetId}`,
        () => {
          if (coreData.value && coreData.value.transactions.items.length > 0) {
            return budgetService.getBudgetStatistics(budgetId);
          }
          return Promise.resolve(null);
        },
        {
            lazy: true,          // Load lazily
            immediate: false,    // Don't execute immediately
            server: false,
        },
        [coreData]
    );


    // --- Computed Properties for Data Access ---
    const budgetData = computed(() => coreData.value?.budget);
    const recentTransactions = computed(() => coreData.value?.transactions.items ?? []);


    const error = computed(() => {
        // Prioritize core error, then stats error
        const firstError = aggregateErrors(errorCore.value, errorStats.value);
        if (firstError) {
            return firstError
        }
        return null;
    });

    return {
        budgetData,
        statisticsData,
        recentTransactions,
        error,
        pendingCore,
        pendingStats,
        refreshCoreData,         // Function to refresh budget and transactions
        refreshStats, // Function to manually fetch/refresh statistics
    };
}
