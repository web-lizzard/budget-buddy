<script setup lang="ts">
import { computed } from 'vue';

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogClose
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button';
import TransactionForm, { type TransactionSubmitPayload } from './TransactionForm.vue';

import type { Category } from '@/types/category';
import type { Budget } from '@/types/budget';
import type { Transaction } from '@/types/transaction';
import type { InitialTransactionFormData } from '@/schemas/transactionFormSchema';
import type {
    CreateTransactionPayload,
} from '@/types/dtos';

import { toast } from "vue-sonner"
import { TransactionService } from '~/services/TransactionService';

const props = withDefaults(defineProps<{
  isOpen: boolean;
  mode: 'create' | 'edit';
  budget: Pick<Budget, 'currency' | 'startDate' | 'endDate' | 'id'>;
  availableCategories: Pick<Category, 'id' | 'name'>[];
  transactionData?: Pick<Transaction, 'id' | 'categoryId' | 'amount' | 'type' | 'date' | 'description'> | null;
}>(), {
  transactionData: null,
});

const emit = defineEmits<{
  (e: 'close' | 'transactionSaved'): void;
}>();

const transactionService = new TransactionService(props.budget.id);

const {
    execute: handleTransactionSubmit,
    loading,
    error,
} = useCommand(async (payload: CreateTransactionPayload) => {
  if (props.mode === 'create') {
    await transactionService.createTransaction(payload);
  } else if (props.mode === 'edit' && props.transactionData?.id) {
    await transactionService.updateTransaction(props.transactionData.id, payload);
  }
})


const formBudget = computed(() => ({
  currency: props.budget.currency,
  startDate: new Date(props.budget.startDate),
  endDate: new Date(props.budget.endDate),
}));

const initialFormData = computed<InitialTransactionFormData>(() => {
  if (props.mode === 'edit' && props.transactionData) {
    return {
      categoryId: props.transactionData.categoryId,
      amount: typeof props.transactionData.amount === 'object' ? props.transactionData.amount.amount : null,
      type: props.transactionData.type,
      occurredDate: new Date(props.transactionData.date),
      description: props.transactionData.description ?? undefined,
    };
  } else {
    return {
      type: 'EXPENSE',
      occurredDate: new Date(),
    };
  }
});


async function handleFormSubmit(formData: TransactionSubmitPayload) {

  if (!formData.categoryId || formData.amount === undefined || formData.amount === null || !formData.occurredDate) {
      toast({
          variant: "destructive",
          title: "Validation Error",
          description: "Missing required fields. Please check the form.",
      })
      return;
  }

  const apiPayloadBase = {
      category_id: formData.categoryId,
      amount: { amount: formData.amount },
      transaction_type: formData.type,
      occurred_date: formData.occurredDate.toISOString(),
      description: formData.description || undefined,
  };

  await handleTransactionSubmit(apiPayloadBase as CreateTransactionPayload);

  if (!error.value) {
    toast({ title: "Success", description: "Transaction created successfully!" });
    emit('transactionSaved');
  }
}

function handleOpenChange(open: boolean) {
  if (!open) {
    emit('close');
  }
}

</script>

<template>
 <Dialog :open="isOpen" @update:open="handleOpenChange">
    <DialogContent class="sm:max-w-[425px]">
      <DialogHeader>
        <DialogTitle>{{ mode === 'create' ? 'Add Transaction' : 'Edit Transaction' }}</DialogTitle>
        <DialogDescription>
          {{ mode === 'create' ? 'Enter the details for the new transaction.' : 'Update the details of the transaction.' }}
        </DialogDescription>
      </DialogHeader>

      <TransactionForm
        :initial-data="initialFormData"
        :budget="formBudget"
        :available-categories="availableCategories"
        :is-loading="loading"
        class="py-4"
        @submit="handleFormSubmit"
      />

       <!-- Display the local error state -->
       <div v-if="error" class="text-destructive text-sm font-medium p-4 bg-destructive/10 rounded-md">
         {{ error }}
       </div>

       <DialogFooter class="pt-4">
         <DialogClose as-child>
           <Button type="button" variant="outline" :disabled="loading">Cancel</Button>
         </DialogClose>
         <!-- Submit button is handled within TransactionForm, it receives isLoading prop -->
         <!-- We don't need a separate submit button here -->
       </DialogFooter>
    </DialogContent>
  </Dialog>
</template>
