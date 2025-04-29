<script setup lang="ts">
import { Button } from '@/components/ui/button'

// Define emits
const emit = defineEmits<{
  (e: 'click'): void;
}>();

function handleClick() {
    emit('click');
}
</script>

<template>
    <Button @click="handleClick">
        <!-- Optional: Add icon here -->
        Create Budget
    </Button>
</template>
