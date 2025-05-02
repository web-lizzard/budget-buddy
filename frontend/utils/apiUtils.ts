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



export const apiConfig  = {
    baseURL: "/v0/",
    commonOptions: {
        headers: {
            'Content-Type': 'application/json',
        },
    },
}
