<script setup lang="ts">
import { Button } from '~/components/ui/button'
import { PlusCircle, Ban } from 'lucide-vue-next'

defineProps<{
    budgetId: string
    isActive: boolean
}>()

const emit = defineEmits<{
    (e: 'add-transaction' | 'deactivate-budget'): void
}>()

const handleAddTransaction = () => {
    emit('add-transaction')
}

const handleDeactivateBudget = () => {
    emit('deactivate-budget')
}

</script>

<template>
    <Card>
        <CardHeader>
            <CardTitle>Actions</CardTitle>
        </CardHeader>
        <CardContent class="flex flex-col space-y-2 md:flex-row md:space-y-0 md:space-x-2 justify-end">
            <Button variant="default" @click="handleAddTransaction">
                 <PlusCircle class="h-4 w-4 mr-2" /> Add Transaction
            </Button>
            <Button
                variant="destructive"
                :disabled="!isActive"
                :title="isActive ? 'Deactivate this budget' : 'Budget is already inactive'"
                @click="handleDeactivateBudget"
            >
                 <Ban class="h-4 w-4 mr-2" /> Deactivate Budget
            </Button>
        </CardContent>
    </Card>
</template>

<style scoped>
/* Add any specific styles */
</style>
