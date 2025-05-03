<script setup lang="ts">
import { format } from 'date-fns';

import { cn } from '@/lib/utils';
import { Calendar as CalendarIcon } from 'lucide-vue-next';

import { useTransactionForm } from '@/composables/useTransactionForm';
import type { Category } from '@/types/category';
import type { Budget } from '@/types/budget';
import type { Transaction, TransactionType } from '@/types/transaction';
import type { TransactionFormInput, InitialTransactionFormData } from '@/schemas/transactionFormSchema';

import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Calendar } from '@/components/ui/calendar';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import { dateToCalendarDate } from '~/utils/dateHelpers';

interface BudgetDates {
  startDate: Date;
  endDate: Date;
}

const props = withDefaults(defineProps<{
  initialData: InitialTransactionFormData;
  budget: Pick<Budget, 'currency'> & BudgetDates;
  availableCategories: Pick<Category, 'id' | 'name'>[];
  isLoading?: boolean;
}>(), {
  initialData: () => ({ type: 'EXPENSE' as TransactionType }),
  isLoading: false,
});

export type TransactionSubmitPayload = Omit<Transaction, 'id' | 'userId' | 'amount' | 'date'> & {
  amount: number | null,
  occurredDate: Date | null
};

const emit = defineEmits<{
  (e: 'submit', values: TransactionSubmitPayload): void;
}>();

const {
    handleSubmit,
    isSubmitting,
} = useTransactionForm(props.budget.startDate, props.budget.endDate, props.initialData);

const budgetStartDateValue = computed(() => dateToCalendarDate(props.budget.startDate));
const budgetEndDateValue = computed(() => dateToCalendarDate(props.budget.endDate));

const handleFormSubmitEvent = async () => {
  const onValidationSuccess = (validatedValues: TransactionFormInput) => {
    const valuesToEmit: TransactionSubmitPayload = {
        categoryId: validatedValues.categoryId ?? '',
        type: validatedValues.type,
        amount: validatedValues.amount,
        occurredDate: validatedValues.occurredDate ? new Date(validatedValues.occurredDate.toString()) : null,
        description: validatedValues.description,
    };
    emit('submit', valuesToEmit);
  };

  const onValidationError = (/* { values, errors } */) => {
    console.error('Form validation failed');
  };

  try {
    await handleSubmit(onValidationSuccess, onValidationError)();
  } catch (error) {
    console.error('Caught validation error during handleSubmit:', error);
  }
};

</script>

<template>
  <form class="space-y-4" @submit.prevent="handleFormSubmitEvent">
    <!-- Category -->
    <FormField v-slot="{ componentField }" name="categoryId">
        <FormItem>
            <FormLabel>Category</FormLabel>
             <Select v-bind="componentField">
                 <FormControl>
                     <SelectTrigger>
                       <SelectValue placeholder="Select a category" />
                     </SelectTrigger>
                 </FormControl>
                 <SelectContent>
                   <SelectItem
                        v-for="category in availableCategories"
                        :key="category.id"
                        :value="category.id"
                    >
                      {{ category.name }}
                   </SelectItem>
                 </SelectContent>
             </Select>
            <FormMessage />
        </FormItem>
    </FormField>

    <!-- Amount -->
    <FormField v-slot="{ field }" name="amount">
      <FormItem>
        <FormLabel>Amount</FormLabel>
        <div class="flex items-center gap-2">
             <FormControl>
                 <Input
                     type="number"
                     placeholder="e.g., 50.00"
                     :model-value="field.value"
                     step="0.01"
                     @update:model-value="(val) => field.onChange(val === '' || val === null ? null : Number(val))"
                 />
             </FormControl>
             <span class="text-muted-foreground">{{ budget.currency }}</span>
        </div>
        <FormMessage />
      </FormItem>
    </FormField>

    <!-- Type -->
    <FormField v-slot="{ componentField }" name="type">
      <FormItem class="space-y-3">
        <FormLabel>Type</FormLabel>
        <FormControl>
          <RadioGroup
            class="flex space-x-4"
            v-bind="componentField"
          >
            <FormItem class="flex items-center space-x-2">
              <FormControl>
                <RadioGroupItem value="EXPENSE" />
              </FormControl>
              <FormLabel class="font-normal">
                Expense
              </FormLabel>
            </FormItem>
            <FormItem class="flex items-center space-x-2">
              <FormControl>
                <RadioGroupItem value="INCOME" />
              </FormControl>
              <FormLabel class="font-normal">
                Income
              </FormLabel>
            </FormItem>
          </RadioGroup>
        </FormControl>
        <FormMessage />
      </FormItem>
    </FormField>

    <!-- Occurred Date -->
    <FormField v-slot="{ field }" name="occurredDate">
        <FormItem class="flex flex-col">
            <FormLabel>Date</FormLabel>
             <Popover>
                <PopoverTrigger as-child>
                  <FormControl>
                    <Button
                      variant="outline"
                      :class="cn(
                        'w-full pl-3 text-left font-normal',
                        !field.value && 'text-muted-foreground',
                      )"
                    >
                      <span>{{ field.value ? format(dateValueToDate(field.value)!, "PPP") : "Pick a date" }}</span>
                      <CalendarIcon class="ml-auto h-4 w-4 opacity-50" />
                    </Button>
                  </FormControl>
                </PopoverTrigger>
                <PopoverContent class="w-auto p-0">
                  <Calendar
                     :model-value="field.value"
                     :min-value="budgetStartDateValue"
                     :max-value="budgetEndDateValue"
                     @update:model-value="field.onChange"
                  />
                </PopoverContent>
              </Popover>
            <FormMessage />
        </FormItem>
    </FormField>

    <!-- Description -->
    <FormField v-slot="{ componentField }" name="description">
       <FormItem>
         <FormLabel>Description <span class="text-muted-foreground">(Optional)</span></FormLabel>
         <FormControl>
           <Input type="text" placeholder="e.g., Weekly groceries" v-bind="componentField" />
         </FormControl>
         <FormMessage />
       </FormItem>
     </FormField>

    <!-- Submit Button -->
    <div class="flex justify-end pt-6 border-t">
      <Button type="submit" :disabled="isLoading || isSubmitting">
        {{ (isLoading || isSubmitting) ? 'Saving...' : 'Save Transaction' }}
      </Button>
    </div>
  </form>
</template>
