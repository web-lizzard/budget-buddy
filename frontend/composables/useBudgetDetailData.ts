import { ref, computed, type MaybeRef, unref } from 'vue'
import { z } from 'zod'
import type { Budget } from '../types/budget'
import type { BudgetStatistics } from '../types/statistics'
import { BudgetSchema } from '@/schemas/budgetSchema'
import { BudgetStatisticsSchema } from '@/schemas/statisticsSchema'
import { TransactionSchema } from '@/schemas/transactionSchema'
import { useAsyncData, createError } from '#app'

// Helper function for safe Zod parsing
function safeParse<T extends z.ZodTypeAny>(schema: T, data: unknown): z.infer<T> {
  const result = schema.safeParse(data)
  if (result.success) {
    return result.data
  }
  else {
    throw Exception
  }
}

// Composable for fetching and managing data for the BudgetDetailView
export const useBudgetDetailData = (budgetId: MaybeRef<string>) => {
  const id = ref(budgetId)

  const { data, pending, error, refresh } = useAsyncData(
    `budget-detail-${id.value}`,
    async () => {
      const currentBudgetId = unref(id)


      console.log(`Fetching data for budget: ${currentBudgetId}`)

      const budgetUrl = `/api/v0/budgets/${currentBudgetId}`
      const statsUrl = `/api/v0/budgets/${currentBudgetId}/statistics`
      const transactionsUrl = `/api/v0/budgets/${currentBudgetId}/transactions?limit=3&sort=date:desc`

      let budgetResponse: unknown = null;
      let statsResponse: unknown = null;
      let transactionsResponse: unknown = null;

      try {
        [budgetResponse, transactionsResponse] = await Promise.all([
          $fetch(budgetUrl),
          $fetch(transactionsUrl),
        ])


        if (!transactionsResponse.items.length) {
          const budget = safeParse(BudgetSchema, budgetResponse, 'budget')
          return {
            budget: {
              ...budget,
              is_active: !budget.deactivation_date,
            },
            stats: null,
            transactions: [],
          }
        }

        try {
            statsResponse = await $fetch(statsUrl);
        } catch (statsError: unknown) {
            if (statsError instanceof Error && 'response' in statsError && statsError.response?.status === 404) {
                console.warn('Statistics endpoint returned 404. Proceeding without statistics.');
                statsResponse = null; // Indicates no stats available (yet)
            } else {
                 console.error('Error fetching statistics:', statsError)
                 // Re-throw other stats errors to be caught below
                 throw createError({ statusCode: statsError.response?.status || 500, statusMessage: 'Failed to fetch statistics', data: statsError.data });
            }
        }

      } catch (err: unknown) {
        console.error('Error fetching budget details or transactions:', err)
        const statusCode = err instanceof Error && 'response' in err && err.response?.status || 500;
        let message = 'Failed to fetch budget data.';
        if (statusCode === 404) message = 'Budget Not Found';
        else if (statusCode === 403) message = 'Access Denied';

        throw createError({ statusCode, statusMessage: message, fatal: true, data: err.data })
      }

      const parsedBudget = safeParse(BudgetSchema, budgetResponse, 'Budget')
      const parsedTransactions = safeParse(z.array(TransactionSchema), transactionsResponse.items, 'Transactions')

      if (!parsedBudget || !parsedTransactions) {
        console.error('Core data validation failed (Budget or Transactions).')
        throw createError({ statusCode: 500, statusMessage: 'Invalid core API response format', fatal: true })
      }

      let parsedStats: BudgetStatistics | null = null;
      if (statsResponse !== null) {
          parsedStats = safeParse(BudgetStatisticsSchema, statsResponse, 'Statistics');
          if (!parsedStats) {
              console.error('Statistics data validation failed.')
              throw createError({ statusCode: 500, statusMessage: 'Invalid statistics API response format', fatal: true })
          }
      }

      const budgetWithType: Budget = {
        ...parsedBudget,
        is_active: !parsedBudget.deactivation_date,
      }

      return {
        budget: budgetWithType,
        stats: parsedStats, // Can be null if 404 or validation failed
        transactions: parsedTransactions,
      }
    },
    {
      watch: [id],
      immediate: true,
      server: true,
    }
  )

  const budgetData = computed(() => data.value?.budget ?? null)
  const statisticsData = computed(() => data.value?.stats ?? null) // Will be null if fetch returned null
  const recentTransactions = computed(() => data.value?.transactions ?? [])

  return {
    budgetData,
    statisticsData,
    recentTransactions,
    pending,
    error,
    refresh,
  }
}
