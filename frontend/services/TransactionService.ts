import { $fetch, type FetchOptions } from 'ofetch';
import { z } from 'zod';
import type { CreateTransactionPayload, UpdateTransactionPayload, TransactionDTO, DomainError, PaginatedItems } from '@/types/dtos';
import { TransactionSchema } from '@/schemas/transactionSchema';
import type { Transaction, TransactionType } from '@/types/transaction';
import { mapToDomainError, apiConfig } from '@/utils/apiUtils';

// Define the shape of the paginated response from the API for transactions
const PaginatedTransactionDTOSchema = z.object({
  items: z.array(TransactionSchema),
  total: z.number(),
  skip: z.number(),
  limit: z.number(),
});

// Define the type for pagination/filtering parameters
export interface GetTransactionsParams {
    page: number;
    limit: number;
    sort?: string;
    // Add other potential filters like date_from, date_to if needed later
}

/**
 * Service class responsible for interacting with Transaction-related API endpoints
 * for a specific budget. Requires budgetId upon instantiation.
 */
export class TransactionService {
    private budgetId: string;
    private baseUrl: string;

    constructor(budgetId: string) {
        if (!budgetId) {
            throw new Error('Budget ID must be provided to instantiate TransactionService.');
        }
        this.budgetId = budgetId;
        this.baseUrl = `${apiConfig.baseURL}/budgets/${this.budgetId}/transactions`;
    }

    /**
     * Creates a new transaction for the specified budget.
     * @param payload - Data for the new transaction (expected in API DTO format).
     * @returns The created transaction details (domain model) if returned by API, otherwise null.
     * @throws {DomainError} If the API call fails or validation fails.
     */
    async createTransaction(payload: CreateTransactionPayload): Promise<Transaction | null> {
        try {
            const response = await $fetch<TransactionDTO | null>(this.baseUrl, {
                method: 'POST',
                body: payload,
                responseType: 'json',
                ...apiConfig.getAuthOptions(),
            });

            if (response) {
                 const parsed = TransactionSchema.safeParse(response);
                 if (parsed.success) {
                     const dto = parsed.data;
                     // TODO: Move mapping to TransactionSchema.transform()
                     return {
                         id: dto.id,
                         categoryId: dto.category_id,
                         userId: dto.user_id,
                         amount: dto.amount,
                         type: dto.transaction_type as TransactionType,
                         date: dto.occurred_date,
                         // description: dto.description, // Assuming schema handles optional description potentially
                     };
                 }
                 console.warn('Create transaction response validation failed, but operation might have succeeded.', parsed.error);
                 return null;
            }
            return null;
        } catch (error: unknown) {
            if (error && typeof error === 'object' && 'status' in error && 'message' in error) {
                throw error as DomainError;
            }
            throw mapToDomainError(error, `Failed to create transaction for budget ${this.budgetId}`);
        }
    }

    /**
     * Updates an existing transaction.
     * @param transactionId - The ID of the transaction to update.
     * @param payload - Updated data for the transaction (expected in API DTO format).
     * @throws {DomainError} If the API call fails.
     */
    async updateTransaction(transactionId: string, payload: UpdateTransactionPayload): Promise<void> {
        const url = `${this.baseUrl}/${transactionId}/`;
        try {
            await $fetch(url, {
                method: 'PUT',
                body: payload,
                responseType: 'json',
                ...apiConfig.getAuthOptions(),
            });
        } catch (error: unknown) {
             if (error && typeof error === 'object' && 'status' in error && 'message' in error) {
                throw error as DomainError;
            }
            throw mapToDomainError(error, `Failed to update transaction ${transactionId}`);
        }
    }

    /**
    * Deletes a transaction.
    * @param transactionId - The ID of the transaction to delete.
    * @throws {DomainError} If the API call fails.
    */
   async deleteTransaction(transactionId: string): Promise<void> {
        const url = `${this.baseUrl}/${transactionId}/`;
        try {
            await $fetch(url, {
                method: 'DELETE',
                responseType: 'json',
                ...apiConfig.getAuthOptions(),
            });
        } catch (error: unknown) {
             if (error && typeof error === 'object' && 'status' in error && 'message' in error) {
                throw error as DomainError;
            }
             throw mapToDomainError(error, `Failed to delete transaction ${transactionId}`);
        }
    }

   /**
    * Fetches recent transactions for the specified budget.
    * Maps the paginated DTO response to a paginated Domain model response.
    * @param limit - Maximum number of transactions to fetch.
    * @param sort - Sorting criteria (e.g., 'date:desc').
    * @returns A paginated response containing recent transactions (domain models).
    * @throws {DomainError} If the API call fails or data validation fails.
    */
   async getRecentTransactions(
        limit: number = 3,
        sort: string = '-occurred_date'
    ): Promise<PaginatedItems<Transaction>> {
     try {
        // Use this.baseUrl which already includes the budgetId
        const options: FetchOptions = {
            ...apiConfig.getAuthOptions(),
            params: { limit, sort },
        };
        const rawData = await $fetch<z.infer<typeof PaginatedTransactionDTOSchema>>(this.baseUrl, {
            ...options,
            responseType: 'json',
        });
        const parsed = PaginatedTransactionDTOSchema.safeParse(rawData);

        if (!parsed.success) {
             console.error('Failed to parse recent transactions structure:', parsed.error);
             throw { status: 'validation_error', message: 'Invalid API response format for recent transactions.' } as DomainError;
        }

        // TODO: Move mapping to TransactionSchema.transform()
        const domainItems = parsed.data.items.map(itemDto => ({
            id: itemDto.id,
            categoryId: itemDto.category_id,
            userId: itemDto.user_id,
            amount: itemDto.amount,
            type: itemDto.transaction_type as TransactionType,
            date: itemDto.occurred_date,
            // description: itemDto.description, // Assume handled by schema or not present
        }));

        return {
            items: domainItems,
            total: parsed.data.total,
            skip: parsed.data.skip,
            limit: parsed.data.limit,
        };
     } catch (error: unknown) {
         if (error && typeof error === 'object' && 'status' in error && 'message' in error) {
            throw error as DomainError;
         }
         throw mapToDomainError(error, `Failed to fetch recent transactions for budget ${this.budgetId}`);
     }
  }

   /**
    * Fetches transactions for the specified budget with pagination.
    * Maps the paginated DTO response to a paginated Domain model response.
    * @param params - Pagination and filtering parameters.
    * @returns A paginated response containing transactions (domain models).
    * @throws {DomainError} If the API call fails or data validation fails.
    */
   async getTransactions(
     params: GetTransactionsParams
   ): Promise<PaginatedItems<Transaction>> {
     try {
       const apiParams: Record<string, string | number> = {
         skip: (params.page - 1) * params.limit, // Convert page to skip
         limit: params.limit,
       };
       if (params.sort) {
         apiParams.sort = params.sort;
       }
       // Add other filters here if needed

       const options: FetchOptions<'json'> = {
         ...apiConfig.getAuthOptions(),
         params: apiParams,
         responseType: 'json',
       };

       const rawData = await $fetch<z.infer<typeof PaginatedTransactionDTOSchema>>(this.baseUrl, options);
       const parsed = PaginatedTransactionDTOSchema.safeParse(rawData);

       if (!parsed.success) {
         console.error('Failed to parse transactions structure:', parsed.error);
         throw { status: 'validation_error', message: 'Invalid API response format for transactions.' } as DomainError;
       }

       // TODO: Move mapping to TransactionSchema.transform()
       const domainItems = parsed.data.items.map(itemDto => ({
         id: itemDto.id,
         categoryId: itemDto.category_id,
         userId: itemDto.user_id,
         amount: itemDto.amount,
         type: itemDto.transaction_type as TransactionType,
         date: itemDto.occurred_date,
         // description: itemDto.description, // Assume handled by schema
       }));

       return {
         items: domainItems,
         total: parsed.data.total,
         skip: parsed.data.skip, // Keep skip and limit from API response
         limit: parsed.data.limit,
       };
     } catch (error: unknown) {
       if (error && typeof error === 'object' && 'status' in error && 'message' in error) {
         throw error as DomainError;
       }
       throw mapToDomainError(error, `Failed to fetch transactions for budget ${this.budgetId}`);
     }
   }

    // TODO: Add methods for getTransactionById etc. as needed
}
