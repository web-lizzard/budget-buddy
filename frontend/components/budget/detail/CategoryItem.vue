<script setup lang="ts">
import type { CategoryListItemViewModel } from '@/types/viewmodels'
import { Button } from '@/components/ui/button'
import LimitProgressBar from '@/components/ui/LimitProgressBar.vue'
import { formatCurrency } from '@/utils/currency'
import { AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion'
import { PenSquare, Trash2 } from 'lucide-vue-next' // Icons

const props = defineProps<{
    category: CategoryListItemViewModel
}>()

const emit = defineEmits<{
    (e: 'edit-category' | 'remove-category', categoryId: string): void
}>()

const handleEdit = () => {
    emit('edit-category', props.category.id)
}

const handleRemove = () => {
    emit('remove-category', props.category.id)
}

const currentBalance = computed(() => formatCurrency(props.category.currentBalance))
const usedLimit = computed(() => formatCurrency(props.category.usedLimit))

</script>

<template>
  <AccordionItem :value="category.id">
    <AccordionTrigger>
        <div class="flex justify-between items-center w-full pr-4">
             <span class="font-medium text-left">{{ category.name }}</span>
             <span class="text-muted-foreground text-sm">{{ category.limit.amount}}</span>
        </div>
    </AccordionTrigger>
    <AccordionContent>
        <div class="px-4 pb-4 space-y-4">
            <LimitProgressBar
                :current-value="category.usedLimit?.amount"
                :limit-value="category.limit?.amount"
                :currency="category.limit?.currency"
                label="Limit Usage"
            />

            <div class="grid grid-cols-2 gap-2 text-sm text-muted-foreground">
                <div v-if="category.currentBalance">
                    <span>Current Balance:</span>
                    <span class="font-medium ml-1">{{ currentBalance }}</span>
                </div>
                 <div v-if="category.usedLimit">
                    <span>Total Spent:</span>
                    <span class="font-medium ml-1">{{ usedLimit }}</span>
                </div>
            </div>

            <div class="flex justify-end space-x-2 mt-2">
                <Button variant="outline" size="sm" @click="handleEdit">
                    <PenSquare class="h-4 w-4 mr-1" /> Edit
                </Button>
                <Button variant="destructive" size="sm" @click="handleRemove">
                     <Trash2 class="h-4 w-4 mr-1" /> Remove
                </Button>
            </div>
        </div>
    </AccordionContent>
  </AccordionItem>
</template>
