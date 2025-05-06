import { computed } from 'vue'
import type { Budget } from "~/types/budget"
import type { PaginatedItems } from "~/types/dtos";
import type { Transaction } from "~/types/transaction"

type TransactionsSource = PaginatedItems<Transaction> | Transaction[] | null | undefined;

export const useTransactionsViewModel = (
    transactions: Ref<TransactionsSource>,
    budget: Ref<Budget | null | undefined>
) => {

    const transactionsItems = computed(() => {
        if (!transactions.value) return [];
        if ('items' in transactions.value) {
            return transactions.value.items
        }

        return transactions.value
    })



    const categoryMap = computed(() => {
        if (!budget.value?.categories) return new Map<string, string>();

        const map = new Map<string, string>();
        budget.value.categories.forEach(category => {
            map.set(category.id, category.name);
        });
        return map;
    });


    const transactionViewModels = computed(() => {
        return transactionsItems.value.map(transaction => {
            return {
                id: transaction.id,
                date: new Date(transaction.date),
                categoryName: categoryMap.value.get(transaction.categoryId) || 'Unknown Category',
                type: transaction.type,
                amount: transaction.amount,
            };
        });
    });

    return {
        transactionViewModels,
        categoryMap
    }
}
