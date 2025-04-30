import { computed } from 'vue';
import { useForm, useFieldArray } from 'vee-validate';
import { toTypedSchema } from '@vee-validate/zod';
import type {  DateValue } from '@internationalized/date';
import {
    budgetFormSchema,
    type BudgetFormInput,
    type CategoryFormData
} from '@/schemas/createBudgetSchemas';


export function useCreateBudgetForm() {

  const formSchema = toTypedSchema(budgetFormSchema);

  const { handleSubmit, resetForm, errors, isSubmitting, meta } = useForm<BudgetFormInput>({
      validationSchema: formSchema,
      initialValues: {
        name: '',
        totalLimit: null,
        currency: undefined,
        startDate: undefined,
        strategyType: undefined,
        categories: [],
      },
  });

  const { fields, remove, push } = useFieldArray<CategoryFormData>('categories');

  // --- Helper function for Calendar --- (Still needed here for the template handler)
  function handleDateUpdate(fieldSetter: (value: DateValue | undefined) => void, dateValue: DateValue | undefined) {
      fieldSetter(dateValue);
  }

  return {
      errors,
      isSubmitting,
      isValid: computed(() => meta.value.valid),

      // Category Fields Management
      categoryFields: fields,
      addCategory: () => push({ name: '', limit: 0 }),
      removeCategory: remove,

      // Actions
      handleSubmit,
      resetForm,

      handleDateUpdate,
      CURRENCIES: ['PLN', 'USD', 'EUR'] as const, // Keep constants here as they relate to form options
      STRATEGIES: ['monthly', 'yearly'] as const,
  };
}
