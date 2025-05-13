
<script setup lang="ts">
import { useLoginForm, type LoginFormValues } from '@/composables/useLoginForm';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import { Loader2 } from 'lucide-vue-next';

// Define emits
const emit = defineEmits<{ (e: 'submit', values: LoginFormValues): void }>();

// Use the composable
const {
  // validationErrors, // Can be accessed via FormMessage
  isSubmitting,
  handleFormSubmit, // This is the function that takes the success callback
  // error, // API error - handled by the parent view
} = useLoginForm();

// Define the function to run on successful validation
const onValidSubmit = (values: LoginFormValues) => {
  // Emit the validated values to the parent component
  emit('submit', values);
};

// Define the event handler for the form's submit event, following the pattern
// from CreateBudgetForm.vue. This handler will call the submit logic from the composable.
const handleFormSubmitEvent = async (event?: Event) => {
  const values = await handleFormSubmit(event);
  if (values) {
    onValidSubmit(values);
  }
};
</script> 

<template>
  <form class="space-y-4" @submit.prevent="handleFormSubmitEvent">
    <!-- Email Field -->
    <FormField v-slot="{ componentField }" name="email">
      <FormItem>
        <FormLabel>Email</FormLabel>
        <FormControl>
          <Input type="email" placeholder="your.email@example.com" v-bind="componentField" :disabled="isSubmitting" />
        </FormControl>
        <FormMessage />
      </FormItem>
    </FormField>

    <!-- Password Field -->
    <FormField v-slot="{ componentField }" name="password">
      <FormItem>
        <FormLabel>Password</FormLabel>
        <FormControl>
          <Input type="password" placeholder="********" v-bind="componentField" :disabled="isSubmitting" />
        </FormControl>
        <FormMessage />
      </FormItem>
    </FormField>

    <!-- Submit Button -->
    <Button type="submit" :disabled="isSubmitting" class="w-full">
      <Loader2 v-if="isSubmitting" class="mr-2 h-4 w-4 animate-spin" />
      <span v-else>Login</span>
    </Button>

    <!-- Display validation errors (optional, usually handled by FormMessage) -->
    <!-- <pre v-if="Object.keys(validationErrors).length > 0">{{ validationErrors }}</pre> -->
  </form>
</template>
