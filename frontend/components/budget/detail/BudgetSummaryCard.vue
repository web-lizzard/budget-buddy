<script setup lang="ts">
import type { Budget } from '~/types/budget'
import { Card, CardContent, CardHeader, CardTitle } from '~/components/ui/card'
import { format } from 'date-fns'

const props = defineProps<{ budget: Budget }>()

const formattedStartDate = computed(() => {
  return format(props.budget.startDate, 'MMM d, yyyy')
})

const formattedEndDate = computed(() => {
  return format(props.budget.endDate, 'MMM d, yyyy')
})

const formattedLimit = computed(() => {
    return `${props.budget.totalLimit.amount.toLocaleString()} ${props.budget.totalLimit.currency}`
})
</script>

<template>
  <Card class="mb-4">
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
          <p :class="[budget.isActive ? 'text-green-600' : 'text-red-600', 'font-medium']">
            {{ budget.isActive ? 'Active' : 'Inactive' }}
          </p>
        </div>
      </div>
    </CardContent>
  </Card>

</template>

<style scoped>
/* Add any specific styles for BudgetSummaryCard here */
</style>
