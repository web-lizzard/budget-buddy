import { ref } from 'vue';
import { useForm } from 'vee-validate';
import { toTypedSchema } from '@vee-validate/zod';
import * as z from 'zod';

// Define Zod schema object for registration form
const registrationSchemaObject = z.object({
  email: z.string().min(1, { message: 'Email is required' }).email({ message: 'Must be a valid email address' }),
  password: z.string().min(8, { message: 'Password must be at least 8 characters' }),
  passwordConfirm: z.string().min(1, { message: 'Password confirmation is required' }),
}).refine(data => data.password === data.passwordConfirm, {
  message: 'Passwords do not match',
  path: ['passwordConfirm'], // Path to field to display the error
});

// Type for the form values, inferred directly from the Zod object schema
export type RegistrationFormValues = z.infer<typeof registrationSchemaObject>;

// Convert the Zod schema object to a vee-validate compatible schema
const registrationValidationSchema = toTypedSchema(registrationSchemaObject);

export function useRegistrationForm() {
  const error = ref<string | null>(null); // For API errors from the store/parent

  // Setup vee-validate form handling
  const { handleSubmit, errors: validationErrors, isSubmitting, resetForm, setValues, setErrors } = useForm<RegistrationFormValues>({
    validationSchema: registrationValidationSchema,
    initialValues: {
      email: '',
      password: '',
      passwordConfirm: '',
    },
  });

  // Wrapper for handleSubmit
  // This function will be called by the component when the form is submitted.
  // It handles the validation and calls the onSuccess callback (provided by the component).
  const handleFormSubmit = handleSubmit(async (values) => {
    error.value = null; // Clear previous API errors (if handled here)
    console.log('Validated Registration Form Values:', values);
    // The actual registration logic (API call) will be triggered by the component
    // emitting an event with the validated 'values'.
    // This composable focuses on form state and validation.
    return values; // Return validated values for the component to emit
  });

  return {
    validationErrors,
    isSubmitting,
    error, // API error state (can be set from parent if needed)
    handleFormSubmit, // The function the component will call on submit
    resetForm,
    setValues,
    setErrors, // Useful for setting API-related errors on fields from parent
  };
} 