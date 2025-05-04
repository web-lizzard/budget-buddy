<script setup lang="ts">
import { ref, computed } from 'vue';

import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
  DialogClose
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { AlertCircle } from 'lucide-vue-next';
import CategoryForm from '@/components/CategoryForm.vue';
import type { CategoryFormData } from '@/components/CategoryForm.vue';


import type { Budget } from '@/types/budget';
import type { Category } from '@/types/category';
import { BudgetService } from '~/services/BudgetService';
import { toast } from 'vue-sonner';

const props = defineProps<{
  budget: Budget;
  isOpen: boolean;
  selectedCategory: Category | null;
}>();

const emit = defineEmits<{
  'close': [];
  'submit': [];
}>();

const closeModal = () => {
  emit('close');
};

const mode = computed(() => props.selectedCategory ? 'edit' : 'create');

const initialFormData = computed(() => {
  if (mode.value === 'edit' && props.selectedCategory) {
    return {
      name: props.selectedCategory.name,
      limit: props.selectedCategory.limit.amount,
    };
  }

  return {
    name: '',
    limit: 0,
  };
});

const getExistingCategoryNames = (): string[] => {
  if (!props.budget) return [];

  return props.budget.categories
    .filter(cat => mode.value !== 'edit' || cat.id !== props.selectedCategory?.id)
    .map(cat => cat.name);
};

const getRemainingBudgetLimit = (): number => {
  if (!props.budget) return 0;

  const totalBudgetLimit = props.budget.totalLimit.amount;
  const sumOfOtherCategoryLimits = props.budget.categories
    .filter(cat => mode.value !== 'edit' || cat.id !== props.selectedCategory?.id)
    .reduce((sum, cat) => sum + cat.limit.amount, 0);

  return totalBudgetLimit - sumOfOtherCategoryLimits;
};

const canAddCategory = (): boolean => {
  return props.budget.categories.length < 5;
};

const budgetService = new BudgetService();

const { execute: submitCategory, loading: isSubmitting, error } = useCommand<CategoryFormData>(async (formData) => {
  if (mode.value === 'create') {
    await budgetService.createCategory(props.budget.id, {
      name: formData.name,
      limit: {
        amount: formData.limit
      }
    });
  }

  if (mode.value === 'edit' && props.selectedCategory) {
    await budgetService.updateCategory(props.budget.id, props.selectedCategory.id, {
      name: formData.name,
      limit: {
        amount: formData.limit
      }
    });
  }
}, {
  onSuccess: () => {
    toast.success('Category updated successfully');
    emit('submit');
  },
  onError: (error) => {
    toast.error(error.message);
  }
});

const handleFormSubmit = (formData: CategoryFormData) => {
  submitCategory(formData);
};

const formKey = computed(() =>
  `${mode.value}-${props.selectedCategory?.id || 'new'}-${props.isOpen}`
);
</script>

<template>
  <Dialog :open="isOpen" @update:open="(open) => !open && closeModal()">
    <DialogContent class="sm:max-w-[425px]">
      <DialogHeader>
        <DialogTitle>{{ mode === 'create' ? 'Add Category' : 'Edit Category' }}</DialogTitle>
        <DialogDescription>
          {{ mode === 'create'
              ? 'Create a new spending category for your budget.'
              : 'Update the details of your spending category.' }}
        </DialogDescription>
      </DialogHeader>

      <div class="py-4">
        <Alert v-if="mode === 'create' && canAddCategory()" variant="default" class="mb-4">
          <AlertCircle class="h-4 w-4" />
          <AlertDescription>
            You've reached the maximum limit of 5 categories for this budget.
          </AlertDescription>
        </Alert>

        <Alert v-if="error" variant="destructive" class="mb-4">
          <AlertCircle class="h-4 w-4" />
          <AlertDescription>
            {{ error.message }}
          </AlertDescription>
        </Alert>

        <CategoryForm
          :key="formKey"
          :initial-data="initialFormData"
          :budget-currency="budget.currency"
          :existing-category-names="getExistingCategoryNames()"
          :remaining-budget-limit="getRemainingBudgetLimit()"
          :is-submitting="isSubmitting"
          :form-key="formKey"
          @submit="handleFormSubmit"
        />
      </div>

      <DialogFooter>
        <DialogClose as-child>
          <Button type="button" variant="outline" :disabled="isSubmitting" @click="closeModal()">
            Cancel
          </Button>
        </DialogClose>
      </DialogFooter>
    </DialogContent>
  </Dialog>
</template>
