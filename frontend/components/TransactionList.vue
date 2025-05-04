<script setup lang="ts">
import type { TransactionViewModel } from '@/types/viewmodels';
import InfiniteScrollTrigger from '@/components/InfiniteScrollTrigger.vue';
import TransactionListItem from '@/components/TransactionListItem.vue';

const props = defineProps<{
  transactions: TransactionViewModel[];
  isLoadingMore: boolean;
  hasMore: boolean;
}>();

const emit = defineEmits<{
  (e: 'edit-transaction' | "delete-transaction", id: string): void;
  (e: 'load-more'): void;
}>();

const handleEditClick = (id: string) => {
  emit('edit-transaction', id);
};

const handleDeleteClick = (id: string) => {
  emit('delete-transaction', id);
};

const handleIntersection = () => {
  if (props.hasMore && !props.isLoadingMore) {
    emit('load-more');
  }
};
</script>

<template>
  <div class="border rounded-md">
    <div v-if="transactions.length === 0 && !isLoadingMore" class="p-4 text-center text-muted-foreground">
      No transactions found.
    </div>

    <template v-else>
      <TransactionListItem
        v-for="transaction in transactions"
        :key="transaction.id"
        :transaction="transaction"
        class="border-b last:border-0"
        @edit-click="handleEditClick"
        @delete-click="handleDeleteClick"
      />
    </template>

    <InfiniteScrollTrigger
      v-if="hasMore"
      :disabled="isLoadingMore"
      @intersected="handleIntersection"
    >
      <div class="p-4 text-center">
        <p v-if="isLoadingMore" class="text-sm text-muted-foreground">
          Loading more transactions...
        </p>
      </div>
    </InfiniteScrollTrigger>
  </div>
</template>
