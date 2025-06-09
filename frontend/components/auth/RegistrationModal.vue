

<script setup lang="ts">
import { watch } from 'vue';
import { useRegistrationForm, type RegistrationFormValues } from '@/composables/useRegistrationForm';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger, // If we want to control it from outside via a prop + trigger
  DialogClose,   // For an explicit close button inside
} from '@/components/ui/dialog';
import { Loader2 } from 'lucide-vue-next';

// Props
const props = defineProps<{
  isOpen: boolean;
  // isLoading: boolean; // isSubmitting from composable will be used
}>();

// Emits
const emit = defineEmits<{ 
  (e: 'update:isOpen', value: boolean): void; // For v-model:isOpen type binding
  (e: 'close'): void;
  (e: 'submit', values: RegistrationFormValues): void;
}>();

// Use the composable
const {
  isSubmitting,
  handleFormSubmit,
  resetForm,
  // validationErrors, // Handled by FormMessage
  // error, // API error - should be handled by the parent view/store
} = useRegistrationForm();

// Handler for successful form validation
const onValidSubmit = (values: RegistrationFormValues) => {
  // Emit the validated values to the parent component
  // The parent (LoginRegistrationView) will then call authStore.register
  emit('submit', values);
  // Modal closing will be handled by parent upon successful registration or explicitly
};

// Define the event handler for the form's submit event
const handleRegistrationFormSubmitEvent = async (event?: Event) => {
  const validatedValues = await handleFormSubmit(event);
  if (validatedValues) {
    onValidSubmit(validatedValues);
  }
};

const handleCloseModal = () => {
  emit('update:isOpen', false);
  emit('close'); // Also emit 'close' for explicit handling if needed
  resetForm(); // Reset form on close
};

// Watch for isOpen prop to reset form when modal becomes visible
// This is particularly useful if the modal can be re-opened with previous (now stale) data
watch(() => props.isOpen, (newValue) => {
  if (newValue) {
    resetForm(); // Clear form fields and validation state
  }
});

</script> 

<template>
  <Dialog :open="props.isOpen" @update:open="(val) => emit('update:isOpen', val)">

    <DialogContent class="sm:max-w-[425px]" @escape-key-down="handleCloseModal" @interact-outside="handleCloseModal">
      <DialogHeader>
        <DialogTitle>Rejestracja</DialogTitle>
        <DialogDescription>
          Wypełnij poniższe pola, aby utworzyć nowe konto.
        </DialogDescription>
      </DialogHeader>
      
      <form class="space-y-4" @submit.prevent="handleRegistrationFormSubmitEvent">
        <!-- Email Field -->
        <FormField v-slot="{ componentField }" name="email">
          <FormItem>
            <FormLabel>Email</FormLabel>
            <FormControl>
              <Input type="email" placeholder="twoj.email@example.com" v-bind="componentField" :disabled="isSubmitting" />
            </FormControl>
            <FormMessage />
          </FormItem>
        </FormField>

        <!-- Password Field -->
        <FormField v-slot="{ componentField }" name="password">
          <FormItem>
            <FormLabel>Hasło</FormLabel>
            <FormControl>
              <Input type="password" placeholder="Min. 8 znaków" v-bind="componentField" :disabled="isSubmitting" />
            </FormControl>
            <FormMessage />
          </FormItem>
        </FormField>

        <!-- Confirm Password Field -->
        <FormField v-slot="{ componentField }" name="passwordConfirm">
          <FormItem>
            <FormLabel>Potwierdź hasło</FormLabel>
            <FormControl>
              <Input type="password" placeholder="Powtórz hasło" v-bind="componentField" :disabled="isSubmitting" />
            </FormControl>
            <FormMessage />
          </FormItem>
        </FormField>

        <DialogFooter class="pt-4">
           <Button type="button" variant="outline" :disabled="isSubmitting" @click="handleCloseModal">
            Anuluj
          </Button>
          <Button type="submit" :disabled="isSubmitting">
            <Loader2 v-if="isSubmitting" class="mr-2 h-4 w-4 animate-spin" />
            <span v-else>Zarejestruj się</span>
          </Button>
        </DialogFooter>
      </form>
    </DialogContent>
  </Dialog>
</template>