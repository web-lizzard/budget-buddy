<script setup lang="ts">
import { format } from 'date-fns';
import { cn } from '@/lib/utils';

// Import the composable and types
import { useCreateBudgetForm } from '@/composables/useCreateBudgetForm';
import type { BudgetFormInput } from '@/schemas/createBudgetSchemas';

import { CalendarDate, today, getLocalTimeZone } from '@internationalized/date';

// Import UI components
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Calendar } from '@/components/ui/calendar';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import { Calendar as CalendarIcon } from 'lucide-vue-next';

// Define emits for the component
const emit = defineEmits(['submit', 'cancel']);

// Use the composable to get form state and methods
const {
    errors,
    categoryFields,
    addCategory,
    removeCategory,
    handleSubmit, // Get the raw handleSubmit
    resetForm,
    handleDateUpdate,
    CURRENCIES,
} = useCreateBudgetForm();

// --- Component-specific Event Handlers ---

// Define the success callback for handleSubmit
const onValidationSuccess = (validatedValues: BudgetFormInput) => {
  emit('submit', validatedValues);
  // context.resetForm(); // Optionally reset form on success
};

// Define the handler for the form's submit event
const handleFormSubmitEvent = async (event?: Event) => {

    const submitHandler = handleSubmit(onValidationSuccess);
    submitHandler(event);
};

function handleFormCancel() {
  resetForm();
  emit('cancel');
}
// --------------------------------------

</script>

<template>
  <!-- Bind the form's submit event to the wrapper handler -->
  <form :id="'budget-form-id'" class="space-y-6" @submit.prevent="handleFormSubmitEvent">
    <!-- Add .prevent modifier -->
    <!-- Use FormField provided by shadcn/ui which integrates with vee-validate -->
    <FormField v-slot="{ componentField }" name="name">
       <FormItem>
         <FormLabel>Budget Name</FormLabel>
         <FormControl>
           <Input type="text" placeholder="e.g., Monthly Groceries" v-bind="componentField" />
         </FormControl>
         <FormDescription>
            Must be between 3 and 100 characters.
         </FormDescription>
         <FormMessage />
       </FormItem>
     </FormField>

    <!-- Total Limit -->
    <FormField v-slot="{ componentField }" name="totalLimit">
      <FormItem>
        <FormLabel>Total Limit</FormLabel>
        <FormControl>
          <Input type="number" placeholder="e.g., 1000" v-bind="componentField" />
        </FormControl>
        <FormDescription>
          The overall spending limit for this budget.
        </FormDescription>
         <!-- Display totalLimit specific error from superRefine -->
         <FormMessage />
         <p v-if="errors.totalLimit && typeof errors.totalLimit === 'string'" class="text-sm font-medium text-destructive">
             {{ errors.totalLimit }}
         </p>
      </FormItem>
    </FormField>

    <!-- Currency -->
    <FormField v-slot="{ componentField }" name="currency">
        <FormItem>
            <FormLabel>Currency</FormLabel>
             <Select v-bind="componentField">
                 <FormControl>
                     <SelectTrigger>
                       <SelectValue placeholder="Select a currency" />
                     </SelectTrigger>
                 </FormControl>
                 <SelectContent>
                   <SelectItem v-for="curr in CURRENCIES" :key="curr" :value="curr">
                      {{ curr }}
                   </SelectItem>
                 </SelectContent>
             </Select>
            <FormDescription>
                The currency for amounts in this budget.
            </FormDescription>
            <FormMessage />
        </FormItem>
    </FormField>

    <!-- Start Date -->
     <FormField v-slot="{ field }" name="startDate">
        <FormItem class="flex flex-col">
            <FormLabel>Start Date</FormLabel>
             <Popover>
                <PopoverTrigger as-child>
                  <FormControl>
                    <Button
                      variant="outline"
                      :class="cn(
                        'w-full pl-3 text-left font-normal',
                        !field.value && 'text-muted-foreground'
                      )"
                    >
                      <span v-if="field.value instanceof CalendarDate">{{ format(field.value.toDate(getLocalTimeZone()), "PPP") }}</span>
                      <span v-else>Pick a date</span>
                      <CalendarIcon class="ml-auto h-4 w-4 opacity-50" />
                    </Button>
                  </FormControl>
                </PopoverTrigger>
                <PopoverContent class="w-auto p-0" align="start">
                  <Calendar
                    :model-value="field.value"
                    :min-value="today(getLocalTimeZone())"
                    @update:model-value="(dateVal) => handleDateUpdate(field.onChange, dateVal)"
                  />
                </PopoverContent>
              </Popover>
             <FormDescription>
                When the budget tracking period begins.
            </FormDescription>
            <FormMessage />
        </FormItem>
    </FormField>

     <!-- Strategy Type -->
     <FormField v-slot="{ componentField }" name="strategyType">
        <FormItem>
            <FormLabel>Budget Strategy</FormLabel>
             <Select v-bind="componentField">
                 <FormControl>
                     <SelectTrigger>
                       <SelectValue placeholder="Select a strategy" />
                     </SelectTrigger>
                 </FormControl>
                 <SelectContent>
                     <SelectItem value="monthly">Monthly</SelectItem>
                     <SelectItem value="yearly">Yearly</SelectItem>
                 </SelectContent>
             </Select>
            <FormDescription>
                Determines the budget's duration and recurrence.
            </FormDescription>
            <FormMessage />
        </FormItem>
    </FormField>

    <!-- Dynamic Categories Section -->
    <div class="space-y-4 border-t pt-6">
        <div class="flex justify-between items-center">
             <div>
                 <h3 class="text-lg font-medium">Categories</h3>
                 <p class="text-sm text-muted-foreground">
                     Optionally, define specific spending categories and their limits (max 5).
                 </p>
             </div>
              <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  :disabled="categoryFields.length >= 5"
                  @click="addCategory"
              >
                  Add Category
             </Button>
         </div>

         <!-- Display general array error -->
         <FormMessage v-if="errors.categories && typeof errors.categories === 'string'" class="text-red-600">
             {{ errors.categories }}
         </FormMessage>

         <!-- Loop through category fields -->
         <div v-for="(categoryField, index) in categoryFields" :key="categoryField.key" class="flex items-end space-x-2 border p-3 rounded-md relative">
              <!-- Category Name -->
              <FormField v-slot="{ componentField }" :name="`categories[${index}].name`" class="flex-grow">
                 <FormItem>
                     <FormLabel :class="{ 'sr-only': index > 0 }">Category Name</FormLabel>
                     <FormControl>
                         <Input type="text" placeholder="e.g., Food" v-bind="componentField" />
                     </FormControl>
                     <FormMessage /> <!-- Field specific errors -->
                 </FormItem>
             </FormField>

             <!-- Category Limit -->
             <FormField v-slot="{ componentField }" :name="`categories[${index}].limit`">
                 <FormItem>
                     <FormLabel :class="{ 'sr-only': index > 0 }">Limit</FormLabel>
                     <FormControl>
                         <Input type="number" placeholder="e.g., 200" v-bind="componentField" step="0.01"/>
                     </FormControl>
                     <FormMessage /> <!-- Field specific errors -->
                 </FormItem>
             </FormField>

             <!-- Remove Button -->
             <Button
                 type="button"
                 variant="ghost"
                 size="icon"
                 class="text-muted-foreground hover:text-destructive"
                 @click="removeCategory(index)"
             >
                 <span class="sr-only">Remove category</span>
                 <!-- SVG Icon (ensure it's correctly formatted) -->
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-5 h-5">
                    <path fill-rule="evenodd" d="M8.75 1A2.75 2.75 0 0 0 6 3.75v.443c-.795.077-1.58.22-2.326.432C2.913 4.845 2.25 5.46 2.25 6.25v1.75c0 .79.663 1.405 1.424 1.624a4.03 4.03 0 0 1-1.359 2.248 1.75 1.75 0 0 0-.515 2.385c.41 1.004 1.63 1.74 3.196 1.74h7a3.25 3.25 0 0 0 3.25-3.25V9.874c.826-.316 1.5-1.014 1.5-1.874V6.25c0-.79-.663-1.405-1.424-1.624A4.035 4.035 0 0 1 14 4.193V3.75A2.75 2.75 0 0 0 11.25 1h-2.5ZM7.5 3.75c0-.69.56-1.25 1.25-1.25h2.5c.69 0 1.25.56 1.25 1.25v.414A4.017 4.017 0 0 1 13.007 5.5H6.993a4.017 4.017 0 0 1 .507-1.336V3.75Zm-2 9.5c-.093 0-.185-.012-.271-.035A.75.75 0 0 1 4.25 13V8.75a.75.75 0 0 1 1.5 0V13c0 .178.11.334.27.398a4.02 4.02 0 0 1 3.733-.398.75.75 0 1 1 .537 1.387 5.52 5.52 0 0 0-5.04 0A1.75 1.75 0 0 0 5.5 13.25Z" clip-rule="evenodd" />
                </svg>
             </Button>
         </div>

          <!-- Message when no categories are added -->
         <p v-if="categoryFields.length === 0" class="text-sm text-muted-foreground text-center italic py-2">
              No categories added yet.
         </p>
     </div>
     <!-- End of Dynamic Categories Section -->

    <!-- Action Buttons -->
    <div class="flex justify-end space-x-2 pt-6 border-t">
      <!-- Use component's cancel handler -->
      <Button type="button" variant="outline" @click="handleFormCancel">Cancel</Button>
      <!-- Submit button triggers the form's submit event -->
      <Button type="submit">Save Budget</Button>
    </div>
  </form>
</template>
