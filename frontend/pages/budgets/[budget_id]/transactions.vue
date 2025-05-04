<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import { useRoute } from 'vue-router';
import type { GetTransactionsParams } from '@/services/TransactionService';
import { useBudgetService, useTransactionService } from '@/composables/useServices';
import { useQuery } from '@/composables/useQuery';
import { useCommand } from '@/composables/useCommand';
import type { Budget } from '@/types/budget';
import type { Transaction } from '@/types/transaction';
import type { DomainError, PaginatedItems } from '@/types/dtos';
import type { TransactionViewModel } from '@/types/viewmodels';
import TransactionList from '@/components/TransactionList.vue';
import ConfirmDeleteModal from '@/components/ConfirmDeleteModal.vue';
import AddEditTransactionModal from '@/components/transaction/AddEditTransactionModal.vue';
import { toast } from "vue-sonner";

const DEFAULT_PAGE_SIZE = 20;

const route = useRoute();
const budgetId = computed(() => route.params.budget_id as string);

const { service: budgetService } = useBudgetService();
const { service: transactionService } = useTransactionService();

const {
  data: budgetData,
  pending: isBudgetLoading,
  error: budgetError,
  refresh: refreshBudget
} = useQuery<Budget | null, string>(
  computed(() => `budget-${budgetId.value}`),
  () => budgetId.value ? budgetService.getBudgetById(budgetId.value) : Promise.resolve(null),

);

const transactions = ref<Transaction[]>([]);
const pagination = ref<{
  total: number;
  page: number;
  limit: number;
  hasMore: boolean;
}>({
  total: 0,
  page: 1,
  limit: DEFAULT_PAGE_SIZE,
  hasMore: true
});
const isLoadingMore = ref(false);

const {
  data: initialTransactionsData,
  pending: isLoadingInitial,
  error: transactionsError,
  refresh: refreshTransactions
} = useQuery<PaginatedItems<Transaction>, string>(
  computed(() => `transactions-initial-${budgetId.value}`),
  () => transactionService.getTransactions({
    page: 1,
    limit: pagination.value.limit
  }),
  {},
);

watch(initialTransactionsData, (data) => {
  if (data) {
    transactions.value = data.items;
    pagination.value = {
      total: data.total,
      page: 1,
      limit: data.limit,
      hasMore: data.skip + data.limit < data.total
    };
  }
}, { immediate: true });

const isDeleteModalOpen = ref(false);
const transactionToDeleteId = ref<string | null>(null);
const isEditModalOpen = ref(false);
const transactionToEdit = ref<Transaction | null>(null);

const categoryMap = computed(() => {
  if (!budgetData.value) return new Map<string, string>();

  const map = new Map<string, string>();
  budgetData.value.categories.forEach(category => {
    map.set(category.id, category.name);
  });
  return map;
});

const transactionViewModels = computed(() => {
  return transactions.value.map(transaction => {
    return {
      id: transaction.id,
      date: new Date(transaction.date),
      categoryName: categoryMap.value.get(transaction.categoryId) || 'Unknown Category',
      type: transaction.type,
      amount: transaction.amount,
    } as TransactionViewModel;
  });
});

const originalTransactionToEdit = computed(() => {
  if (!transactionToEdit.value?.id) return null;
  return transactions.value.find(t => t.id === transactionToEdit.value?.id) || null;
});

const availableCategories = computed(() => {
  return budgetData.value?.categories.map(c => ({ id: c.id, name: c.name })) || [];
});

const { execute: executeDelete, loading: isDeleting } = useCommand(
  async () => {
    if (!transactionToDeleteId.value) return;
    await transactionService.deleteTransaction(transactionToDeleteId.value);
  },
  {
    onSuccess: () => {
      toast.success('Transaction deleted successfully!');
      if (transactionToDeleteId.value) {
        transactions.value = transactions.value.filter(t => t.id !== transactionToDeleteId.value);
      }
      isDeleteModalOpen.value = false;
      transactionToDeleteId.value = null;
    },
    onError: (error: DomainError) => {
      toast.error(`Failed to delete transaction: ${error.message}`);
      isDeleteModalOpen.value = false;
      transactionToDeleteId.value = null;
    },
  }
);

const handleTransactionSaved = () => {
  isEditModalOpen.value = false;
  transactionToEdit.value = null;
  refreshTransactions();
};

const loadMoreTransactions = async () => {
  if (!pagination.value.hasMore || isLoadingMore.value) return;

  isLoadingMore.value = true;
  try {
    const nextPage = pagination.value.page + 1;
    const params: GetTransactionsParams = {
      page: nextPage,
      limit: pagination.value.limit
    };

    const nextPageData = await transactionService.getTransactions(params);
    transactions.value = [...transactions.value, ...nextPageData.items];

    pagination.value = {
      total: nextPageData.total,
      page: nextPage,
      limit: nextPageData.limit,
      hasMore: nextPageData.skip + nextPageData.limit < nextPageData.total
    };
  } catch (error) {
    console.error('Failed to load more transactions:', error);
  } finally {
    isLoadingMore.value = false;
  }
};

const handleEditTransaction = (id: string) => {
  const transaction = transactions.value.find(t => t.id === id);
  if (transaction) {
    transactionToEdit.value = { ...transaction };
    isEditModalOpen.value = true;
  }
};

const handleDeleteTransaction = (id: string) => {
  transactionToDeleteId.value = id;
  isDeleteModalOpen.value = true;
};

const handleConfirmDelete = () => {
  executeDelete();
};

const handleCancelDelete = () => {
  isDeleteModalOpen.value = false;
  transactionToDeleteId.value = null;
};

const handleEditModalClose = () => {
  isEditModalOpen.value = false;
  transactionToEdit.value = null;
};

const hasError = computed(() => !!budgetError.value || !!transactionsError.value);
const errorMessage = computed(() => {
  if (budgetError.value?.status === 'budget_not_found') {
    return 'Budget not found. It may have been deleted or you don\'t have access to it.';
  }
  return budgetError.value?.message || transactionsError.value?.message || 'An error occurred while loading data.';
});

const handleRetry = () => {
  if (budgetError.value) {
    refreshBudget();
  }
  if (transactionsError.value) {
    refreshTransactions();
  }
};

</script>

<template>
  <div class="container mx-auto py-6">
    <h1 class="text-2xl font-bold mb-6">Transaction History</h1>

    <div v-if="isBudgetLoading || (isLoadingInitial && transactions.length === 0)" class="flex justify-center py-12">
      <p>Loading transactions...</p>
    </div>

    <div v-else-if="hasError" class="rounded-md border border-destructive p-4 my-4">
      <div class="flex items-start gap-4">
        <div>
          <p class="text-sm text-destructive">{{ errorMessage }}</p>
          <button
            class="mt-2 text-sm font-medium underline cursor-pointer"
            @click="handleRetry"
          >
            Try again
          </button>
        </div>
      </div>
    </div>

    <div
      v-else-if="!isLoadingInitial && transactions.length === 0 && !hasError"
      class="rounded-md border border-border p-8 my-4 text-center"
    >
      <h3 class="text-lg font-medium">No transactions yet</h3>
      <p class="text-muted-foreground mt-2">
        There are no transactions recorded for this budget.
      </p>
    </div>

    <div v-else-if="transactions.length > 0">
      <TransactionList
        :transactions="transactionViewModels"
        :is-loading-more="isLoadingMore"
        :has-more="pagination.hasMore"
        @edit-transaction="handleEditTransaction"
        @delete-transaction="handleDeleteTransaction"
        @load-more="loadMoreTransactions"
      />
    </div>

    <ConfirmDeleteModal
      :is-open="isDeleteModalOpen"
      title="Delete Transaction?"
      message="Are you sure you want to delete this transaction? This action cannot be undone."
      confirm-text="Delete"
      :is-confirming="isDeleting"
      @update:is-open="isDeleteModalOpen = $event"
      @confirm="handleConfirmDelete"
      @cancel="handleCancelDelete"
    />

    <AddEditTransactionModal
      v-if="budgetData"
      :is-open="isEditModalOpen"
      mode="edit"
      :budget="{ id: budgetData.id, currency: budgetData.currency, startDate: budgetData.startDate, endDate: budgetData.endDate }"
      :available-categories="availableCategories"
      :transaction-data="originalTransactionToEdit"
      @close="handleEditModalClose"
      @transaction-saved="handleTransactionSaved"
    />

  </div>
</template>

<style scoped>
</style>
