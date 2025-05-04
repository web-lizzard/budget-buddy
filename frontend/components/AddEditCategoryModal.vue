<script setup lang="ts">
import { computed, ref, watch } from 'vue';

// Components
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
import type { CategoryFormData, InitialCategoryFormData } from '@/components/CategoryForm.vue';

// Services & Utils
import { BudgetService } from '@/services/BudgetService';
import { useCommand } from '@/composables/useCommand';
import { toast } from 'vue-sonner';

// Types
import type { Budget } from '@/types/budget';
import type { Category } from '@/types/category';

export interface CategoryData {
  id: string;
  name: string;
  limit: number;
}

// Props
const props = defineProps<{
  isOpen: boolean;
  mode: 'create' | 'edit';
  budget: Budget;
  categoryData?: Category | null;
}>();

const emit = defineEmits<{
  close: [];
  categorySaved: [];
  'update:isOpen': [boolean];
}>();

// Local state for managing form data
const localCategoryData = ref<CategoryData | null>(null);

// Watch for changes in props.categoryData and mode to update local state
watch(
  [() => props.categoryData, () => props.mode, () => props.isOpen],
  ([newCategoryData, newMode, isOpen]) => {
    if (isOpen) {
      if (newMode === 'edit' && newCategoryData) {
        // Map Category to CategoryData format
        localCategoryData.value = {
          id: newCategoryData.id,
          name: newCategoryData.name,
          limit: newCategoryData.limit.amount,
        };
      } else {
        // Reset for create mode
        localCategoryData.value = null;
      }
    }
  },
  { immediate: true }
);

// Services
const budgetService = new BudgetService();

// Computed properties
const initialFormData = computed<InitialCategoryFormData>(() => {
  if (props.mode === 'edit' && localCategoryData.value) {
    return {
      name: localCategoryData.value.name,
      limit: localCategoryData.value.limit,
    };
  }
  // For create mode, always return empty values
  return {
    name: '',
    limit: 0,
  };
});

const existingCategoryNames = computed<string[]>(() => {
  // For create mode: all category names
  // For edit mode: all category names except the current one being edited
  return props.budget.categories
    .filter(cat => props.mode !== 'edit' || cat.id !== props.categoryData?.id)
    .map(cat => cat.name);
});

const remainingBudgetLimit = computed<number>(() => {
  const totalBudgetLimit = props.budget.totalLimit.amount;
  const sumOfOtherCategoryLimits = props.budget.categories
    .filter(cat => props.mode !== 'edit' || cat.id !== props.categoryData?.id)
    .reduce((sum, cat) => sum + cat.limit.amount, 0);

  return totalBudgetLimit - sumOfOtherCategoryLimits;
});

const computedCanAddCategory = computed<boolean>(() => {
  return props.budget.categories.length < 5;
});

// Reset error on modal open/close
const clearErrorOnModalToggle = () => {
  if (error.value) {
    error.value = null;
  }
};

watch(() => props.isOpen, clearErrorOnModalToggle);

// State management
const { execute, loading, error } = useCommand<{
  budgetId: string;
  categoryId?: string;
  data: CategoryFormData;
}>(async (payload) => {
  if (props.mode === 'create') {
    await budgetService.createCategory(payload.budgetId, {
      name: payload.data.name,
      limit: {
        amount: payload.data.limit
      }
    });
  } else if (props.mode === 'edit' && payload.categoryId) {
    await budgetService.updateCategory(payload.budgetId, payload.categoryId, {
      name: payload.data.name,
      limit: {
        amount: payload.data.limit
      }
    });
  }
}, {
  onSuccess: () => {
    toast({
      title: props.mode === 'create' ? 'Category created' : 'Category updated',
      description: `Category has been successfully ${props.mode === 'create' ? 'created' : 'updated'}.`,
    });
    emit('categorySaved');
    emit('update:isOpen', false);
  }
});

// Event handlers
const handleFormSubmit = (formData: CategoryFormData) => {
  // For create mode, check if we can add more categories
  if (props.mode === 'create' && !computedCanAddCategory.value) {
    toast({
      title: 'Cannot add category',
      description: 'You have reached the maximum limit of 5 categories for this budget.',
      variant: 'destructive',
    });
    return;
  }

  execute({
    budgetId: props.budget.id,
    categoryId: props.mode === 'edit' ? props.categoryData?.id : undefined,
    data: formData
  });
};

const handleClose = () => {
  // Clear local data
  localCategoryData.value = null;
  emit('close');
  emit('update:isOpen', false);
};

// Handle dialog update:open event
const handleUpdateOpen = (open: boolean) => {
  if (!open) {
    handleClose();
  }
  emit('update:isOpen', open);
};
</script>

<template>
  <Dialog :open="isOpen" @update:open="handleUpdateOpen">
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
        <!-- Display maximum categories warning -->
        <Alert v-if="mode === 'create' && !computedCanAddCategory" variant="default" class="mb-4">
          <AlertCircle class="h-4 w-4" />
          <AlertDescription>
            You've reached the maximum limit of 5 categories for this budget.
          </AlertDescription>
        </Alert>

        <!-- Display API errors -->
        <Alert v-if="error" variant="destructive" class="mb-4">
          <AlertCircle class="h-4 w-4" />
          <AlertDescription>
            {{ error.message }}
          </AlertDescription>
        </Alert>

        <!-- Category Form -->
        <CategoryForm
          :key="`${mode}-${props.categoryData?.id || 'new'}-${isOpen}`"
          :initial-data="initialFormData"
          :budget-currency="budget.currency"
          :existing-category-names="existingCategoryNames"
          :remaining-budget-limit="remainingBudgetLimit"
          :is-submitting="loading"
          @submit="handleFormSubmit"
        />
      </div>

      <DialogFooter>
        <DialogClose asChild>
          <Button type="button" variant="outline" @click="handleClose" :disabled="loading">
            Cancel
          </Button>
        </DialogClose>
      </DialogFooter>
    </DialogContent>
  </Dialog>
</template> 