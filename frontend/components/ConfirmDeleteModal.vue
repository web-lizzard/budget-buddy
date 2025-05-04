<script setup lang="ts">
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '~/components/ui/alert-dialog';
import { Button } from '~/components/ui/button';

// Define props
const props = withDefaults(defineProps<{
  isOpen: boolean;
  title?: string;
  message?: string;
  confirmText?: string;
  cancelText?: string;
  isConfirming?: boolean; // To disable buttons during confirmation
}>(), {
  title: 'Are you absolutely sure?',
  message: 'This action cannot be undone.',
  confirmText: 'Confirm',
  cancelText: 'Cancel',
  isConfirming: false,
});

// Define emits
const emit = defineEmits<{
  (e: 'update:isOpen', value: boolean): void;
  (e: 'confirm' | "cancel"): void;
}>();

// Handle internal open state changes
const handleOpenChange = (open: boolean) => {
  emit('update:isOpen', open);
  if (!open) {
    // Also emit cancel if closed without confirmation
    emit('cancel');
  }
};

const onConfirm = () => {
  if (props.isConfirming) return; // Prevent double clicks
  emit('confirm');
};

const onCancel = () => {
  emit('update:isOpen', false);
  emit('cancel');
};
</script>

<template>
  <AlertDialog :open="isOpen" @update:open="handleOpenChange">
    <AlertDialogContent>
      <AlertDialogHeader>
        <AlertDialogTitle>{{ title }}</AlertDialogTitle>
        <AlertDialogDescription>
          {{ message }}
        </AlertDialogDescription>
      </AlertDialogHeader>
      <AlertDialogFooter>
        <AlertDialogCancel as-child>
          <Button variant="outline" :disabled="isConfirming" @click="onCancel">
            {{ cancelText }}
          </Button>
        </AlertDialogCancel>
        <AlertDialogAction as-child>
          <Button variant="destructive" :disabled="isConfirming" @click="onConfirm">
            {{ isConfirming ? 'Confirming...' : confirmText }}
          </Button>
        </AlertDialogAction>
      </AlertDialogFooter>
    </AlertDialogContent>
  </AlertDialog>
</template>
