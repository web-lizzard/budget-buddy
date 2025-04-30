<script setup lang="ts">
import type { Budget } from '~/types/budget'
import { Card, CardContent, CardHeader, CardTitle } from '~/components/ui/card'
import { format } from 'date-fns'

const props = defineProps<{ budget: Budget | null }>()

const formattedStartDate = computed(() => {
  return props.budget?.start_date ? format(new Date(props.budget.start_date), 'PP') : 'N/A'
})

const formattedEndDate = computed(() => {
  return props.budget?.end_date ? format(new Date(props.budget.end_date), 'PP') : 'N/A'
})

const formattedLimit = computed(() => {
    if (!props.budget?.total_limit) return 'N/A'
    // Basic currency formatting (consider a dedicated utility)
    return `${props.budget.total_limit.amount.toLocaleString()} ${props.budget.total_limit.currency}`
})
</script>

<template>
  <Card v-if="budget" class="mb-4">
    <CardHeader>
      <CardTitle>{{ budget.name }}</CardTitle>
    </CardHeader>
    <CardContent>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
        <div>
          <p class="text-muted-foreground">Date Range</p>
          <p class="font-medium">{{ formattedStartDate }} - {{ formattedEndDate }}</p>
        </div>
        <div>
          <p class="text-muted-foreground">Total Limit</p>
          <p class="font-medium">{{ formattedLimit }}</p>
        </div>
         <div>
          <p class="text-muted-foreground">Status</p>
          <p :class="[budget.is_active ? 'text-green-600' : 'text-red-600', 'font-medium']">
            {{ budget.is_active ? 'Active' : 'Inactive' }}
          </p>
        </div>
      </div>
    </CardContent>
  </Card>
  <div v-else>
    <!-- Optional: Placeholder or message when budget is null -->
    <p>Budget data not available.</p>
  </div>
</template>

<style scoped>
/* Add any specific styles for BudgetSummaryCard here */
</style>
