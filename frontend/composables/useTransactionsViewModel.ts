import type { Budget } from "~/types/budget"
import type { Transaction } from "~/types/transaction"

export const useTransactionsViewModel = (
    transactions: Transaction[],
    budget: Budget | null
) => {

    const categoryMap = computed(() => {
        if (!budget?.categories) return new Map<string, string>();

        const map = new Map<string, string>();
        budget.categories.forEach(category => {
            map.set(category.id, category.name);
        });
        return map;
    });

    const transactionViewModels = computed(() => {
        if (!transactions) return [];

        return transactions.map(transaction => {
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
