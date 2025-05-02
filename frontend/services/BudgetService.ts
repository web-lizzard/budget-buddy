import { $fetch } from 'ofetch';
import { z } from 'zod';
import { apiConfig, mapToDomainError } from '@/utils/apiUtils';
import type { Budget } from '@/types/budget';
import type { BudgetStatistics } from '@/types/statistics';
import type { CreateBudgetRequestPayload, BudgetDTO, BudgetStatisticsDTO, DomainError, CategoryStatisticsDTO, CategoryDTO, PaginatedItems } from '@/types/dtos';
import { BudgetSchema } from '@/schemas/budgetSchema';
import { BudgetStatisticsSchema } from '@/schemas/statisticsSchema';

// Define the shape returned by the createBudget API call (example)
const CreateBudgetResponseSchema = z.object({
  id: z.string(),
});

const PaginatedBudgetSchema = z.object({
  items: z.array(BudgetSchema),
  total: z.number(),
  skip: z.number(),
  limit: z.number(),
});

/**
 * Service class responsible for interacting with Budget-related API endpoints.
 * Must be instantiated.
 */
export class BudgetService {
  /**
   * Fetches details for a specific budget.
   * @param budgetId - The ID of the budget.
   * @returns The budget details (domain model).
   * @throws {DomainError} If the API call fails or data validation fails.
   */
  async getBudgetById(budgetId: string): Promise<Budget> {
    try {
      const url = `${apiConfig.baseURL}/budgets/${budgetId}`;
      const rawData = await $fetch<BudgetDTO>(url, { responseType: 'json', ...apiConfig.commonOptions });
      const parsed = BudgetSchema.safeParse(rawData);

      if (!parsed.success) {
        console.error('Failed to parse budget data:', parsed.error);
        throw { status: 'validation_error', message: 'Invalid API response format for budget.' } as DomainError;
      }
      const dto = parsed.data;
      return {
        id: dto.id,
        userId: dto.user_id,
        name: dto.name,
        totalLimit: dto.total_limit,
        currency: dto.currency,
        startDate: dto.start_date,
        endDate: dto.end_date,
        deactivationDate: dto.deactivation_date,
        categories: dto.categories.map((catDto: CategoryDTO) => ({
          id: catDto.id,
          name: catDto.name,
          limit: catDto.limit,
        })),
        isActive: !dto.deactivation_date,
      };
    } catch (error: unknown) {
       if (error && typeof error === 'object' && 'status' in error && 'message' in error) {
         throw error as DomainError;
       }
       throw mapToDomainError(error, `Failed to fetch budget ${budgetId}`);
    }
  }

  /**
   * Fetches statistics for a specific budget.
   * @param budgetId - The ID of the budget.
   * @returns The budget statistics (domain model), or null if not found (404).
   * @throws {DomainError} If the API call fails (excluding 404) or data validation fails.
   */
  async getBudgetStatistics(budgetId: string): Promise<BudgetStatistics | null> {
     const url = `${apiConfig.baseURL}/budgets/${budgetId}/statistics`;
    try {
      const rawData = await $fetch<BudgetStatisticsDTO>(url, { responseType: 'json', ...apiConfig.commonOptions });
      const parsed = BudgetStatisticsSchema.safeParse(rawData);

       if (!parsed.success) {
         console.error('Failed to parse budget statistics:', parsed.error);
         throw { status: 'validation_error', message: 'Invalid API response format for budget statistics.' } as DomainError;
       }
       const dto = parsed.data;
       return {
           currentBalance: dto.current_balance,
           dailyAvailableAmount: dto.daily_available_amount,
           dailyAverage: dto.daily_average,
           usedLimit: dto.used_limit,
           categoriesStatistics: dto.categories_statistics.map((csDto: CategoryStatisticsDTO) => ({
               categoryId: csDto.category_id,
               currentBalance: csDto.current_balance,
               dailyAvailableAmount: csDto.daily_available_amount,
               dailyAverage: csDto.daily_average,
               usedLimit: csDto.used_limit,
           })),
       };
    } catch (error: unknown) {
       if (error && typeof error === 'object' && 'status' in error && 'message' in error) {
         if ((error as DomainError).status === 'budget_not_found' || (error as DomainError).status === 'statistics_record_not_found' ) {
             console.warn(`Statistics not found for budget ${budgetId} (status: ${(error as DomainError).status}). Returning null.`);
             return null;
         }
         throw error as DomainError;
       }
       const domainError = mapToDomainError(error, `Failed to fetch statistics for budget ${budgetId}`);
       if (domainError.status === 'budget_not_found' || domainError.status === 'statistics_record_not_found') {
           console.warn(`Statistics not found for budget ${budgetId} (mapped status: ${domainError.status}). Returning null.`);
           return null;
       }
       throw domainError;
    }
  }

  /**
   * Creates a new budget.
   * @param payload - The data for the new budget (conforming to CreateBudgetRequestPayload DTO).
   * @returns The ID of the newly created budget.
   * @throws {DomainError} If the API call fails or validation fails.
   */
  async createBudget(payload: CreateBudgetRequestPayload): Promise<void> {
     try {
         const url = `${apiConfig.baseURL}/budgets`;
         const response = await $fetch<unknown>(url, {
             method: 'POST',
             body: payload,
             responseType: 'json',
             ...apiConfig.commonOptions,
         });

         const parsedResponse = CreateBudgetResponseSchema.safeParse(response);
         if (!parsedResponse.success) {
            console.error('Failed to parse create budget response:', parsedResponse.error, response);
            throw { status: 'validation_error', message: 'Invalid API response after creating budget.' } as DomainError;
         }

     } catch (error: unknown) {
        if (error && typeof error === 'object' && 'status' in error && 'message' in error) {
            throw error as DomainError;
        }
         throw mapToDomainError(error, 'Failed to create budget');
     }
   }
  /**
   * Fetches a list of budgets.
   * @returns A paginated response containing budgets (domain models).
   * @throws {DomainError} If the API call fails or data validation fails.
   */
  async listBudgets(): Promise<PaginatedItems<Budget>> {
      try {
          const url = `${apiConfig.baseURL}/budgets`;
          const response = await $fetch<unknown>(url, {
              method: 'GET',
              responseType: 'json',
              ...apiConfig.commonOptions,
          });

          const parsedResponse = PaginatedBudgetSchema.safeParse(response);
          if (!parsedResponse.success) {
              console.error('Failed to parse list budgets response:', parsedResponse.error, response);
              throw { status: 'validation_error', message: 'Invalid API response while fetching budgets.' } as DomainError;
          }

          const domainItems = parsedResponse.data.items.map(budgetDto => ({
              id: budgetDto.id,
              name: budgetDto.name,
              totalLimit: {
                  amount: budgetDto.total_limit.amount,
                  currency: budgetDto.total_limit.currency,
              },
              userId: budgetDto.user_id,
              startDate: budgetDto.start_date,
              endDate: budgetDto.end_date,
              currency: budgetDto.currency,
              categories: budgetDto.categories, // Assuming categories is part of the budget DTO
              isActive: !budgetDto.deactivation_date, // Assuming isActive is part of the budget DTO
          }));

          return {
              items: domainItems,
              total: parsedResponse.data.total,
              skip: parsedResponse.data.skip,
              limit: parsedResponse.data.limit,
          };
      } catch (error: unknown) {
          if (error && typeof error === 'object' && 'status' in error && 'message' in error) {
              throw error as DomainError;
          }
          throw mapToDomainError(error, 'Failed to fetch budgets');
      }
  }

  // TODO: Add instance methods for updateBudget, deleteBudget, listBudgets etc. as needed
}
