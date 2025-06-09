import { FetchError } from 'ofetch';
import type { DomainError } from '@/types/dtos';
import { type DomainErrorStatus, isDomainErrorStatus } from '@/types/domainErrorStatus';

/**
 * Maps various error types (FetchError, Error, unknown) into a standardized DomainError.
 *
 * @param error - The error object caught from an API call.
 * @param contextMessage - A specific message providing context about the failed operation.
 * @returns A standardized DomainError object.
 */
export function mapToDomainError(error: unknown, contextMessage: string = 'An API error occurred'): DomainError {
  let httpStatus = 500; // Keep track of HTTP status for potential fallback/logging
  let domainStatus: DomainErrorStatus = 'internal_server_error'; // Default domain status
  let message = contextMessage;

  if (error instanceof FetchError) {
    httpStatus = error.statusCode ?? 500;

    // Extract domain status and message from backend response if available
    const backendStatus = error.data?.status;
    const backendMessage = error.data?.message || error.data?.detail;

    if (backendStatus && typeof backendStatus === 'string' && isDomainErrorStatus(backendStatus)) {
      domainStatus = backendStatus;
      // Use backend message if available, otherwise construct one
      message = backendMessage ? `${contextMessage}: ${backendMessage}` : `${contextMessage} (${domainStatus})`;
    } else {
      // Fallback if backend status is missing or not recognized
      domainStatus = httpStatus >= 500 ? 'internal_server_error' : 'network_error'; // Simple fallback
      message = backendMessage
        ? `${contextMessage}: ${backendMessage} (HTTP ${httpStatus})`
        : `${contextMessage} (HTTP Status: ${httpStatus})`;
      if (backendStatus) {
        console.warn(`Unrecognized domain status from API: ${backendStatus}`);
        domainStatus = 'unknown_domain_error'; // More specific fallback
      }
    }

    console.error(`API FetchError (HTTP ${httpStatus}, Domain ${domainStatus}): ${message}`, error);

  } else if (error instanceof Error) {
    // Handle generic JS errors (e.g., validation errors before fetch, parsing errors)
    message = `${contextMessage}: ${error.message}`;
    domainStatus = 'validation_error'; // Or map based on error type if possible
    console.error(`API Client Error (${domainStatus}): ${message}`, error);

  } else {
    // Handle unknown errors
    message = `${contextMessage}: An unknown error occurred.`;
    domainStatus = 'unknown_domain_error';
    console.error(`Unknown API Error (${domainStatus}): ${message}`, error);
  }

  return {
    status: domainStatus, // Use the derived DomainErrorStatus string
    message,
  };
}

// Future potential helpers: function to transform snake_case to camelCase, etc.
// Although Zod's .transform() is preferred for schema-based transformations.

/**
 * Creates headers with authentication token if available
 */
export function createAuthHeaders(): Record<string, string> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };

  // Add Authorization header if we're on client side and have auth store
  if (import.meta.client) {
    try {
      const authStore = useAuthStore();
      if (authStore.accessToken && authStore.isAuthenticated) {
        headers['Authorization'] = `Bearer ${authStore.accessToken}`;
      }
    } catch (error) {
      // Store might not be available during SSR
      console.warn('Could not access auth store for headers:', error);
    }
  }

  return headers;
}

/**
 * Debug function to test if auth headers are being created correctly
 */
export function testAuthHeaders(): void {
  if (import.meta.client) {
    const headers = createAuthHeaders();

    // Check localStorage tokens for debugging
    const accessTokenInStorage = localStorage.getItem('budgetBuddyAccessToken');
    const refreshTokenInStorage = localStorage.getItem('budgetBuddyRefreshToken');
    const userDataInStorage = localStorage.getItem('budgetBuddyUserData');

    console.log('🔍 Auth Headers Test:', {
      hasContentType: !!headers['Content-Type'],
      hasAuthorization: !!headers['Authorization'],
      authHeader: headers['Authorization']?.substring(0, 20) + '...' || 'Not present',
      allHeaders: Object.keys(headers)
    });

    console.log('🔍 localStorage Tokens:', {
      hasAccessToken: !!accessTokenInStorage,
      hasRefreshToken: !!refreshTokenInStorage,
      hasUserData: !!userDataInStorage,
      accessTokenPreview: accessTokenInStorage?.substring(0, 20) + '...' || 'Not present',
      refreshTokenPreview: refreshTokenInStorage?.substring(0, 20) + '...' || 'Not present',
      userData: userDataInStorage ? JSON.parse(userDataInStorage) : 'Not present'
    });

    console.log('🔍 Auth Store State:');
    try {
      const authStore = useAuthStore();
      console.log({
        isAuthenticated: authStore.isAuthenticated,
        hasAccessTokenInStore: !!authStore.accessToken,
        hasRefreshTokenInStore: !!authStore.refreshToken,
        hasUser: !!authStore.user,
        accessTokenMatch: authStore.accessToken === accessTokenInStorage,
        refreshTokenMatch: authStore.refreshToken === refreshTokenInStorage
      });
    } catch (error) {
      console.warn('Could not access auth store:', error);
    }
  }
}

export const apiConfig = {
    baseURL: "/api/v0",
    commonOptions: {
        headers: {
            'Content-Type': 'application/json',
        },
    },
    // New method to get options with auth headers
    getAuthOptions: () => ({
        headers: createAuthHeaders(),
    }),
};
