<script setup lang="ts">
import { computed, type PropType } from 'vue';
import type { BudgetListItemViewModel, BudgetSortOption } from '@/types/budget';
import {
  Table,
  TableBody,
  TableCaption,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { Skeleton } from '@/components/ui/skeleton'
import { Button } from '@/components/ui/button'
import { ArrowUpDown, ArrowUp, ArrowDown } from 'lucide-vue-next'

// Define Props
const props = defineProps({
  budgets: {
    type: Array as PropType<BudgetListItemViewModel[]>,
    required: true,
  },
  isLoading: {
    type: Boolean,
    required: true,
  },
  pagination: {
    type: Object as PropType<{ currentPage: number; itemsPerPage: number; totalItems: number; }>,
    required: true,
  },
  sorting: {
    type: Object as PropType<BudgetSortOption>,
    required: true,
  },
});

// Define Emits
const emit = defineEmits<{
  (e: 'update:pagination', value: { page: number }): void;
  (e: 'update:sorting', value: BudgetSortOption): void;
  (e: 'row-click', value: { id: string }): void;
}>();

// Calculate total pages for pagination
const totalPages = computed(() => {
    if (!props.pagination || props.pagination.itemsPerPage <= 0) {
        return 0;
    }
    return Math.ceil(props.pagination.totalItems / props.pagination.itemsPerPage);
});

// Placeholder for column definitions - customize as needed
const columns = [
    { key: 'name', label: 'Name', sortable: true },
    { key: 'statusLabel', label: 'Status', sortable: false },
    { key: 'dateRange', label: 'Date Range', sortable: true, dataKey: 'startDate' }, // Sort by startDate
    { key: 'limitFormatted', label: 'Limit', sortable: false },
];

// Formatting Helpers
function formatDateRange(startDateStr: string, endDateStr: string): string {
    try {
        const options: Intl.DateTimeFormatOptions = { year: 'numeric', month: '2-digit', day: '2-digit' };
        const startDate = new Date(startDateStr).toLocaleDateString(undefined, options);
        const endDate = new Date(endDateStr).toLocaleDateString(undefined, options);
        return `${startDate} - ${endDate}`;
    } catch (e) {
        console.error("Error formatting date range:", e);
        // Fallback to basic string split if Intl fails or dates are invalid
        return `${startDateStr.split('T')[0]} - ${endDateStr.split('T')[0]}`;
    }
}

function formatCurrency(amount: number, currencyCode: string): string {
    try {
        const options: Intl.NumberFormatOptions = { style: 'currency', currency: currencyCode };
        return new Intl.NumberFormat(undefined, options).format(amount);
    } catch (e) {
        console.error("Error formatting currency:", e);
        // Fallback to basic concatenation
        return `${amount.toFixed(2)} ${currencyCode}`;
    }
}

// Extracts amount and currency from the combined string (e.g., "1000 PLN")
// This relies on the format set in the store's mapper - consider passing raw amount/currency directly
function parseLimitString(limitString: string): { amount: number, currency: string } {
    const parts = limitString.split(' ');
    const amount = parseFloat(parts[0].replace(/,/g, '')); // Handle potential thousand separators if Intl was used before
    const currency = parts[1] || ''
    return { amount: isNaN(amount) ? 0 : amount, currency };
}

// Methods (to be implemented later)
function handleSort(columnKey: string) {
    let newSortOrder: 'asc' | 'desc';

    // If clicking the same column, toggle order
    if (props.sorting.sortBy === columnKey) {
        newSortOrder = props.sorting.sortOrder === 'asc' ? 'desc' : 'asc';
    }
    // If clicking a new column, default to ascending
    else {
        newSortOrder = 'asc';
    }

    emit('update:sorting', { sortBy: columnKey, sortOrder: newSortOrder });
}

function handleRowClick(budgetId: string) {
    emit('row-click', { id: budgetId });
}

function handlePageChange(newPage: number) {
    // Ensure newPage is within valid bounds
    const clampedPage = Math.max(1, Math.min(newPage, totalPages.value));
    if (clampedPage !== props.pagination.currentPage) {
        emit('update:pagination', { page: clampedPage });
    }
}

</script>

<template>
  <div>
    <Table>
      <TableCaption v-if="!isLoading && budgets.length === 0">
        No budgets found.
      </TableCaption>
      <TableHeader>
        <TableRow>
          <!-- Loop through columns to create headers -->
          <TableHead
             v-for="column in columns"
             :key="column.key"
             :class="{ 'cursor-pointer hover:bg-muted/50': column.sortable }"
             class="whitespace-nowrap"
             @click="column.sortable ? handleSort(column.dataKey || column.key) : null"
          >
            <div class="flex items-center gap-2">
                {{ column.label }}
                <!-- Sorting Indicator -->
                <template v-if="column.sortable">
                    <ArrowUp
                        v-if="sorting.sortBy === (column.dataKey || column.key) && sorting.sortOrder === 'asc'"
                        class="h-4 w-4"
                     />
                    <ArrowDown
                        v-else-if="sorting.sortBy === (column.dataKey || column.key) && sorting.sortOrder === 'desc'"
                        class="h-4 w-4"
                    />
                    <ArrowUpDown
                        v-else
                        class="h-4 w-4 text-muted-foreground"
                    />
                </template>
            </div>
          </TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        <!-- Loading State: Show Skeleton Rows -->
        <template v-if="isLoading">
          <TableRow v-for="n in pagination.itemsPerPage" :key="`skel-${n}`">
            <TableCell v-for="column in columns" :key="`skel-cell-${column.key}-${n}`">
              <Skeleton class="h-4 w-full" />
            </TableCell>
          </TableRow>
        </template>

        <!-- Data Rows -->
        <template v-else-if="budgets.length > 0">
          <TableRow
            v-for="budget in budgets"
            :key="budget.id"
            class="cursor-pointer hover:bg-muted/50"
            @click="handleRowClick(budget.id)"
          >
            <!-- Loop through columns to display formatted data -->
            <TableCell v-for="column in columns" :key="`cell-${column.key}-${budget.id}`">
                <template v-if="column.key === 'dateRange'">
                    {{ formatDateRange(budget.startDate, budget.endDate) }} <!-- Assuming endDate is available or added to ViewModel -->
                    <!-- If endDate is not in ViewModel, might need adjustment or get it from budget.dateRange split -->
                </template>
                <template v-else-if="column.key === 'limitFormatted'">
                     <!-- Parse the string first -->
                     {{ formatCurrency(parseLimitString(budget.limitFormatted).amount, parseLimitString(budget.limitFormatted).currency) }}
                    <!-- Ideally, ViewModel should provide raw amount and currency -->
                    <!-- {{ formatCurrency(budget.limitAmount, budget.currency) }} -->
                </template>
                <template v-else>
                    {{ budget[column.key as keyof BudgetListItemViewModel] }}
                </template>
            </TableCell>
          </TableRow>
        </template>

        <!-- Empty state message is handled by TableCaption -->

      </TableBody>
    </Table>

    <!-- Simple Pagination Controls -->
    <div v-if="totalPages > 0" class="flex items-center justify-between space-x-2 py-4">
        <div class="text-sm text-muted-foreground">
            Page {{ pagination.currentPage }} of {{ totalPages }}
            ({{ pagination.totalItems }} total budgets)
        </div>
        <div class="space-x-2">
            <Button
                variant="outline"
                size="sm"
                :disabled="pagination.currentPage <= 1"
                @click="handlePageChange(pagination.currentPage - 1)"
            >
                Previous
            </Button>
            <Button
                variant="outline"
                size="sm"
                :disabled="pagination.currentPage >= totalPages"
                @click="handlePageChange(pagination.currentPage + 1)"
            >
                Next
            </Button>
        </div>
    </div>
  </div>
</template>
