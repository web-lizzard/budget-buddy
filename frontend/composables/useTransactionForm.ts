import { computed } from 'vue';
import { useForm } from 'vee-validate';
import { toTypedSchema } from '@vee-validate/zod';

import {
    createTransactionFormSchema,
    type TransactionFormInput,
    type InitialTransactionFormData
} from '@/schemas/transactionFormSchema';
import { dateToCalendarDate } from '~/utils/dateHelpers';



export function useTransactionForm(budgetStartDate: Date, budgetEndDate: Date, initialValuesProp?: InitialTransactionFormData) {

  // Create the schema instance with the provided dates
  const transactionFormSchema = createTransactionFormSchema(budgetStartDate, budgetEndDate);
  const formSchema = toTypedSchema(transactionFormSchema);

  const initialFormValues = computed<Partial<TransactionFormInput>>(() => ({
      categoryId: initialValuesProp?.categoryId ?? null, // Keep null here, schema handles it
      amount: initialValuesProp?.amount ?? null,      // Keep null here, schema handles it
      type: initialValuesProp?.type ?? 'EXPENSE',
      occurredDate: initialValuesProp?.occurredDate ? dateToCalendarDate(initialValuesProp.occurredDate) : null,
      description: initialValuesProp?.description ?? undefined,
  }));

  const { handleSubmit, resetForm, errors, isSubmitting, meta } = useForm<TransactionFormInput>({
      validationSchema: formSchema,
      initialValues: initialFormValues.value, // Pass the computed value once
      keepValuesOnUnmount: false,
  });

  return {
      errors,
      isSubmitting,
      isValid: computed(() => meta.value.valid),
      handleSubmit: handleSubmit,
      resetForm,
  };
}
