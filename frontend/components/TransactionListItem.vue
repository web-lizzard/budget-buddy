<script setup lang="ts">
import type { TransactionViewModel } from '@/types/viewmodels';
import { Button } from '@/components/ui/button';
import { formatCurrency } from '@/utils/currency';
import { format } from 'date-fns';

const props = defineProps<{
  transaction: TransactionViewModel;
}>();

const emit = defineEmits<{
  (e: 'edit' | "delete", id: string): void;
}>();

const formattedDate = computed(() => {
  try {
    return format(props.transaction.date, 'PP');
  } catch (e) {
    console.error('Error formatting date:', e);
    return 'Invalid Date';
  }
});

const formattedAmount = computed(() => {
  return formatCurrency(props.transaction.amount);
});

const amountClass = computed(() => {
  return props.transaction.type === 'INCOME' ? 'text-green-600' : 'text-red-600';
});

const onEditClick = () => {
  emit('edit', props.transaction.id);
};

const onDeleteClick = () => {
  emit('delete', props.transaction.id);
};
</script>

<template>
  <div class="p-4 flex justify-between items-center">
    <div class="flex-grow mr-4">
      <p class="font-medium">{{ transaction.categoryName }}</p>
      <p class="text-sm text-muted-foreground">
        {{ formattedDate }} - {{ transaction.type }}
      </p>
    </div>

    <div class="flex items-center space-x-4">
      <p :class="['font-medium', amountClass]">
        {{ transaction.type === 'INCOME' ? '+' : '-' }}
        {{ formattedAmount }}
      </p>

      <div class="flex gap-2">
        <Button
          variant="outline"
          size="sm"
          @click="onEditClick"
        >
          Edit
        </Button>
        <Button
          variant="destructive"
          size="sm"
          @click="onDeleteClick"
        >
          Delete
        </Button>
      </div>
    </div>
  </div>
</template>

<style scoped>
</style>
