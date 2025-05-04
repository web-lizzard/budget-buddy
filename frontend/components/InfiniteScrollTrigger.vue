<script setup lang="ts">
import { onMounted, onUnmounted, ref, watch } from 'vue';

// Define props
const props = defineProps<{
  // Optional: Allow custom observer options
  options?: IntersectionObserverInit;
  // Optional: Whether to disable the trigger temporarily
  disabled?: boolean;
}>();

// Define emits
const emit = defineEmits<{
  (e: 'intersected'): void;
}>();

// Reference to the element to observe
const triggerRef = ref<HTMLElement | null>(null);

// Observer instance
let observer: IntersectionObserver | null = null;

// Create and connect observer
onMounted(() => {
  // Skip if disabled
  if (props.disabled) return;

  // Create observer with default or custom options
  observer = new IntersectionObserver(entries => {
    // If the trigger element is intersecting (visible)
    if (entries[0]?.isIntersecting) {
      emit('intersected');
    }
  }, props.options || {
    // Default options
    rootMargin: '0px',
    threshold: 0.1 // Trigger when at least 10% of the element is visible
  });

  // Start observing the trigger element
  if (triggerRef.value) {
    observer.observe(triggerRef.value);
  }
});

// Clean up observer on component unmount
onUnmounted(() => {
  if (observer) {
    observer.disconnect();
    observer = null;
  }
});

// Watch for changes in disabled prop
watch(() => props.disabled, (isDisabled) => {
  if (!observer || !triggerRef.value) return;

  if (isDisabled) {
    // Stop observing if disabled
    observer.unobserve(triggerRef.value);
  } else {
    // Resume observing if enabled
    observer.observe(triggerRef.value);
  }
});
</script>

<template>
  <div ref="triggerRef" class="infinite-scroll-trigger">
    <!-- This element is usually invisible but can contain loading indicators -->
    <slot />
  </div>
</template>

<style scoped>
.infinite-scroll-trigger {
  /* Minimal required height to be observable */
  min-height: 1px;
}
</style>
