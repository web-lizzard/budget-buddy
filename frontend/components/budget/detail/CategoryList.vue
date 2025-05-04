<script setup lang="ts">
import type { CategoryListItemViewModel } from '@/types/viewmodels'
import CategoryItem from './CategoryItem.vue'
import { Accordion } from '@/components/ui/accordion'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

const props = defineProps<{
    categories: CategoryListItemViewModel[]
}>()

const emit = defineEmits<{
    (e: 'edit-category' | 'remove-category', categoryId: string): void
    (e: 'create-category'): void
}>()

const handleEdit = (categoryId: string) => {
    emit('edit-category', categoryId)
}

const handleRemove = (categoryId: string) => {
    emit('remove-category', categoryId)
}

const handleAddCategory = () => {
    emit('create-category')
}

const hasCategories = computed(() => props.categories && props.categories.length > 0)

</script>

<template>
 <Card>
    <CardHeader>
      <CardTitle>Categories</CardTitle>
    </CardHeader>
    <CardContent>
        <Accordion v-if="hasCategories" type="single" collapsible class="w-full">
            <CategoryItem
                v-for="category in categories"
                :key="category.id"
                :category="category"
                @edit-category="handleEdit"
                @remove-category="handleRemove"
            />
        </Accordion>
        <div v-else class="text-center text-muted-foreground py-5">
            <p>No categories found for this budget.</p>
            <!-- Optional: Add button to add a category -->
        </div>
    </CardContent>
    <CardFooter>
        <Button @click="handleAddCategory">Add Category</Button>
    </CardFooter>
 </Card>
</template>
