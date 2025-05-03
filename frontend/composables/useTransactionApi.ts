import { computed, type MaybeRef, unref } from 'vue';
import { useCommand } from '@/composables/useCommand';
import { TransactionService } from '@/services/TransactionService';
// Import correct payload types from dtos
import type { CreateTransactionPayload, UpdateTransactionPayload } from '@/types/dtos';

// Type for the update command payload, combining ID and data
interface UpdateCommandPayload {
    transactionId: string;
    payload: UpdateTransactionPayload;
}

export function useTransactionApi(budgetId: MaybeRef<string>) {
    const unreffedBudgetId = computed(() => unref(budgetId));

    // Instantiate service reactively based on budgetId
    const transactionService = computed(() => new TransactionService(unreffedBudgetId.value));

    // --- Command for Creating Transaction ---
    const {
        execute: executeCreate,
        loading: loadingCreate,
        error: errorCreate
    } = useCommand<CreateTransactionPayload>(
        async (payload) => {
            await transactionService.value.createTransaction(payload);
        },
        {
            // Optional: Add onSuccess/onError specific to the composable consumer
        }
    );

    // --- Command for Updating Transaction ---
    const {
        execute: executeUpdate,
        loading: loadingUpdate,
        error: errorUpdate
    } = useCommand<UpdateCommandPayload>(
        async ({ transactionId, payload }) => {
            await transactionService.value.updateTransaction(transactionId, payload);
        },
        {
            // Optional: Add onSuccess/onError
        }
    );

    // --- Command for Deleting Transaction (Example) ---
    const {
        execute: executeDelete,
        loading: loadingDelete,
        error: errorDelete
    } = useCommand<string>( // Payload is the transactionId
        async (transactionId) => {
            await transactionService.value.deleteTransaction(transactionId);
        },
        {
             // Optional: Add onSuccess/onError
        }
    );

    // Combine errors if needed, or let consumer handle individual errors
    const combinedError = computed(() => errorCreate.value || errorUpdate.value || errorDelete.value );

    return {
        createTransaction: executeCreate,
        loadingCreate,
        errorCreate,

        updateTransaction: executeUpdate,
        loadingUpdate,
        errorUpdate,

        deleteTransaction: executeDelete,
        loadingDelete,
        errorDelete,

        // Optional combined error state
        error: combinedError,
    };
}
