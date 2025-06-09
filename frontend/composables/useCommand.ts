import { ref, type Ref } from 'vue';
import type { DomainError } from '@/types/dtos'; // Adjusted based on where DomainError is defined
import { mapToDomainError } from '@/utils/apiUtils'; // Ensure path is correct
import { useAuthStore } from '@/stores/auth'; // Import the auth store

// Define the type for the async function that performs the command
type CommandExecutor<P = void> = (payload: P) => Promise<void>;

// Define options for useCommand
interface UseCommandOptions {
  onSuccess?: () => Promise<void> | void; // Renamed from onActionDone for clarity
  onError?: (error: DomainError) => Promise<void> | void;
  requireAuth?: boolean; // Option to indicate if the command requires authentication
}

/**
 * Composable for handling state-changing API operations (POST, PUT, DELETE).
 * Provides loading state, error handling, and callbacks.
 *
 * @param executor - An async function that performs the command (e.g., calling a service method).
 * @param options - Configuration object with onSuccess and onError callbacks.
 */
export function useCommand<P = void>(
  executor: CommandExecutor<P>,
  options: UseCommandOptions = {}
) {
  const loading: Ref<boolean> = ref(false);
  const error: Ref<DomainError | null> = ref(null);
  const authStore = useAuthStore(); // Get the auth store instance

  const { onSuccess, onError, requireAuth = true } = options; // Default requireAuth to true

  /**
   * Executes the command.
   * @param payload - The data/payload required by the executor function.
   */
  const execute = async (payload: P): Promise<void> => {
    loading.value = true;
    error.value = null;

    try {
      await executor(payload);
      if (onSuccess) {
        await onSuccess();
      }
    } catch (err: unknown) {
      // Attempt to map the error to DomainError first
      const mappedError = err && typeof err === 'object' && 'status' in err && 'message' in err && typeof err.status === 'string'
          ? err as DomainError // Assume it's already a DomainError
          : mapToDomainError(err, 'Command execution failed');

      // Check for 401 Unauthorized and if authentication is required for this command
      // Also check if a token refresh is already in progress
      if (
        requireAuth &&
        mappedError.status?.toString() === '401' &&
        authStore.refreshToken &&
        !authStore.isRefreshingToken
      ) {
        console.log('useCommand: Detected 401, attempting token refresh.');
        try {
          const refreshed = await authStore.refreshAccessToken();
          if (refreshed) {
            console.log('useCommand: Token refreshed successfully, retrying original command.');
            // Retry the original command
            await executor(payload); // Re-execute after successful refresh
            if (onSuccess) {
              await onSuccess(); // Call success callback if retry is successful
            }
            return; // Exit after successful retry
          } else {
            console.log('useCommand: Token refresh failed. User will be logged out if not already.');
            // If refresh failed, error is already set in authStore, or logout was called.
            // We still need to set the local error state for this command execution attempt.
            error.value = mappedError; // Keep the original 401 error for this specific command context
            if (onError) {
              await onError(mappedError);
            }
          }
        } catch (refreshError: unknown) {
          console.error('useCommand: Error during token refresh attempt:', refreshError);
          // If refreshAccessToken itself throws an error (should be handled internally by it)
          // For safety, set the original error and call onError
          error.value = mappedError;
          if (onError) {
            await onError(mappedError);
          }
        }
      } else {
        // Handle non-401 errors or if refresh is not applicable/in progress
        error.value = mappedError;
        if (onError) {
          await onError(mappedError);
        }
      }
    } finally {
      loading.value = false;
    }
  };

  return {
    loading,
    error,
    execute,
  };
}
