<script setup lang="ts">
import { computed } from 'vue';
import { useForm } from 'vee-validate';
import { toTypedSchema } from '@vee-validate/zod';
import * as z from 'zod';

// UI Components
import { FormField, FormItem, FormLabel, FormControl, FormMessage } from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';

export interface InitialCategoryFormData {
  name?: string;
  limit?: number;
}

export interface CategoryFormData {
  name: string;
  limit: number;
}

const props = defineProps<{
  initialData: InitialCategoryFormData;
  budgetCurrency: string;
  existingCategoryNames: string[];
  remainingBudgetLimit: number;
  isSubmitting: boolean;
  formKey: string;
}>();

const emit = defineEmits<{
  'submit': [CategoryFormData];
}>();

// Create dynamic validation schema based on props
const validationSchema = computed(() => {
  return toTypedSchema(z.object({
    name: z.string()
      .min(1, "Category name is required")
      .refine(
        (name) => !props.existingCategoryNames.includes(name),
        "Category with this name already exists"
      ),
    limit: z.number({
        required_error: "Limit is required",
        invalid_type_error: "Limit must be a number"
      })
      .positive("Limit must be positive")
      .refine(
        (limit) => limit <= props.remainingBudgetLimit,
        `Limit cannot exceed remaining budget limit (${props.remainingBudgetLimit})`
      ),
  }));
});

// Initialize the form
const { handleSubmit } = useForm<CategoryFormData>({
  validationSchema,
  initialValues: {
    name: props.initialData.name ?? '',
    limit: props.initialData.limit ?? 0,
  },
});

// Form submission handler
const onSubmit = handleSubmit((values) => {
  emit('submit', {
    name: values.name,
    limit: values.limit
  });
});
</script>

<template>
  <form class="space-y-4" @submit.prevent="onSubmit">
    <!-- Category Name Field -->
    <FormField v-slot="{ field, errorMessage }" name="name">
      <FormItem>
        <FormLabel>Category Name</FormLabel>
        <FormControl>
          <Input
            v-bind="field"
            placeholder="e.g., Groceries"
            :disabled="isSubmitting"
          />
        </FormControl>
        <FormMessage>{{ errorMessage }}</FormMessage>
      </FormItem>
    </FormField>

    <!-- Category Limit Field -->
    <FormField v-slot="{ field, errorMessage }" name="limit">
      <FormItem>
        <FormLabel>Category Limit</FormLabel>
        <div class="flex items-center gap-2">
          <FormControl>
            <Input
              type="number"
              :value="field.value"
              placeholder="e.g., 500"
              step="0.01"
              :disabled="isSubmitting"
              @input="(e: Event) => field.onChange(Number((e.target as HTMLInputElement).value))"
            />
          </FormControl>
          <span class="text-muted-foreground">{{ budgetCurrency }}</span>
        </div>
        <FormMessage>{{ errorMessage }}</FormMessage>
      </FormItem>
    </FormField>

    <!-- Form Actions -->
    <div class="flex justify-end pt-4">
      <Button type="submit" :disabled="isSubmitting">
        <span v-if="isSubmitting">Saving...</span>
        <span v-else>Save</span>
      </Button>
    </div>
  </form>
</template>
