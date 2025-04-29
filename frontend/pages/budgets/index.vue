<script setup lang="ts">
import { onMounted } from 'vue';
import { storeToRefs } from 'pinia';
import { useBudgetStore } from '@/stores/budgetStore';
import type { BudgetFilterValue, BudgetSortOption } from '@/types/budget';
import { useRouter } from 'vue-router'; // Import useRouter for navigation

// Import child components
import BudgetFilterTabs from '@/components/BudgetFilterTabs.vue';
import BudgetListTable from '@/components/BudgetListTable.vue'; // Uncomment the table import

// Import Shadcn UI components used directly here
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Button } from '@/components/ui/button' // Used for retry and empty state actions

const budgetStore = useBudgetStore();
const router = useRouter(); // Initialize router

// Use storeToRefs for reactive state
const {
  budgets,
  totalBudgets,
  currentPage,
  itemsPerPage,
  currentFilter,
  currentSort,
  isLoading,
  error
} = storeToRefs(budgetStore);

// Fetch budgets on mount
onMounted(() => {
  if (budgets.value.length === 0) {
    budgetStore.fetchBudgets();
  }
});

// Event Handlers
function handleFilterChange(newFilter: BudgetFilterValue) { // Use imported type
  budgetStore.setFilter(newFilter);
}

function handlePageChange(update: { page: number }) { // Update argument type if needed
  budgetStore.setPage(update.page);
}

function handleSortChange(newSort: BudgetSortOption) { // Use imported type
  budgetStore.setSort(newSort);
}

function handleRowClick(payload: { id: string }) {
  console.log('Navigate to budget details:', payload.id);
  router.push(`/budgets/${payload.id}`); // Implement navigation
}

function handleCreateClick() {
  console.log('Navigate to create budget page - Nav Skipped as requested');
  // router.push('/budgets/create'); // Navigation logic intentionally omitted
}

</script>

<template>
  <div class="container mx-auto p-4 space-y-6">
    <div class="flex justify-between items-center">
      <h1 class="text-3xl font-bold">My Budgets</h1>
      <!-- Use CreateBudgetButton component -->
      <Button @click="handleCreateClick">Create Budget</Button>
    </div>

    <!-- Use BudgetFilterTabs component -->
    <div class="pt-4">
        <BudgetFilterTabs :model-value="currentFilter" @update:model-value="handleFilterChange" />
    </div>

    <!-- Loading State -->
    <div v-if="isLoading">
        <BudgetListTable
          :budgets="[]"
          :is-loading="true"
          :pagination="{ currentPage: 1, itemsPerPage: itemsPerPage, totalItems: 0 }"
          :sorting="currentSort"
        />
    </div>

    <!-- Error State -->
    <Alert v-else-if="error" variant="destructive">
      <AlertTitle>Error Loading Budgets</AlertTitle>
      <AlertDescription>
        {{ error }}
        <Button variant="outline" size="sm" class="ml-4" @click="budgetStore.fetchBudgets">
            Retry
        </Button>
      </AlertDescription>
    </Alert>

    <!-- Content: Table or Empty State -->
    <div v-else>
      <!-- Show table only if there are budgets -->
      <BudgetListTable
         v-if="budgets.length > 0"
         :budgets="budgets"
         :is-loading="false"
         :pagination="{ currentPage: currentPage, itemsPerPage: itemsPerPage, totalItems: totalBudgets }"
         :sorting="currentSort"
         @update:pagination="handlePageChange"
         @update:sorting="handleSortChange"
         @row-click="handleRowClick"
      />
      <!-- Empty State -->
      <div v-else class="text-center py-10 border rounded-md bg-card text-card-foreground">
            <h3 class="text-lg font-semibold">No Budgets Found</h3>
            <p class="text-muted-foreground mt-1 px-4">No budgets match your current filter settings. Try selecting 'All' or create a new budget.</p>
            <div class="mt-4">
                <Button v-if="currentFilter !== 'all'" variant="outline" size="sm" @click="handleFilterChange('all')">
                    Show All Budgets
                </Button>
                <!-- Create button handled by the main one, removed here -->
            </div>
        </div>
    </div>

  </div>
</template>

<style scoped>
/* No additional styles needed for now */
</style>
