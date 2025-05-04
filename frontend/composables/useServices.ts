import { BudgetService } from "~/services/BudgetService"
import { TransactionService} from "@/services/TransactionService"

export const useBudgetService = () => {

    const service = new BudgetService()

    return {
        service
    }
}

export const useTransactionService = () => {
    const route = useRoute()

    const budgetId = computed(() => route.params.budget)

    const service = new TransactionService(budgetId.value as string)

    return {
        service
    }
}
