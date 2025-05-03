<script setup lang="ts">
import { computed } from 'vue'
import { format } from 'date-fns'
import type { TransactionViewModel } from '~/types/viewmodels'
import { formatCurrency } from '~/utils/currency'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "~/components/ui/table"
import { Button } from "~/components/ui/button"

const props = defineProps<{
  transactions: TransactionViewModel[]
  budgetId: string
}>()
const router = useRouter()

const hasTransactions = computed(() => props.transactions && props.transactions.length > 0)

const formatDate = (date: Date) => {
  return format(date, 'PP')
}

const amountClass = (type: TransactionViewModel['type']) => {
  return type === 'INCOME' ? 'text-green-600' : 'text-red-600'
}


const viewAllTransactions = () => {
    router.push(`/budgets/${props.budgetId}/transactions`);
}

</script>

<template>
  <Card class="mb-4">
    <CardHeader>
      <CardTitle>Recent Activity</CardTitle>
    </CardHeader>
    <CardContent>
        <Table v-if="hasTransactions">
        <!-- <TableCaption>A list of the last 3 transactions.</TableCaption> -->
        <TableHeader>
            <TableRow>
            <TableHead class="w-[120px]">Date</TableHead>
            <TableHead>Category</TableHead>
            <TableHead>Type</TableHead>
            <TableHead class="text-right">Amount</TableHead>
            </TableRow>
        </TableHeader>
        <TableBody>
            <TableRow v-for="transaction in transactions" :key="transaction.id">
            <TableCell class="font-medium">{{ formatDate(transaction.date) }}</TableCell>
            <TableCell>{{ transaction.categoryName }}</TableCell>
            <TableCell>{{ transaction.type }}</TableCell>
            <TableCell :class="[amountClass(transaction.type), 'text-right font-medium']">
                {{ formatCurrency(transaction.amount) }}
            </TableCell>
            </TableRow>
        </TableBody>
        </Table>
       <div v-else class="text-center text-muted-foreground py-5">
            <p>No recent transactions found.</p>
       </div>
    </CardContent>
    <CardFooter class="flex justify-end">
         <Button variant="outline" size="sm" @click="viewAllTransactions">
            View All Transactions
        </Button>
    </CardFooter>
  </Card>
</template>

<style scoped>
/* Add any specific styles */
</style>
