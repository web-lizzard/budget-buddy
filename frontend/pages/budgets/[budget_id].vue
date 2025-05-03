<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import BudgetSummaryCard from '@/components/budget/detail/BudgetSummaryCard.vue'
import OverallStatsCard from '@/components/budget/detail/OverallStatsCard.vue'
import CategorySpendingChart from '@/components/budget/detail/CategorySpendingChart.vue'
import RecentTransactionsTable from '@/components/budget/detail/RecentTransactionsTable.vue'
import CategoryList from '@/components/budget/detail/CategoryList.vue'
import ActionButtons from '@/components/budget/detail/ActionButtons.vue'
import AddEditTransactionModal from '@/components/transaction/AddEditTransactionModal.vue'
import { Skeleton } from '@/components/ui/skeleton'
import type { ChartDataViewModel, TransactionViewModel, CategoryListItemViewModel } from '~/types/viewmodels'
import type { TransactionType } from '~/types/transaction'
import type { Category } from '~/types/category'
import type { CategoryStatistics } from '~/types/statistics'
import { useQuery } from '~/composables/useQuery'
import { BudgetService } from '~/services/BudgetService'
import { TransactionService } from '~/services/TransactionService'
import { useIntervalAction } from '~/composables/useIntervalAction'

const route = useRoute()
const router = useRouter()

const budgetIdParam = computed(() => route.params.budget_id)


// Added reactive state for controlling the Add/Edit Transaction modal
const isTransactionModalOpen = ref(false)

const budgetService = new BudgetService()
const transactionService = new TransactionService(budgetIdParam.value as string)



const { data: budgetData, pending, error, refresh } = useQuery(
  `budget-${budgetIdParam.value}`,
  () => budgetService.getBudgetById(budgetIdParam.value as string),
  {
    onError() {
        throw createError({
            statusCode: 404,
            statusMessage: 'Budget not found',
            fatal: true
        })
    },
  }
)

const { data: recentTransactions, pending: pendingTransactions, refresh: refreshTransactions } = useQuery(
  `recent-transactions-${budgetIdParam.value}`,
  async () => {
    return (await transactionService.getRecentTransactions(3)).items
  },
)


const { data: statisticsData, pending: pendingStats, refresh: refreshStats } = useQuery(
  `budget-stats-${budgetIdParam.value}`,
  async () => {
    return budgetService.getBudgetStatistics(budgetIdParam.value as string);
  },
)

const statsTimestamp = computed(() => {
  if (!statisticsData.value) return null;
  return statisticsData.value.creationDate;
})

const timestamp = ref(new Date().toISOString()) // Store timestamp in UTC format

const { executeAction: executeRefreshStats } = useIntervalAction(
  () => refreshStats(),
  () => {
    if (!statsTimestamp.value) return false;

    // TODO: This is a hack to compare the timestamps. We should use a more reliable method. Backend should returns timezone offset
    const timeStamp = new Date(timestamp.value)
    const statsTimeStamp = new Date(statsTimestamp.value)
    const minutes = timeStamp.getMinutes()
    const minutesStats = statsTimeStamp.getMinutes()
    return minutes <= minutesStats;
  }
)




const categoryMap = computed(() => {
    const map = new Map<string, string>();
    budgetData.value?.categories.forEach(cat => map.set(cat.id, cat.name));
    return map;
});

const transactionViewModels = computed((): TransactionViewModel[] => {

    if (!recentTransactions.value) return [];
    return recentTransactions.value.map((tx) => ({
        id: tx.id,
        date: new Date(tx.date), // Convert string date to Date object
        categoryName: categoryMap.value.get(tx.categoryId) ?? 'Uncategorized', // Get name from map
        type: tx.type.toUpperCase() as TransactionType,
        amount: tx.amount,
    }));
});

const categorySpendingChartData = computed((): ChartDataViewModel | null => {
    if (!statisticsData.value || !statisticsData.value.categoriesStatistics || statisticsData.value.categoriesStatistics.length === 0) {
        return null; // No data for chart
    }

    const labels: string[] = [];
    const data: number[] = [];
    const backgroundColors: string[] = [
        '#41B883', '#E46651', '#00D8FF', '#DD1B16', '#FFB44C', '#34495E', '#9B59B6', '#3498DB', '#1ABC9C', '#F1C40F'
    ];

    statisticsData.value.categoriesStatistics.forEach((catStat) => {
        if (catStat.usedLimit && catStat.usedLimit.amount > 0) {
            labels.push(categoryMap.value.get(catStat.categoryId) ?? `Unknown Cat ${catStat.categoryId.substring(0,4)}`);
            data.push(catStat.usedLimit.amount);
        }
    });

    if (data.length === 0) return null;

    return {
        labels: labels,
        datasets: [{
            data: data,
            backgroundColor: backgroundColors.slice(0, data.length) // Use generated colors
        }]
    };
});

const categoryListViewModels = computed((): CategoryListItemViewModel[] => {
    if (!budgetData.value?.categories) return [];

    const statsMap = new Map<string, CategoryStatistics>();
    statisticsData.value?.categoriesStatistics?.forEach(stat => {
        statsMap.set(stat.categoryId, stat);
    });

    return budgetData.value.categories.map((cat: Category) => {
        const stats = statsMap.get(cat.id);
        const currentValue = stats?.usedLimit?.amount ?? 0; // Use used_limit as current spending
        const limitValue = cat.limit?.amount ?? 0;
        let progressPercentage = 0;
        if (limitValue > 0) {
            progressPercentage = (currentValue / limitValue) * 100;
        }
         else if (currentValue > 0) {
            progressPercentage = 100; // Show 100% if limit is 0 but there's spending
        }

        return {
            id: cat.id,
            name: cat.name,
            limit: cat.limit,
            currentBalance: stats?.currentBalance,
            usedLimit: stats?.usedLimit,
            progressPercentage: progressPercentage
        };
    });
});

// --- Event Handlers ---

const handleEditCategory = (categoryId: string) => {
    console.log('Action: Edit category', categoryId);
    // Example Navigation:
    router.push(`/budgets/${budgetIdParam.value}/categories/${categoryId}/edit`);
};

const handleRemoveCategory = (categoryId: string) => {
    console.log('Action: Remove category', categoryId);
    // TODO: Open RemoveCategoryModal - Requires state management for modal
    alert(`Placeholder: Trigger remove modal for category ${categoryId}`);
};

const handleAddTransaction = () => {
    console.log('Action: Add transaction');
    // Open the Add/Edit Transaction modal instead of navigating
    isTransactionModalOpen.value = true;
};

const handleTransactionSaved = () => {
    // Called when the modal successfully saves a transaction
    isTransactionModalOpen.value = false;
    timestamp.value = new Date().toISOString();
    refresh();
    executeRefreshStats();
    refreshTransactions();
};

const handleDeactivateBudget = () => {
    console.log('Action: Deactivate budget', budgetIdParam.value);
    // TODO: Implement API call to PATCH /budgets/{id}/deactivate
    // TODO: Show confirmation, handle loading/error state, refresh data
    alert(`Placeholder: Deactivate budget ${budgetIdParam.value}`);
};


</script>

<template>
  <div class="container mx-auto p-4">
    <h1 class="text-2xl font-bold mb-4">Budget Detail</h1>
    <div v-if="error">
      <p class="text-red-500">Error: {{ error.message }}</p>
      <button class="mt-2 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600" @click="() => refresh()">Try Again</button>
    </div>

    <div v-else class="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div class="lg:col-span-2 space-y-4">
            <Skeleton v-if="pending" class="h-32 w-full" />
            <BudgetSummaryCard v-if="budgetData" :budget="budgetData" />

            <Skeleton v-if="pending" class="h-12 w-full" />
            <ActionButtons
              v-else-if="budgetData"
              :budget-id="budgetIdParam as string"
              :is-active="budgetData.isActive"
              @add-transaction="handleAddTransaction"
              @deactivate-budget="handleDeactivateBudget"
            />

            <Skeleton v-if="pendingTransactions" class="h-64 w-full" />
            <RecentTransactionsTable
              v-else-if="recentTransactions"
              :transactions="transactionViewModels"
              :budget-id="budgetIdParam as string"
            />

            <Skeleton v-if="pendingStats" class="h-40 w-full" />
            <OverallStatsCard
              v-else-if="statisticsData"
              :statistics="statisticsData"
              :budget-limit="budgetData?.totalLimit ?? { amount: 0, currency: 'USD' }"
            />
        </div>

        <div class="lg:col-span-1 space-y-4">
            <Skeleton v-if="pendingStats" class="h-64 w-full" />
            <CategorySpendingChart
              v-else-if="categorySpendingChartData"
              :chart-data="categorySpendingChartData"
            />

            <Skeleton v-if="pending || pendingStats" class="h-96 w-full" />
            <CategoryList
              v-else-if="budgetData && categoryListViewModels.length"
              :categories="categoryListViewModels"
              @edit-category="handleEditCategory"
              @remove-category="handleRemoveCategory"
            />
        </div>
    </div>

    <AddEditTransactionModal
      v-if="budgetData"
      :is-open="isTransactionModalOpen"
      mode="create"
      :budget="budgetData"
      :available-categories="budgetData?.categories || []"
      @close="isTransactionModalOpen = false"
      @transaction-saved="handleTransactionSaved"
    />
  </div>
</template>
