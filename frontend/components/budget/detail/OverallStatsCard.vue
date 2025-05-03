<script setup lang="ts">
import { computed } from 'vue' // Import computed
import type { BudgetStatistics } from '~/types/statistics'
import type { Money } from '~/types/money'
import { Card, CardContent, CardHeader, CardTitle } from '~/components/ui/card'
import { formatCurrency } from '~/utils/currency' // Import the helper
import LimitProgressBar from '~/components/LimitProgressBar.vue' // Import LimitProgressBar

const props = defineProps<{
    statistics: BudgetStatistics
    budgetLimit: Money
}>()

// Computed properties for formatted values
const currentBalance = computed(() => formatCurrency(props.statistics.currentBalance))
const dailyAvailable = computed(() => formatCurrency(props.statistics.dailyAvailableAmount))
const dailyAverage = computed(() => formatCurrency(props.statistics.dailyAverage))
const usedLimitValue = computed(() => props.statistics.usedLimit.amount)
const budgetLimitValue = computed(() => props.budgetLimit.amount)
const currency = computed(() => props.budgetLimit.currency)

// Add computed for progress bar later
// const limitProgress = computed(() => ...)

</script>

<template>
  <Card v-if="statistics" class="mb-4">
    <CardHeader>
      <CardTitle>Overall Statistics</CardTitle>
    </CardHeader>
    <CardContent>
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div>
          <p class="text-muted-foreground text-sm">Current Balance</p>
          <p class="font-medium text-lg">{{ currentBalance }}</p>
        </div>
        <div>
          <p class="text-muted-foreground text-sm">Daily Available</p>
          <p class="font-medium text-lg">{{ dailyAvailable }}</p>
        </div>
        <div>
          <p class="text-muted-foreground text-sm">Daily Average</p>
          <p class="font-medium text-lg">{{ dailyAverage }}</p>
        </div>
        <div>
          <p class="text-muted-foreground text-sm">Limit Usage</p>
          <LimitProgressBar
            :current-value="usedLimitValue"
            :limit-value="budgetLimitValue"
            :currency="currency"
            class="mt-2"
           />
        </div>
      </div>
    </CardContent>
  </Card>
  <div v-else>
    <Card class="mb-4 border-dashed">
      <CardHeader>
          <CardTitle>Overall Statistics</CardTitle>
      </CardHeader>
       <CardContent>
           <p class="text-muted-foreground text-sm">Statistics data is currently unavailable.</p>
       </CardContent>
    </Card>
  </div>
</template>

<style scoped>
/* Add any specific styles for OverallStatsCard here */
</style>
