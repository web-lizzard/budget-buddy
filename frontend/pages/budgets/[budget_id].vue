<script setup lang="ts">
import { computed, watchEffect } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useBudgetDetailData } from '~/composables/useBudgetDetailData'
import { createError } from '#app'
import BudgetSummaryCard from '@/components/budget/detail/BudgetSummaryCard.vue'
import OverallStatsCard from '@/components/budget/detail/OverallStatsCard.vue'
import CategorySpendingChart from '@/components/budget/detail/CategorySpendingChart.vue'
import RecentTransactionsTable from '@/components/budget/detail/RecentTransactionsTable.vue'
import CategoryList from '@/components/budget/detail/CategoryList.vue'
import ActionButtons from '@/components/budget/detail/ActionButtons.vue'
import type { ChartDataViewModel, TransactionViewModel, CategoryListItemViewModel } from '~/types/viewmodels'
import type { Transaction } from '~/types/transaction'
import type { Category } from '~/types/category'
import type { CategoryStatistics } from '~/types/statistics'

const route = useRoute()
const router = useRouter()

const budgetIdParam = computed(() => route.params.budget_id)

// Validate the budgetId when the param changes. Throw 400 error if invalid.
// Use watchEffect to reactively check and throw error.
watchEffect(() => {
    const id = budgetIdParam.value;
    if (typeof id !== 'string' || !/^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$/.test(id)) {
        console.error('Invalid budget ID format in URL:', id)
        // Throw a non-fatal 400 error to let Nuxt handle it (e.g., show error page)
        throw createError({ statusCode: 400, statusMessage: 'Invalid Budget ID', fatal: true })
    }
})

// Now, we can safely assume budgetIdParam holds a valid string UUID if the effect didn't throw
// We pass the potentially changing param directly to the composable
const { budgetData, statisticsData, recentTransactions, pending, error, refresh } =
  useBudgetDetailData(budgetIdParam as ComputedRef<string>) // Assert type as string now

// --- Computed ViewModels ---

const categoryMap = computed(() => {
    const map = new Map<string, string>();
    budgetData.value?.categories.forEach(cat => map.set(cat.id, cat.name));
    return map;
});

const transactionViewModels = computed((): TransactionViewModel[] => {
    if (!recentTransactions.value) return [];
    return recentTransactions.value.map((tx: Transaction) => ({
        id: tx.id,
        date: new Date(tx.date), // Convert string date to Date object
        categoryName: categoryMap.value.get(tx.category_id) ?? 'Uncategorized', // Get name from map
        type: tx.type,
        amount: tx.amount
    }));
});

const categorySpendingChartData = computed((): ChartDataViewModel | null => {
    if (!statisticsData.value || !statisticsData.value.categories_statistics || statisticsData.value.categories_statistics.length === 0) {
        return null; // No data for chart
    }

    const labels: string[] = [];
    const data: number[] = [];
    const backgroundColors: string[] = [
        '#41B883', '#E46651', '#00D8FF', '#DD1B16', '#FFB44C', '#34495E', '#9B59B6', '#3498DB', '#1ABC9C', '#F1C40F'
    ];

    statisticsData.value.categories_statistics.forEach((catStat) => {
        if (catStat.used_limit && catStat.used_limit.amount > 0) {
            labels.push(categoryMap.value.get(catStat.category_id) ?? `Unknown Cat ${catStat.category_id.substring(0,4)}`);
            data.push(catStat.used_limit.amount);
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

// Prepare data for CategoryList
const categoryListViewModels = computed((): CategoryListItemViewModel[] => {
    if (!budgetData.value?.categories) return [];

    // Create a map of category stats for quick lookup
    const statsMap = new Map<string, CategoryStatistics>();
    statisticsData.value?.categories_statistics?.forEach(stat => {
        statsMap.set(stat.category_id, stat);
    });

    return budgetData.value.categories.map((cat: Category) => {
        const stats = statsMap.get(cat.id);
        const currentValue = stats?.used_limit?.amount ?? 0; // Use used_limit as current spending
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
            currentBalance: stats?.current_balance,
            usedLimit: stats?.used_limit,
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
     // Example Navigation:
    router.push(`/budgets/${budgetIdParam.value}/transactions/new`);
};

const handleDeactivateBudget = () => {
    console.log('Action: Deactivate budget', budgetIdParam.value);
    // TODO: Implement API call to PATCH /budgets/{id}/deactivate
    // TODO: Show confirmation, handle loading/error state, refresh data
    alert(`Placeholder: Deactivate budget ${budgetIdParam.value}`);
};

// TODO: Implement SkeletonLoader component
// TODO: Implement ErrorDisplay component

</script>

<template>
  <div class="container mx-auto p-4">
    <h1 class="text-2xl font-bold mb-4">Budget Detail</h1>

    <div v-if="pending">
      <p>Loading budget details...</p>
      <!-- TODO: SkeletonLoader -->
    </div>

    <div v-else-if="error">
      <p class="text-red-500">Error: {{ error.message }}</p>
      <p v-if="error.statusCode !== 400" class="text-sm text-muted-foreground">Status Code: {{ error.statusCode }}</p>
      <button v-if="error.statusCode !== 400" class="mt-2 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600" @click="() => refresh()">Try Again</button>
      <button v-else class="mt-2 px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600" @click="() => router.push('/budgets')">Go to Budgets</button>
    </div>

    <div v-else-if="budgetData" class="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <!-- Left Column (or Main Column on smaller screens) -->
        <div class="lg:col-span-2 space-y-4">
             <BudgetSummaryCard :budget="budgetData" />
             <OverallStatsCard
                :statistics="statisticsData"
                :budget-limit="budgetData.total_limit"
             />
            <!-- Render CategoryList -->
             <CategoryList
                :categories="categoryListViewModels"
                @edit-category="handleEditCategory"
                @remove-category="handleRemoveCategory"
              />
        </div>

        <!-- Right Column (or Second Column on smaller screens) -->
        <div class="lg:col-span-1 space-y-4">
            <CategorySpendingChart :chart-data="categorySpendingChartData" />
            <RecentTransactionsTable :transactions="transactionViewModels" :budget-id="budgetIdParam as string" />
            <!-- Use ActionButtons -->
            <ActionButtons
                :budget-id="budgetIdParam as string"
                :is-active="budgetData.is_active"
                @add-transaction="handleAddTransaction"
                @deactivate-budget="handleDeactivateBudget"
              />
        </div>
    </div>

    <div v-else>
      <p class="text-yellow-600">Budget data could not be loaded or is unavailable.</p>
    </div>

  </div>
</template>

<style scoped>
/* Scoped styles for the budget detail page */
</style>
