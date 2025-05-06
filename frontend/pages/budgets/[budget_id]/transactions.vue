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
import TransactionList from '@/components/TransactionList.vue';
import ConfirmDeleteModal from '@/components/ConfirmDeleteModal.vue';
import AddEditTransactionModal from '@/components/transaction/AddEditTransactionModal.vue';
import { toast } from "vue-sonner";
import {Skeleton} from '@/components/ui/skeleton';
import { useTransactionsViewModel } from '~/composables/useTransactionsViewModel';

const DEFAULT_PAGE_SIZE = 20;

const INITIAL_QUERY_PARAMS = {
  page: 1,
  limit: DEFAULT_PAGE_SIZE
}

const route = useRoute();
const budgetId = computed(() => route.params.budget_id as string);

const { service: budgetService } = useBudgetService();
const { service: transactionService } = useTransactionService();

const {
  data: budgetData,
  pending: isBudgetLoading,
  error: budgetError,
  refresh: refreshBudget
} = useQuery<Budget | null>(
  computed(() => `budget-${budgetId.value}`),
  () => budgetId.value ? budgetService.getBudgetById(budgetId.value) : Promise.resolve(null),
);

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

const {
  data: transactionsData,
  pending: isTransactionsLoading,
  error: transactionsError,
  refresh: refreshTransactions
} = useQuery<PaginatedItems<Transaction>, GetTransactionsParams>(
  computed(() => `transactions-${budgetId.value}`),
  (params) => transactionService.getTransactions(params || INITIAL_QUERY_PARAMS),
  { initialParams: INITIAL_QUERY_PARAMS },
);

const isDeleteModalOpen = ref(false);
const transactionToDeleteId = ref<string | null>(null);
const isEditModalOpen = ref(false);
const transactionToEdit = ref<Transaction | null>(null);

const { transactionViewModels } = useTransactionsViewModel(
  transactionsData,
  budgetData
);

const originalTransactionToEdit = computed(() => {
  if (!transactionToEdit.value?.id) return null;
  return transactionsData.value?.items.find(t => t.id === transactionToEdit.value?.id) || null;
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
      refreshTransactions({
        page: pagination.value.page,
        limit: pagination.value.limit
      });
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
  refreshTransactions({
    page: pagination.value.page,
    limit: pagination.value.limit
  });
};

const loadMoreTransactions = async () => {
  if (!pagination.value.hasMore || isTransactionsLoading.value) return;

    const nextPage = pagination.value.page + 1;
    const params: GetTransactionsParams = {
      page: nextPage,
      limit: pagination.value.limit
    };

    await refreshTransactions(params);
};

const handleEditTransaction = (id: string) => {
  const transaction = transactionsData.value?.items.find(t => t.id === id);
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
    refreshTransactions({
      page: pagination.value.page,
      limit: pagination.value.limit
    });
  }
};

watch(() => transactionsData.value, (newData) => {
  if (newData) {
    pagination.value = {
      total: newData.total,
      page: newData.skip ? Math.floor(newData.skip / newData.limit) + 1 : 1,
      limit: newData.limit,
      hasMore: (newData.skip || 0) + newData.limit < newData.total
    };
  }
}, { immediate: true });
</script>

<template>
  <div class="container mx-auto py-6">
    <h1 class="text-2xl font-bold mb-6">Transaction History</h1>

    <div v-if="isBudgetLoading || (!transactionsData && isTransactionsLoading)" class="flex justify-center py-12">
      <Skeleton class="w-full h-48" />
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
      v-else-if="!isTransactionsLoading && transactionsData && transactionsData.items.length === 0 && !hasError"
      class="rounded-md border border-border p-8 my-4 text-center"
    >
      <h3 class="text-lg font-medium">No transactions yet</h3>
      <p class="text-muted-foreground mt-2">
        There are no transactions recorded for this budget.
      </p>
    </div>

    <div v-else-if="transactionsData && transactionsData.items.length > 0">
      <TransactionList
        :transactions="transactionViewModels"
        :is-loading-more="isTransactionsLoading"
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
