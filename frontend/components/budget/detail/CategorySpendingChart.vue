<script setup lang="ts">
import { computed } from 'vue'
import { Doughnut } from 'vue-chartjs'
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  CategoryScale,
  type TooltipItem,
} from 'chart.js'
import type { ChartDataViewModel } from '@/types/viewmodels'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DEFAULT_CHART_COLORS } from '@/constants/charts'


// Register Chart.js components
// (Might be done globally in a Nuxt plugin instead)
ChartJS.register(Title, Tooltip, Legend, ArcElement, CategoryScale)

const props = defineProps<{
  chartData: ChartDataViewModel | null
}>()

const hasData = computed(() => {
  return (
    props.chartData &&
    props.chartData.labels.length > 0 &&
    props.chartData.datasets.length > 0 &&
    props.chartData.datasets[0].data.some(value => value > 0) // Check if there's any non-zero spending
  )
})

// Default Chart.js options
const chartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'right' as const, // Position legend on the right
    },
    tooltip: {
      callbacks: {
        // Customize tooltip to show currency (requires access to raw amounts or formatting)
        // This basic example just shows the value
        label: function(context: TooltipItem<'doughnut'>) {
            let label = context.dataset.label || '';
            if (label) {
                label += ': ';
            }
            if (context.parsed !== null) {
                 // TODO: Find a way to get currency/format properly
                label += context.parsed.toFixed(2); // Example: format as needed
            }
            return label;
        }
      }
    }
  },
}))

// Prepare data in the structure vue-chartjs expects
const doughnutChartData = computed(() => {
    if (!hasData.value || !props.chartData) {
        // Return a structure Chart.js understands even when empty
        return {
            labels: [],
            datasets: [{
                 data: [],
                 backgroundColor: [],
            }]
        }
    }
    return {
        labels: props.chartData.labels,
        datasets: props.chartData.datasets.map(dataset => ({
            ...dataset,
            // Use imported default colors
            backgroundColor: dataset.backgroundColor && dataset.backgroundColor.length > 0
                ? dataset.backgroundColor
                : DEFAULT_CHART_COLORS // Use constant
        }))
    }
})

</script>

<template>
  <Card class="mb-4">
    <CardHeader>
      <CardTitle>Spending by Category</CardTitle>
    </CardHeader>
    <CardContent>
      <div v-if="hasData" class="chart-container relative h-64 md:h-80">
          <Doughnut
            :data="doughnutChartData"
            :options="chartOptions"
          />
      </div>
      <div v-else class="text-center text-muted-foreground py-10">
          <p>No spending data available to display the chart.</p>
      </div>
    </CardContent>
  </Card>
</template>

<style scoped>
/* Ensure chart container allows the chart to be responsive */
.chart-container {
  position: relative;
  /* height: 300px; You might need to set a fixed height or aspect ratio */
}
</style>
