/**
 * Authentication middleware to protect routes
 */
export default defineNuxtRouteMiddleware((to) => {
  const authStore = useAuthStore();

  // If user is not authenticated and trying to access protected route
  if (!authStore.isAuthenticated && to.path !== '/auth/login' && !to.path.startsWith('/auth/')) {
    return navigateTo('/auth/login');
  }

  // If user is authenticated and trying to access auth pages, redirect to home
  if (authStore.isAuthenticated && to.path.startsWith('/auth/')) {
    return navigateTo('/');
  }
});
