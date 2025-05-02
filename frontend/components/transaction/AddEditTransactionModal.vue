<script setup lang="ts">
import { ref, computed } from 'vue';

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

import type {
    CategoryViewModel,
    TransactionDataViewModel
} from '@/types/viewmodels';
import type {
    CreateTransactionPayload,
    UpdateTransactionPayload
} from '@/types/transaction';


import { useTransactionApi } from '@/composables/useTransactionApi';
import { toast } from "vue-sonner"


type BudgetViewModel = {
  currency: string;
  startDate: Date;
  endDate: Date;
  budgetId: string;
}



const props = withDefaults(defineProps<{
  isOpen: boolean;
  mode: 'create' | 'edit';
  budget: BudgetViewModel;
  availableCategories: CategoryViewModel[];
  transactionData?: TransactionDataViewModel | null;
}>(), {
  transactionData: null,
});

const emit = defineEmits<{
  (e: 'close' | 'transactionSaved'): void;
}>();

const isLoading = ref(false);
const error = ref<string | null>(null);
const { createTransaction, updateTransaction } = useTransactionApi(computed(() => props.budget.budgetId));

const initialFormData = computed(() => {
  if (props.mode === 'edit' && props.transactionData) {
    return {
      categoryId: props.transactionData.categoryId,
      amount: props.transactionData.amount,
      type: props.transactionData.type,
      occurredDate: new Date(props.transactionData.occurredDate),
      description: props.transactionData.description,
    };
  } else {
    return {};
  }
});


async function handleFormSubmit(formData: TransactionSubmitPayload) {
  isLoading.value = true;
  error.value = null;

  if (formData.categoryId === null || formData.amount === null || formData.occurredDate === null) {
      error.value = "Missing required fields. Please check the form.";
      isLoading.value = false;
      toast({
          variant: "destructive",
          title: "Validation Error",
          description: error.value,
      })
      return;
  }

  const apiPayload: CreateTransactionPayload | UpdateTransactionPayload = {
      category_id: formData.categoryId,
      amount: { amount: formData.amount },
      transaction_type: formData.type,
      occurred_date: formData.occurredDate.toISOString(),
      description: formData.description || undefined,
  };


  try {
    if (props.mode === 'create') {
        await createTransaction(apiPayload as CreateTransactionPayload);
        toast({ title: "Success", description: "Transaction created successfully!" });
    } else if (props.mode === 'edit' && props.transactionData?.id) {
        await updateTransaction(props.transactionData.id, apiPayload as UpdateTransactionPayload);
        toast({ title: "Success", description: "Transaction updated successfully!" });
    } else {
        throw new Error('Invalid mode or missing transaction ID for edit.');
    }

    emit('transactionSaved');
    emit('close');

  } catch (apiError: unknown) {
      const errorMessage = apiError instanceof Error ? apiError.message : "Failed to save transaction. Please try again.";
      error.value = errorMessage;
      toast({ variant: "destructive", title: "Error", description: errorMessage });
  } finally {
      isLoading.value = false;
  }
}

function handleOpenChange(open: boolean) {
  if (!open) {
    error.value = null;
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
        :budget="budget"
        :available-categories="availableCategories"
        :is-loading="isLoading"
        class="py-4"
        @submit="handleFormSubmit"
      />

       <div v-if="error" class="text-destructive text-sm font-medium p-4 bg-destructive/10 rounded-md">
         {{ error }}
       </div>

       <DialogFooter class="pt-4">
         <DialogClose as-child>
           <Button type="button" variant="outline">Cancel</Button>
         </DialogClose>
       </DialogFooter>
    </DialogContent>
  </Dialog>
</template>
