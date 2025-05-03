<script setup lang="ts">
import { ref, computed, watch } from 'vue';

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
    UpdateTransactionPayload,
} from '@/types/dtos';

import { useTransactionApi } from '@/composables/useTransactionApi';
import { toast } from "vue-sonner"

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

// Use the refactored composable
const {
    createTransaction,
    updateTransaction,
    loadingCreate,
    errorCreate,
    loadingUpdate,
    errorUpdate,
} = useTransactionApi(computed(() => props.budget.id));

// Determine loading state based on mode
const isLoading = computed(() => props.mode === 'create' ? loadingCreate.value : loadingUpdate.value);

// Use a local ref for displaying errors in the modal
const displayError = ref<string | null>(null);

// Watch for API errors from the composable and update local display error
watch(errorCreate, (newError) => {
  if (props.mode === 'create' && newError) {
    displayError.value = newError.message || 'Failed to create transaction.';
     toast({ variant: "destructive", title: "API Error", description: displayError.value });
  }
});
watch(errorUpdate, (newError) => {
  if (props.mode === 'edit' && newError) {
    displayError.value = newError.message || 'Failed to update transaction.';
    toast({ variant: "destructive", title: "API Error", description: displayError.value });
  }
});

// Convert budget dates to Date objects for the form
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
  displayError.value = null;

  if (!formData.categoryId || formData.amount === undefined || formData.amount === null || !formData.occurredDate) {
      displayError.value = "Missing required fields. Please check the form.";
      toast({
          variant: "destructive",
          title: "Validation Error",
          description: displayError.value,
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

  try {
    if (props.mode === 'create') {
        await createTransaction(apiPayloadBase as CreateTransactionPayload);
        if (!errorCreate.value) {
           toast({ title: "Success", description: "Transaction created successfully!" });
           emit('transactionSaved');
           emit('close');
        }
    } else if (props.mode === 'edit' && props.transactionData?.id) {
        await updateTransaction({
            transactionId: props.transactionData.id,
            payload: apiPayloadBase as UpdateTransactionPayload
        });
         if (!errorUpdate.value) {
            toast({ title: "Success", description: "Transaction updated successfully!" });
            emit('transactionSaved');
            emit('close');
         }
    } else {
        throw new Error('Invalid mode or missing transaction ID for edit.');
    }

  } catch (error) {
      if (!displayError.value) {
          const message = error instanceof Error ? error.message : 'An unexpected error occurred during submission.';
          displayError.value = message;
          toast({ variant: "destructive", title: "Submission Error", description: message });
      }
      console.error("Error during form submission:", error);
  }
}

function handleOpenChange(open: boolean) {
  if (!open) {
    displayError.value = null;
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
        :is-loading="isLoading"
        class="py-4"
        @submit="handleFormSubmit"
      />

       <!-- Display the local error state -->
       <div v-if="displayError" class="text-destructive text-sm font-medium p-4 bg-destructive/10 rounded-md">
         {{ displayError }}
       </div>

       <DialogFooter class="pt-4">
         <DialogClose as-child>
           <Button type="button" variant="outline" :disabled="isLoading">Cancel</Button>
         </DialogClose>
         <!-- Submit button is handled within TransactionForm, it receives isLoading prop -->
         <!-- We don't need a separate submit button here -->
       </DialogFooter>
    </DialogContent>
  </Dialog>
</template>
