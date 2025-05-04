import { ref, computed, type MaybeRef, type WatchSource, unref } from 'vue';
import { useAsyncData, type AsyncDataOptions } from '#app';
import type { DomainError } from '@/types/dtos';
import { mapToDomainError } from '@/utils/apiUtils';

type QueryFetcher<TResponse, TParams = unknown> = (params?: TParams) => Promise<TResponse>;

interface UseQueryOptions<T, P = unknown> extends Omit<AsyncDataOptions<T>, 'watch'> {
  onError?: (error: DomainError) => void;
  initialParams?: P;
}

/**
 * Composable for handling asynchronous data fetching (GET requests).
 * Wraps Nuxt's useAsyncData with standardized error handling and structure.
 * Supports passing parameters during refresh.
 *
 * @param key - Unique key for the data cache (passed to useAsyncData).
 * @param fetcher - An async function that fetches and returns data, can accept parameters.
 * @param options - Options object including standard useAsyncData options and custom ones like onError and initialParams.
 * @param watchSources - Optional array of refs/reactives to watch for triggering automatic refresh.
 */
export function useQuery<TResponse, TParams = unknown, TWatchers = unknown>(
  key: MaybeRef<string>,
  fetcher: QueryFetcher<TResponse, TParams>,
  options: UseQueryOptions<TResponse, TParams> = {},
  watchSources: WatchSource<TWatchers>[] = []
) {
  const domainError = ref<DomainError | null>(null);
  const unrefKey = computed(() => `query-${unref(key)}`);

  const currentParams = ref<TParams | undefined>(options.initialParams);

  const { onError: onErrorCallback, initialParams, ...asyncDataOptions } = options;

  const { data, pending, refresh: nuxtRefresh, execute: nuxtExecute } = useAsyncData<TResponse>(
    unrefKey.value,
    async () => {
      domainError.value = null;
      try {
        const result = await fetcher(currentParams.value);
        return result;
      } catch (err: unknown) {
         const mappedError = err && typeof err === 'object' && 'status' in err && 'message' in err && typeof err.status === 'string'
             ? err as DomainError
             : mapToDomainError(err, 'Data fetching failed');

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

  const refresh = async (params?: TParams) => {
    if (params !== undefined) {
      currentParams.value = params;
    }
    return nuxtRefresh();
  };

  const execute = async (params?: TParams) => {
    if (params !== undefined) {
      currentParams.value = params;
    }
    return nuxtExecute();
  };

  return {
    data,
    pending,
    error: domainError,
    refresh,
    execute,
    // Udostępniamy parametry na wypadek potrzeby do nich dostępu
    params: currentParams,
  };
}
