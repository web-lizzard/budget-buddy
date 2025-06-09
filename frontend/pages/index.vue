<template>
  <div class="min-h-screen bg-gray-50">
    <div class="container mx-auto px-4 py-8">
      <div v-if="authStore.isAuthenticated" class="text-center">
        <h1 class="text-4xl font-bold text-gray-900 mb-4">Welcome to Budget Buddy!</h1>
        <p class="text-xl text-gray-600 mb-8">Manage your finances with ease</p>
        <div class="space-x-4">
          <Button class="bg-indigo-600 hover:bg-indigo-700" @click="navigateTo('/budgets')">
            View Budgets
          </Button>
        </div>
      </div>
      <div v-else class="text-center">
        <h1 class="text-4xl font-bold text-gray-900 mb-4">Welcome to Budget Buddy!</h1>
        <p class="text-xl text-gray-600 mb-8">Please log in to manage your finances</p>
        <Button class="bg-indigo-600 hover:bg-indigo-700" @click="navigateTo('/auth/login')">
          Log In
        </Button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Button } from '@/components/ui/button';

const authStore = useAuthStore();

// Define page meta with middleware
definePageMeta({
  middleware: 'auth' as any
});
</script>
