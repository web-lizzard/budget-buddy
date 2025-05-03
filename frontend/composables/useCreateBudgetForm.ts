import { computed } from 'vue';
import { useFieldArray, useForm } from 'vee-validate';
import { toTypedSchema } from '@vee-validate/zod';
import type { DateValue } from '@internationalized/date';

import { useBudgetStore } from '@/stores/budgetStore';
import { budgetFormSchema, type BudgetFormInput } from '@/schemas/createBudgetSchemas';
import type { CreateBudgetRequestPayload, CreateCategoryRequestPayload, StrategyPayload } from '@/types/dtos';

// Supported currencies (consider moving to a config file)
const CURRENCIES = ['PLN', 'EUR', 'USD', 'GBP']

export function useCreateBudgetForm() {
    const budgetStore = useBudgetStore();

    const form = useForm<BudgetFormInput>({
        validationSchema: toTypedSchema(budgetFormSchema),
        initialValues: {
            name: '',
            totalLimit: undefined,
            currency: 'PLN',
            startDate: undefined,
            strategyType: 'monthly',
            categories: [],
        },
    });

    const { fields: categoryFields, push: addCategory, remove: removeCategory } = useFieldArray<{
        name: string;
        limit: number | undefined;
    }>('categories');

    const handleDateUpdate = (onChange: (value: unknown) => void, dateValue: DateValue | undefined) => {
        if (dateValue) {
            onChange(dateValue);
        }
    };

    const mapFormToPayload = (values: BudgetFormInput): CreateBudgetRequestPayload => {
        const startDate = values.startDate!.toDate('UTC');
        const totalLimitAmount = values.totalLimit!;

        const mappedCategories: CreateCategoryRequestPayload[] = (values.categories ?? []).map(cat => {
            const categoryPayload: Partial<CreateCategoryRequestPayload> & { name: string } = { name: cat.name };
            if (cat.limit !== undefined && cat.limit !== null && cat.limit > 0) {
                categoryPayload.limit = { amount: cat.limit, currency: values.currency };
            }
            return categoryPayload as CreateCategoryRequestPayload;
        });

        const payload: CreateBudgetRequestPayload = {
            name: values.name,
            total_limit: { amount: totalLimitAmount, currency: values.currency },
            start_date: startDate.toISOString(),
            categories: mappedCategories,
            strategy: values.strategyType as unknown as StrategyPayload,
        };

        return payload;
    };

    const handleSubmit = form.handleSubmit(async (values) => {
        console.log('Form validated successfully:', values);
        const payload = mapFormToPayload(values);
        console.log('Mapped payload for API:', payload);

        await budgetStore.createBudget(payload);

        if (!budgetStore.error) {
            console.log('Budget creation initiated successfully via store.');
            form.resetForm();
        }
         else {
             console.error('Budget creation failed via store:', budgetStore.error);
         }
    });

    return {
        errors: form.errors,
        meta: form.meta,
        values: form.values,
        categoryFields,
        addCategory,
        removeCategory,
        handleSubmit,
        resetForm: form.resetForm,
        handleDateUpdate,
        CURRENCIES,
        isCreating: computed(() => budgetStore.isCreating),
        error: computed(() => budgetStore.error),
        setFieldValue: form.setFieldValue,
        handleReset: form.handleReset,
    };
}
