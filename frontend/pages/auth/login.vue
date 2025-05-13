<template>
  <div class="min-h-screen flex flex-col items-center justify-center bg-gray-100 p-4">
    <div class="w-full max-w-md bg-white shadow-lg rounded-lg p-8">
      <h1 class="text-2xl font-bold text-center mb-6 text-gray-800">Budget Buddy</h1>

      <!-- Global Error Alert from authStore -->
      <div v-if="authStore.error && !isRegistrationModalOpen" class="mb-4 p-3 bg-red-50 border border-red-300 rounded-md text-sm text-red-700">
        <p><span class="font-medium">Błąd logowania:</span> {{ authStore.error }}</p>
      </div>

      <!-- Global Loading Indicator from authStore -->
      <div v-if="authStore.isLoading" class="flex justify-center items-center my-4">
        <Loader2 class="h-8 w-8 text-indigo-600 animate-spin" />
        <p class="ml-2 text-gray-600">Przetwarzanie...</p>
      </div>

      <LoginForm @submit="handleLoginSubmit" />

      <div class="mt-6 text-center">
        <Button variant="link" @click="openRegistrationModal" class="text-indigo-600 hover:text-indigo-500">
          Nie masz konta? Zarejestruj się
        </Button>
      </div>
    </div>

    <!-- Registration Modal -->
    <!-- Errors within the modal will be handled by its own form validation or if authStore.error is specifically for registration -->
    <RegistrationModal 
      v-model:isOpen="isRegistrationModalOpen" 
      @submit="handleRegisterSubmit"
    />
    <!-- We can also pass authStore.isLoading to RegistrationModal if its submit button should be globally controlled -->
    <!-- :is-loading="authStore.isLoading" -->

  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import { useRouter } from 'vue-router';
import LoginForm from '@/components/auth/LoginForm.vue';
import RegistrationModal from '@/components/auth/RegistrationModal.vue';
import { useAuthStore } from '@/stores/auth';
import type { LoginFormValues } from '@/composables/useLoginForm'; // For login payload
import type { RegistrationFormValues } from '@/composables/useRegistrationForm'; // For registration payload
import { Button } from '@/components/ui/button'; // Shadcn button for "Zarejestruj się"
import { Loader2 } from 'lucide-vue-next'; // For global loading indicator

const authStore = useAuthStore();
const router = useRouter();

const isRegistrationModalOpen = ref(false);

const openRegistrationModal = () => {
  authStore.clearError(); // Clear previous errors before opening modal
  isRegistrationModalOpen.value = true;
};

// Login form submission handler
const handleLoginSubmit = async (credentials: LoginFormValues) => {
  await authStore.login(credentials);
  if (authStore.isAuthenticated) {
    // alert('Login successful!'); // Placeholder
    router.push('/'); // Redirect to dashboard or home page after successful login
  }
  // Error display is handled by the template via authStore.error
};

// Registration modal submission handler
const handleRegisterSubmit = async (userData: RegistrationFormValues) => {
  // We only need email and password for UserCreate, Zod schema in composable includes passwordConfirm for validation only
  const { email, password } = userData;
  await authStore.register({ email, password });
  if (!authStore.error) { // Check if registration was successful (no error in store)
    isRegistrationModalOpen.value = false; // Close modal on successful registration
    // Optionally, you can add a success message here, e.g., using a toast notification
    alert('Rejestracja zakończona pomyślnie! Możesz się teraz zalogować.'); // Placeholder
    // User will typically need to log in after registration as per current authStore.register logic
  }
  // If there's an error, it will be displayed inside the modal by its form validation
  // or if we decide to show authStore.error specifically for registration within the modal.
};

// Watch for changes in authentication state to redirect if user logs out on this page
// or if auth state changes due to other reasons (e.g. token expiry handled elsewhere)
watch(() => authStore.isAuthenticated, (newAuthStatus, oldAuthStatus) => {
  if (oldAuthStatus && !newAuthStatus && router.currentRoute.value.path === '/auth/login') {
    // If user was authenticated and now is not, and is still on login page, do nothing specific here
    // unless you want to clear forms or show a message.
  }
});

// Clear any auth errors when the component is unmounted (e.g., user navigates away)
import { onUnmounted } from 'vue';
onUnmounted(() => {
  authStore.clearError();
});

</script>

<style scoped>
/* Scoped styles for LoginRegistrationView if needed */
.min-h-screen {
  min-height: 100vh;
}
</style> 