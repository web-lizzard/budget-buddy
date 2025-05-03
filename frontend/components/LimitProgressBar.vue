<script setup lang="ts">
import { computed } from 'vue'
import { Progress } from '~/components/ui/progress' // Import Shadcn Progress
import { AlertCircle } from 'lucide-vue-next' // Import warning icon
import { formatCurrency } from '~/utils/currency'
import type { Money } from '~/types/money'

const props = withDefaults(defineProps<{
  currentValue: number | undefined | null
  limitValue: number | undefined | null
  currency: string | undefined | null
  label?: string // Optional label (e.g., "Category Limit")
}>(), {
    currentValue: 0,
    limitValue: 0,
    currency: ''
})

const progressPercentage = computed(() => {
  const current = props.currentValue ?? 0
  const limit = props.limitValue ?? 0
  if (limit <= 0) {
    return current > 0 ? 100 : 0
  }
  const percentage = (current / limit) * 100
  return percentage;
})

const displayPercentage = computed(() => {
    return Math.round(progressPercentage.value);
})

const isOverLimit = computed(() => progressPercentage.value > 100)
const isWarning = computed(() => progressPercentage.value > 80 && progressPercentage.value <= 100)
const isNearLimit = computed(() => progressPercentage.value > 80);
const currentMoney: Money = {
    amount: props.currentValue ?? 0,
    currency: props.currency ?? ''
}

const limitMoney: Money = {
    amount: props.limitValue ?? 0,
    currency: props.currency ?? ''
}

const formattedCurrent = computed(() => formatCurrency(currentMoney))
const formattedLimit = computed(() => formatCurrency(limitMoney))

</script>

<template>
  <div>
    <div v-if="label" class="text-sm font-medium mb-1">{{ label }}</div>
    <Progress
        :model-value="displayPercentage"
        class="w-full h-2"
        :class="{
            '[&>*]:bg-red-500': isOverLimit,
            '[&>*]:bg-yellow-500': isWarning,
        }"
    />
    <div class="flex justify-between items-center mt-1 text-xs text-muted-foreground">
      <span>{{ formattedCurrent }} / {{ formattedLimit }}</span>
      <div class="flex items-center">
         <AlertCircle v-if="isNearLimit" class="h-4 w-4 text-red-500 ml-1" />
         <span :class="{'text-red-500 font-semibold': isNearLimit }">
             ({{ displayPercentage }}%)
          </span>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Customize progress bar appearance if needed */
</style>
