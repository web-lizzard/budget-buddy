<script setup lang="ts">
import { onMounted, onUnmounted, ref, watch } from 'vue';

const props = defineProps<{
  options?: IntersectionObserverInit;
  disabled?: boolean;
}>();

const emit = defineEmits<{
  (e: 'intersected'): void;
}>();

const triggerRef = ref<HTMLElement | null>(null);
let observer: IntersectionObserver | null = null;

onMounted(() => {
  if (props.disabled) return;

  observer = new IntersectionObserver(entries => {
    if (entries[0]?.isIntersecting) {
      emit('intersected');
    }
  }, props.options || {
    rootMargin: '0px',
    threshold: 0.1 // Trigger when at least 10% of the element is visible
  });

  if (triggerRef.value) {
    observer.observe(triggerRef.value);
  }
});

onUnmounted(() => {
  if (observer) {
    observer.disconnect();
    observer = null;
  }
});

watch(() => props.disabled, (isDisabled) => {
  if (!observer || !triggerRef.value) return;

  if (isDisabled) {
    observer.unobserve(triggerRef.value);
  } else {
    observer.observe(triggerRef.value);
  }
});
</script>

<template>
  <div ref="triggerRef" class="infinite-scroll-trigger">
    <slot />
  </div>
</template>

<style scoped>
.infinite-scroll-trigger {
  min-height: 1px;
}
</style>
