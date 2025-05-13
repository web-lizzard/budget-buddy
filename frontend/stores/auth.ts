import { defineStore } from 'pinia';
import { ref } from 'vue';
import type {
  UserLogin,
  UserCreate,
  TokenResponse,
  UserResponse,
  AuthenticatedUser,
} from '@/types/auth'; // Adjusted path

// Importuj typy z backendu, jeśli są dostępne i potrzebne
// import type { UserResponse, TokenResponse, UserLogin, UserCreate } from '~/types/api';

// Przykładowy prosty typ dla użytkownika - dostosuj wg potrzeb

// Helper type guard to check for FetchError-like structure
interface FetchErrorLike extends Error {
  data?: {
    detail?: string;
    // Add other potential error fields from your API
  };
}

function isFetchErrorLike(error: unknown): error is FetchErrorLike {
  return (
    typeof error === 'object' &&
    error !== null &&
    'data' in error &&
    typeof (error as FetchErrorLike).data === 'object' &&
    (error as FetchErrorLike).data !== null &&
    ('detail' in (error as FetchErrorLike).data!)
  );
}

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<AuthenticatedUser | null>(null);
  const accessToken = ref<string | null>(null);
  // TODO: Consider storing refreshToken securely (e.g., httpOnly cookie handled by backend or localStorage with care)
  const isAuthenticated = ref(false);
  const isLoading = ref(false);
  const error = ref<string | null>(null);

  // Actions
  const login = async (credentials: UserLogin) => {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await $fetch<TokenResponse>('/api/auth/login', {
        method: 'POST',
        body: credentials,
      });

      accessToken.value = response.access_token;
      // Assuming the token itself contains enough info for AuthenticatedUser for now,
      // or you might need another call to a /users/me endpoint.
      // For simplicity, let's decode a pseudo-jwt or assume email is available.
      // In a real scenario, you'd decode the JWT or fetch user details.
      user.value = { 
        // id: decodedToken.sub, // Example if JWT sub is user ID
        id: 'temp-id-from-login', // Placeholder - adjust based on actual token or API response
        email: credentials.email 
      }; 
      isAuthenticated.value = true;

      // TODO: Handle refresh token (response.refresh_token) persistence
      console.log('Login successful, access token set.');

    } catch (err: unknown) {
      console.error('Login failed:', err);
      accessToken.value = null;
      user.value = null;
      isAuthenticated.value = false;
      if (isFetchErrorLike(err) && err.data?.detail) {
        error.value = err.data.detail;
      } else if (err instanceof Error) {
        error.value = err.message || 'Login failed. Please check your credentials.';
      } else if (typeof err === 'string') {
        error.value = err;
      } else {
        error.value = 'An unknown error occurred during login.';
      }
    } finally {
      isLoading.value = false;
    }
  };

  const register = async (userData: UserCreate) => {
    isLoading.value = true;
    error.value = null;
    try {
      const registeredUser = await $fetch<UserResponse>('/api/auth/register', {
        method: 'POST',
        body: userData,
      });
      console.log('Registration successful:', registeredUser);
    } catch (err: unknown) {
      console.error('Registration failed:', err);
      if (isFetchErrorLike(err) && err.data?.detail) {
        error.value = err.data.detail;
      } else if (err instanceof Error) {
        error.value = err.message || 'Registration failed. Please try again.';
      } else if (typeof err === 'string') {
        error.value = err;
      } else {
        error.value = 'An unknown error occurred during registration.';
      }
    } finally {
      isLoading.value = false;
    }
  };

  const logout = () => {
    // TODO: Implement API call to /auth/logout if your backend has an explicit logout endpoint (e.g., to invalidate refresh token)
    user.value = null;
    accessToken.value = null;
    isAuthenticated.value = false;
    error.value = null;
    // TODO: Clear persisted refresh token from localStorage or signal backend to clear httpOnly cookie
    console.log('User logged out');
  };

  const clearError = () => {
    error.value = null;
  };

  // TODO: Add action to check authentication status on app load (e.g., using a refresh token)
  // e.g., attemptToRefreshAccessToken() or checkAuthStatus()

  return {
    user,
    accessToken,
    isAuthenticated,
    isLoading,
    error,
    login,
    register,
    logout,
    clearError,
  };
}); 