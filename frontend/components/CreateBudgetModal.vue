<script setup lang="ts">
import { ref } from 'vue';
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

const props = defineProps<{ modelValue: boolean }>();
const emit = defineEmits<{
  (e: 'close-modal'): void;
}>();

const budgetStore = useBudgetStore();
const { isLoading, error: storeError } = storeToRefs(budgetStore);

const mappingError = ref<string | null>(null);


function closeModal() {
  if (!isLoading.value) {
     emit('close-modal');
     budgetStore.error = null;
     mappingError.value = null;
  }
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

      <CreateBudgetForm  @cancel="handleCancel" @budget-created="closeModal" />

    </DialogContent>
  </Dialog>
</template>
