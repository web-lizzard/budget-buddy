import { ref, onUnmounted } from 'vue';

interface IntervalActionConfig {
  initialDelay?: number;
  maxDelay?: number;
  multiplier?: number;
  jitterRange?: number; // Max random ms to add/subtract for jitter
}

// Default configuration values
const DEFAULT_CONFIG: Required<IntervalActionConfig> = {
  initialDelay: 1000,
  maxDelay: 30000,
  multiplier: 2,
  jitterRange: 100, // Default jitter +/- 50ms
};

/**
 * Composable for running an asynchronous action periodically with exponential backoff and condition-based stopping.
 *
 * @param actionCallback - The async function to execute periodically. Must return a value.
 * @param conditionCallback - A function that takes the result of the actionCallback and returns true to stop the interval.
 * @param config - Optional configuration for timing and backoff.
 * @returns An object containing the stopInterval function.
 */
export function useIntervalAction<T>(
  actionCallback: () => Promise<T>,
  conditionCallback: (result: T) => boolean,
  config?: IntervalActionConfig
) {
  // Merge provided config with defaults
  const { initialDelay, maxDelay, multiplier, jitterRange } = {
    ...DEFAULT_CONFIG,
    ...config,
  };

  const timeoutId = ref<ReturnType<typeof setTimeout> | null>(null);
  const currentDelay = ref(initialDelay);
  const isActive = ref(true); // Track if the interval is currently active

  const stopInterval = () => {
    if (timeoutId.value !== null) {
      clearTimeout(timeoutId.value);
      timeoutId.value = null;
      isActive.value = false;
      console.log('[useIntervalAction] Interval manually stopped.');
    }
  };

  const executeAction = async () => {
    // Ensure it doesn't run again if stopped manually between schedule and execution
    if (!isActive.value) {
        console.log('[useIntervalAction] Execution skipped, interval not active.');
        return;
    }

    console.log('[useIntervalAction] Executing action...');
    try {
      const result = await actionCallback();
      console.log('[useIntervalAction] Action executed, result:', result);

      if (conditionCallback(result)) {
        console.log('[useIntervalAction] Condition met. Stopping interval.');
        stopInterval(); // Use the internal stop function which also sets isActive to false
      } else {
        // Calculate next delay with exponential backoff and jitter
        const jitter = Math.random() * jitterRange - jitterRange / 2; // Centered jitter
        const nextDelayRaw = currentDelay.value * multiplier + jitter;
        currentDelay.value = Math.min(Math.max(nextDelayRaw, 0), maxDelay); // Ensure delay doesn't go below 0 or exceed maxDelay

        console.log(`[useIntervalAction] Condition not met. Scheduling next action in ${currentDelay.value.toFixed(0)} ms.`);

        timeoutId.value = setTimeout(executeAction, currentDelay.value);
      }
    } catch (error) {
      console.error('[useIntervalAction] Error during action execution:', error);
      // Optional: Implement retry/error handling logic or stop on error
      // For now, we stop the interval on error to prevent potential infinite loops with failing actions
      console.log('[useIntervalAction] Stopping interval due to error.');
      stopInterval();
    }
  };



  onUnmounted(() => {
    console.log('[useIntervalAction] Component unmounted. Stopping interval.');
    stopInterval();
  });

  // Expose the manual stop function
  return { stopInterval, executeAction };
}
