import type { CreateTransactionPayload, UpdateTransactionPayload } from '@/types/transaction';
import { $fetch, FetchError } from 'ofetch';

// Helper function to handle potential FetchError and extract message
function handleApiError(error: unknown): string {
    if (error instanceof FetchError) {
        // Try to get error message from response data, fallback to status text or generic message
        return error.data?.message || error.statusText || error.message || 'An unexpected API error occurred.';
    }
    if (error instanceof Error) {
        return error.message;
    }
    return 'An unknown error occurred.';
}

export function useTransactionApi(budgetId: MaybeRef<string>) {
    const id = toValue(budgetId); // Get the actual budget ID value

    // Base URL for the transaction endpoints for this specific budget
    const baseUrl = `/api/budgets/${id}/transactions`;

    /**
     * Creates a new transaction for the budget.
     * @param payload - The data for the new transaction.
     * @throws {Error} If the API call fails.
     */
    async function createTransaction(payload: CreateTransactionPayload): Promise<void> {
        try {
            await $fetch(baseUrl, {
                method: 'POST',
                body: payload,
            });
        } catch (error) {
            const errorMessage = handleApiError(error);
            throw new Error(`Failed to create transaction: ${errorMessage}`);
        }
    }

    /**
     * Updates an existing transaction.
     * @param transactionId - The ID of the transaction to update.
     * @param payload - The updated data for the transaction.
     * @throws {Error} If the API call fails.
     */
    async function updateTransaction(transactionId: string, payload: UpdateTransactionPayload): Promise<void> {
        const url = `${baseUrl}/${transactionId}`;
        try {
            await $fetch(url, {
                method: 'PUT',
                body: payload,
            });
            // PUT usually returns 200 OK with no body
        } catch (error) {
            const errorMessage = handleApiError(error);
            console.error(`Failed to update transaction ${transactionId}:`, errorMessage, error);
            throw new Error(`Failed to update transaction: ${errorMessage}`);
        }
    }

    return {
        createTransaction,
        updateTransaction,
    };
}
