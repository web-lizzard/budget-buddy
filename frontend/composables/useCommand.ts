import { ref, type Ref } from 'vue';
import type { DomainError } from '@/types/dtos'; // Adjusted based on where DomainError is defined
import { mapToDomainError } from '@/utils/apiUtils'; // Ensure path is correct

// Define the type for the async function that performs the command
type CommandExecutor<P = void> = (payload: P) => Promise<void>;

// Define options for useCommand
interface UseCommandOptions {
  onSuccess?: () => Promise<void> | void; // Renamed from onActionDone for clarity
  onError?: (error: DomainError) => Promise<void> | void;
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

  const { onSuccess, onError } = options;

  /**
   * Executes the command.
   * @param payload - The data/payload required by the executor function.
   * @returns The result from the executor, or undefined if an error occurred.
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
       // Assume service layer throws DomainError directly or map other errors
       const mappedError = err && typeof err === 'object' && 'status' in err && 'message' in err && typeof err.status === 'string'
            ? err as DomainError // Assume it's already a DomainError
            : mapToDomainError(err, 'Command execution failed');

       error.value = mappedError;
       if (onError) {
           await onError(mappedError);
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
