import { ref, computed, type MaybeRef, type WatchSource, unref } from 'vue';
import { useAsyncData, type AsyncDataOptions } from '#app';
import type { DomainError } from '@/types/dtos'; // Adjusted based on where DomainError is defined
import { mapToDomainError } from '@/utils/apiUtils'; // Ensure path is correct

// Define a type for the async function that useQuery will wrap
type QueryFetcher<T> = () => Promise<T>;

// Define options specific to useQuery, extending useAsyncData options
interface UseQueryOptions<T> extends Omit<AsyncDataOptions<T>, 'watch'> {
  onError?: (error: DomainError) => void; // Using DomainError type from dtos
}

/**
 * Composable for handling asynchronous data fetching (GET requests).
 * Wraps Nuxt's useAsyncData with standardized error handling and structure.
 *P
 * @param key - Unique key for the data cache (passed to useAsyncData).
 * @param fetcher - An async function that fetches and returns data (e.g., calling a service method).
 * @param options - Options object including standard useAsyncData options and custom ones like onError.
 * @param watchSources - Optional array of refs/reactives to watch for triggering automatic refresh (passed to useAsyncData's watch).
 */
export function useQuery<TResponse, TWatchers>(
  key: MaybeRef<string>,
  fetcher: QueryFetcher<TResponse>,
  options: UseQueryOptions<TResponse> = {},
  watchSources: WatchSource<TWatchers>[] = []
) {
  const domainError = ref<DomainError | null>(null);
  const unrefKey = computed(() => `query-${unref(key)}`);

  const { onError: onErrorCallback, ...asyncDataOptions } = options;

  const { data, pending, refresh, execute } = useAsyncData<TResponse>(
    unrefKey.value,
    async () => {
      domainError.value = null;
      try {
        const result = await fetcher();
        return result;
      } catch (err: unknown) {
         // Assume service layer throws DomainError directly or map other errors
         const mappedError = err && typeof err === 'object' && 'status' in err && 'message' in err && typeof err.status === 'string'
             ? err as DomainError // Assume it's already a DomainError from the service layer
             : mapToDomainError(err, 'Data fetching failed'); // Map other errors

         domainError.value = mappedError;

         if (onErrorCallback) {
             onErrorCallback(mappedError);
         }
         throw mappedError;
      }
    },
    {
      ...asyncDataOptions,
      watch: watchSources,
      lazy: options.lazy ?? true,
    }
  );



  return {
    data,
    pending,
    error: domainError, // Our standardized error ref
    refresh,
    execute,
  };
}
