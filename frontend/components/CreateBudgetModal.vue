<script setup lang="ts">
import { ref, watch } from 'vue';
import { storeToRefs } from 'pinia';
import CreateBudgetForm from '@/components/forms/CreateBudgetForm.vue';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { useBudgetStore } from '@/stores/budgetStore';
import { mapBudgetFormToRequestPayload } from '@/utils/mappers';
import type { BudgetFormInput } from '@/schemas/createBudgetSchemas';

// Define props using v-model pattern
const props = defineProps<{ modelValue: boolean }>();
const emit = defineEmits(['update:modelValue']);

const budgetStore = useBudgetStore();
const { isLoading, error: storeError } = storeToRefs(budgetStore);

const mappingError = ref<string | null>(null);

watch(() => props.modelValue, (newValue) => {
  if (newValue) {
      budgetStore.error = null;
      mappingError.value = null;
  }
});

function closeModal() {
  if (!isLoading.value) {
     emit('update:modelValue', false);
     budgetStore.error = null;
     mappingError.value = null;
  }
}

async function handleActualFormSubmit(formData: BudgetFormInput) {
  mappingError.value = null;
  budgetStore.error = null;

  const payload = mapBudgetFormToRequestPayload(formData);

  if (!payload) {
      mappingError.value = "Internal error: Could not prepare data for submission.";
      return;
  }

  await budgetStore.createBudget(payload);

  emit('update:modelValue', false);
}

function handleCancel() {
  closeModal();
}

</script>

<template>
  <Dialog :open="props.modelValue" @update:open="closeModal">
    <DialogContent class="sm:max-w-[600px] max-h-[90vh] overflow-scroll">
      <DialogHeader>
        <DialogTitle>Create New Budget</DialogTitle>
        <DialogDescription>
          Fill in the details below to create a new budget plan.
        </DialogDescription>
      </DialogHeader>

      <Alert v-if="mappingError || storeError" variant="destructive" class="mt-4">
          <AlertTitle>Error</AlertTitle>
          <AlertDescription>
              {{ mappingError || storeError }}
          </AlertDescription>
      </Alert>

      <CreateBudgetForm @submit="handleActualFormSubmit" @cancel="handleCancel" />

    </DialogContent>
  </Dialog>
</template>
