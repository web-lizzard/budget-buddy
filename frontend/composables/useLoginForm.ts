import { ref } from 'vue';
import { useForm } from 'vee-validate';
import { toTypedSchema } from '@vee-validate/zod';
import * as z from 'zod';

// Define Zod schema object first
const loginSchemaObject = z.object({
  email: z.string().min(1, { message: 'Email is required' }).email({ message: 'Must be a valid email address' }),
  password: z.string().min(1, { message: 'Password is required' }),
  // Example: Add minimum password length if needed
  // password: z.string().min(8, { message: 'Password must be at least 8 characters' }),
});

// Type for the form values, inferred directly from the Zod object schema
export type LoginFormValues = z.infer<typeof loginSchemaObject>;

// Convert the Zod schema object to a vee-validate compatible schema
const loginValidationSchema = toTypedSchema(loginSchemaObject);

export function useLoginForm() {
  const error = ref<string | null>(null); // For API errors

  // Setup vee-validate form handling
  const { handleSubmit, errors: validationErrors, isSubmitting, resetForm, setValues, setErrors } = useForm<LoginFormValues>({
    validationSchema: loginValidationSchema, // Use the converted schema
    initialValues: {
      email: '',
      password: '',
    },
  });

  // Wrapper for handleSubmit
  const handleFormSubmit = handleSubmit(async (values) => {
    error.value = null; // Clear previous API errors
    console.log('Validated Login Form Values:', values);
    // The actual login logic (API call) will be triggered by the component
    return values; // Return validated values for the component to emit
  });

  return {
    validationErrors,
    isSubmitting,
    error, // API error state
    handleFormSubmit,
    resetForm,
    setValues,
    setErrors,
  };
} 