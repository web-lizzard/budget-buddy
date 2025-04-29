<script setup lang="ts">
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs'
import type { BudgetFilterValue } from '@/types/budget';

// Define props
const props = defineProps<{
  modelValue: BudgetFilterValue;
}>();

// Define emits
const emit = defineEmits<{
  (e: 'update:modelValue', value: BudgetFilterValue): void;
}>();

// Method to handle update event from Tabs
function handleUpdate(value: string | number | undefined) {
    if (value === 'all' || value === 'active' || value === 'expired') {
         emit('update:modelValue', value as BudgetFilterValue);

            }
        }

// Filter options
const filterOptions: { label: string; value: BudgetFilterValue }[] = [
  { label: 'All', value: 'all' },
  { label: 'Active', value: 'active' },
  { label: 'Expired', value: 'expired' },
];

</script>

<template>
  <!-- Use a method to handle the update event -->
  <Tabs :model-value="props.modelValue" @update:model-value="handleUpdate">
     <TabsList class="grid w-full grid-cols-3 md:w-[400px]">
       <TabsTrigger
         v-for="option in filterOptions"
         :key="option.value"
         :value="option.value"
       >
         {{ option.label }}
       </TabsTrigger>
     </TabsList>
  </Tabs>
</template>
