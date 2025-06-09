/**
 * Client-side plugin to initialize authentication on app startup
 */
export default defineNuxtPlugin(async () => {
  const authStore = useAuthStore();

  // Only run on client side and when not already initialized
  if (import.meta.client && !authStore.isAuthenticated) {
    try {
      await authStore.initializeAuth();
    } catch (error) {
      console.error('Failed to initialize authentication:', error);
    }
  }

  // Add debug functions to window for development
  if (import.meta.client && import.meta.dev) {
    const { testAuthHeaders } = await import('@/utils/apiUtils');

    // Make auth testing functions available globally for debugging
    (window as typeof window & { testAuthHeaders: typeof testAuthHeaders; authStore: typeof authStore }).testAuthHeaders = testAuthHeaders;
    (window as typeof window & { testAuthHeaders: typeof testAuthHeaders; authStore: typeof authStore }).authStore = authStore;

    console.log('🔧 Auth debug functions available:');
    console.log('- window.testAuthHeaders() - Test auth headers and tokens');
    console.log('- window.authStore - Access to auth store');
  }
});
