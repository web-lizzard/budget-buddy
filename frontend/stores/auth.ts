import { defineStore } from 'pinia';
import { ref } from 'vue';
import type {
  UserLogin,
  UserCreate,
  TokenResponse,
  UserResponse,
  AuthenticatedUser,
  NewAccessTokenResponse,
} from '@/types/auth';
import { extractUserIdFromToken, isTokenExpired } from '@/utils/jwt';

// Importuj typy z backendu, jeśli są dostępne i potrzebne
// import type { UserResponse, TokenResponse, UserLogin, UserCreate } from '~/types/api';

// Helper type guard to check for FetchError-like structure
interface FetchErrorLike extends Error {
  data?: {
    detail?: string;
    // Add other potential error fields from your API
  };
  status?: number; // Added to check for 401 specifically
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

// Storage keys for localStorage
const REFRESH_TOKEN_STORAGE_KEY = 'budgetBuddyRefreshToken';
const ACCESS_TOKEN_STORAGE_KEY = 'budgetBuddyAccessToken';
const USER_DATA_STORAGE_KEY = 'budgetBuddyUserData';

// Helper functions for localStorage operations
const getFromStorage = (key: string): string | null => {
  if (typeof localStorage === 'undefined') return null;
  try {
    return localStorage.getItem(key);
  } catch (error) {
    console.warn(`Failed to get ${key} from localStorage:`, error);
    return null;
  }
};

const setToStorage = (key: string, value: string): void => {
  if (typeof localStorage === 'undefined') return;
  try {
    localStorage.setItem(key, value);
  } catch (error) {
    console.warn(`Failed to set ${key} to localStorage:`, error);
  }
};

const removeFromStorage = (key: string): void => {
  if (typeof localStorage === 'undefined') return;
  try {
    localStorage.removeItem(key);
  } catch (error) {
    console.warn(`Failed to remove ${key} from localStorage:`, error);
  }
};

const getUserDataFromStorage = (): AuthenticatedUser | null => {
  const userData = getFromStorage(USER_DATA_STORAGE_KEY);
  if (!userData) return null;
  try {
    return JSON.parse(userData) as AuthenticatedUser;
  } catch (error) {
    console.warn('Failed to parse user data from localStorage:', error);
    return null;
  }
};

const setUserDataToStorage = (userData: AuthenticatedUser): void => {
  try {
    setToStorage(USER_DATA_STORAGE_KEY, JSON.stringify(userData));
  } catch (error) {
    console.warn('Failed to save user data to localStorage:', error);
  }
};

export const useAuthStore = defineStore('auth', () => {
  // State - Initialize access token from localStorage
  const user = ref<AuthenticatedUser | null>(getUserDataFromStorage());
  const accessToken = ref<string | null>(getFromStorage(ACCESS_TOKEN_STORAGE_KEY));
  const refreshToken = ref<string | null>(getFromStorage(REFRESH_TOKEN_STORAGE_KEY));
  const isAuthenticated = ref(false);
  const isLoading = ref(false); // General loading state
  const isRefreshingToken = ref(false); // Specific loading state for token refresh
  const error = ref<string | null>(null);

  // Helper function to update tokens in both state and localStorage
  const updateTokens = (accessTokenValue: string | null, refreshTokenValue: string | null) => {
    accessToken.value = accessTokenValue;
    refreshToken.value = refreshTokenValue;

    if (accessTokenValue) {
      setToStorage(ACCESS_TOKEN_STORAGE_KEY, accessTokenValue);
    } else {
      removeFromStorage(ACCESS_TOKEN_STORAGE_KEY);
    }

    if (refreshTokenValue) {
      setToStorage(REFRESH_TOKEN_STORAGE_KEY, refreshTokenValue);
    } else {
      removeFromStorage(REFRESH_TOKEN_STORAGE_KEY);
    }
  };

  // Helper function to update user data in both state and localStorage
  const updateUserData = (userData: AuthenticatedUser | null) => {
    user.value = userData;
    if (userData) {
      setUserDataToStorage(userData);
    } else {
      removeFromStorage(USER_DATA_STORAGE_KEY);
    }
  };

  // Actions
  const login = async (credentials: UserLogin) => {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await $fetch<TokenResponse>('/api/v0/auth/login', {
        method: 'POST',
        body: credentials,
      });

      // Update tokens in state and localStorage
      updateTokens(response.access_token, response.refresh_token);

      // Extract user ID from JWT token
      const userId = extractUserIdFromToken(response.access_token);
      if (!userId) {
        throw new Error('Failed to extract user ID from token');
      }

      const userData: AuthenticatedUser = {
        id: userId,
        email: credentials.email,
      };

      updateUserData(userData);
      isAuthenticated.value = true;

      console.log('Login successful, tokens and user data saved.');
    } catch (err: unknown) {
      console.error('Login failed:', err);
      updateTokens(null, null);
      updateUserData(null);
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
      const registeredUser = await $fetch<UserResponse>('/api/v0/auth/register', {
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
    // Optionally, call a backend endpoint to invalidate the refresh token
    // try {
    //   await $fetch('/api/v0/auth/logout', { method: 'POST' }); // Assuming such an endpoint exists
    // } catch (e) {
    //   console.warn('Failed to call backend logout endpoint:', e);
    // }
    updateTokens(null, null);
    updateUserData(null);
    isAuthenticated.value = false;
    error.value = null;
    console.log('User logged out, all tokens and data cleared.');
    // Potentially redirect to login page
    // const router = useRouter();
    // router.push('/login');
  };

  const clearError = () => {
    error.value = null;
  };

  const refreshAccessToken = async (): Promise<boolean> => {
    if (!refreshToken.value) {
      console.log('No refresh token available for refreshing.');
      isAuthenticated.value = false;
      return false;
    }

    isRefreshingToken.value = true;
    error.value = null;

    try {
      console.log('Attempting to refresh access token...');
      const response = await $fetch<NewAccessTokenResponse>('/api/v0/auth/refresh', {
        method: 'POST',
        body: { refresh_token: refreshToken.value },
      });

      // Update only access token, keep existing refresh token
      updateTokens(response.access_token, refreshToken.value);
      isAuthenticated.value = true;

      // Update user object with potentially new data from token
      if (user.value && accessToken.value) {
        const userId = extractUserIdFromToken(accessToken.value);
        if (userId && userId !== user.value.id) {
          const updatedUser = { ...user.value, id: userId };
          updateUserData(updatedUser);
        }
      }

      console.log('Access token refreshed successfully.');
      return true;
    } catch (err: unknown) {
      console.error('Failed to refresh access token:', err);
      const fetchError = err as FetchErrorLike;
      if (fetchError.status === 401) {
        console.log('Refresh token invalid or expired. Logging out.');
        logout();
      } else {
        if (isFetchErrorLike(err) && err.data?.detail) {
          error.value = err.data.detail;
        } else if (err instanceof Error) {
          error.value = err.message || 'Failed to refresh token.';
        } else {
          error.value = 'An unknown error occurred during token refresh.';
        }
        isAuthenticated.value = false;
        updateTokens(null, refreshToken.value); // Clear access token but keep refresh token
      }
      return false;
    } finally {
      isRefreshingToken.value = false;
    }
  };

  // Action to initialize authentication state, e.g., on app load
  const initializeAuth = async () => {
    isLoading.value = true;

    // First, check if we have a valid access token in localStorage
    if (accessToken.value && !isTokenExpired(accessToken.value)) {
      console.log('Found valid access token in localStorage.');
      isAuthenticated.value = true;

      // Ensure user data is available
      if (!user.value && accessToken.value) {
        const userId = extractUserIdFromToken(accessToken.value);
        if (userId) {
          updateUserData({
            id: userId,
            email: '', // Would need to be fetched or stored separately
          });
        }
      }

      console.log('Authentication initialized successfully with stored access token.');
    } else if (refreshToken.value) {
      console.log('Access token expired or missing, attempting refresh with refresh token.');
      const refreshed = await refreshAccessToken();
      if (refreshed) {
        console.log('Authentication initialized successfully via refresh token.');
      } else {
        console.log('Failed to initialize authentication via refresh token.');
      }
    } else {
      console.log('No tokens found. User needs to log in.');
      isAuthenticated.value = false;
      updateTokens(null, null);
      updateUserData(null);
    }

    isLoading.value = false;
  };

  return {
    user,
    accessToken,
    refreshToken,
    isAuthenticated,
    isLoading,
    isRefreshingToken,
    error,
    login,
    register,
    logout,
    clearError,
    refreshAccessToken,
    initializeAuth,
  };
});
