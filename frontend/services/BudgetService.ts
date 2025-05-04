import { $fetch } from 'ofetch';
import { z } from 'zod';
import { apiConfig, mapToDomainError } from '@/utils/apiUtils';
import type { Budget } from '@/types/budget';
import type { BudgetStatistics } from '@/types/statistics';
import type { CreateBudgetRequestPayload, BudgetDTO, BudgetStatisticsDTO, DomainError, CategoryStatisticsDTO, CategoryDTO, PaginatedItems, CreateCategoryRequestPayload, UpdateCategoryRequestPayload } from '@/types/dtos';
import { BudgetSchema } from '@/schemas/budgetSchema';
import { BudgetStatisticsSchema } from '@/schemas/statisticsSchema';


const PaginatedBudgetDTOSchema = z.object({
  items: z.array(BudgetSchema),
  total: z.number(),
  skip: z.number(),
  limit: z.number(),
});
interface ListBudgetsParams {
    page?: number;
    limit?: number;
    status?: 'active' | 'inactive' | 'expired' | 'all';
    sort?: string;
}

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
           creationDate: new Date(dto.creation_date),
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
        const url = `${apiConfig.baseURL}/budgets/`;
        await $fetch<unknown>(url, {
             method: 'POST',
             body: payload,
             responseType: 'json',
             ...apiConfig.commonOptions,
         });
     } catch (error: unknown) {
        if (error && typeof error === 'object' && 'status' in error && 'message' in error) {
            throw error as DomainError;
        }
         throw mapToDomainError(error, 'Failed to create budget');
     }
   }

   /**
    * Fetches a list of budgets with pagination, filtering, and sorting.
    * @param params - Parameters for pagination, filtering, and sorting.
    * @returns A paginated response containing budgets (domain models).
    * @throws {DomainError} If the API call fails or data validation fails.
    */
   async listBudgets(params: ListBudgetsParams = {}): Promise<PaginatedItems<Budget>> {
       try {
           const url = `${apiConfig.baseURL}/budgets/`; // Added trailing slash
           // Prepare query parameters, omitting undefined values and handling 'all' status
           const queryParams: Record<string, string | number> = {};
           if (params.page) queryParams.page = params.page;
           if (params.limit) queryParams.limit = params.limit;
           if (params.status && params.status !== 'all') queryParams.status = params.status;
           if (params.sort) queryParams.sort = params.sort;

           const response = await $fetch<unknown>(url, {
               method: 'GET',
               responseType: 'json',
               params: queryParams, // Pass prepared query parameters
               ...apiConfig.commonOptions,
           });

           // Validate the structure of the paginated response
           const parsedResponse = PaginatedBudgetDTOSchema.safeParse(response);
           if (!parsedResponse.success) {
               console.error('Failed to parse list budgets response:', parsedResponse.error, response);
               throw { status: 'validation_error', message: 'Invalid API response while fetching budgets.' } as DomainError;
           }

           // Map DTO items to Domain Model items
           const domainItems = parsedResponse.data.items.map(budgetDto => ({
               id: budgetDto.id,
               userId: budgetDto.user_id,
               name: budgetDto.name,
               totalLimit: budgetDto.total_limit,
               currency: budgetDto.currency,
               startDate: budgetDto.start_date,
               endDate: budgetDto.end_date,
               deactivationDate: budgetDto.deactivation_date,
               categories: budgetDto.categories.map((catDto: CategoryDTO) => ({
                 id: catDto.id,
                 name: catDto.name,
                 limit: catDto.limit,
               })),
               isActive: !budgetDto.deactivation_date,
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

   /**
    * Deactivate a budget by its ID.
    * @param budgetId - The ID of the budget to deactivate.
    * @throws {DomainError} If the API call fails or data validation fails.
    */
   async deactivateBudget(budgetId: string): Promise<void> {
       try {
           const url = `${apiConfig.baseURL}/budgets/${budgetId}/deactivate`;
           await $fetch(url, {
               method: 'PATCH',
               responseType: 'json',
               ...apiConfig.commonOptions,
           });
       } catch (error: unknown) {
           if (error && typeof error === 'object' && 'status' in error && 'message' in error) {
               throw error as DomainError;
           }
           throw mapToDomainError(error, 'Failed to deactivate budget');
       }
   }
  /**
   * Renew a budget by its ID.
   * @param budgetId - The ID of the budget to renew.
   * @throws {DomainError} If the API call fails or data validation fails.
   */
  async renewBudget(budgetId: string): Promise<void> {
      try {
          const url = `${apiConfig.baseURL}/budgets/${budgetId}/renew`;
          await $fetch(url, {
              method: 'POST',
              responseType: 'json',
              ...apiConfig.commonOptions,
          });
      } catch (error: unknown) {
          if (error && typeof error === 'object' && 'status' in error && 'message' in error) {
              throw error as DomainError;
          }
          throw mapToDomainError(error, 'Failed to renew budget');
      }
  }

  /**
   * Creates a new category within a budget.
   * @param budgetId - The ID of the budget to add the category to.
   * @param payload - The data for the new category (conforming to CreateCategoryRequestPayload DTO).
   * @throws {DomainError} If the API call fails or validation fails.
   */
  async createCategory(budgetId: string, payload: CreateCategoryRequestPayload): Promise<void> {
     try {
        const url = `${apiConfig.baseURL}/budgets/${budgetId}/categories`;
        await $fetch<unknown>(url, {
             method: 'POST',
             body: payload,
             responseType: 'json',
             ...apiConfig.commonOptions,
         });
     } catch (error: unknown) {
        if (error && typeof error === 'object' && 'status' in error && 'message' in error) {
            throw error as DomainError;
        }
         throw mapToDomainError(error, 'Failed to create category');
     }
   }

   /**
    * Updates an existing category within a budget.
    * @param budgetId - The ID of the budget containing the category.
    * @param categoryId - The ID of the category to update.
    * @param payload - The data to update in the category (conforming to UpdateCategoryRequestPayload DTO).
    * @throws {DomainError} If the API call fails or validation fails.
    */
   async updateCategory(budgetId: string, categoryId: string, payload: UpdateCategoryRequestPayload): Promise<void> {
       try {
           const url = `${apiConfig.baseURL}/budgets/${budgetId}/categories/${categoryId}`;
           await $fetch<unknown>(url, {
               method: 'PUT',
               body: payload,
               responseType: 'json',
               ...apiConfig.commonOptions,
           });
       } catch (error: unknown) {
           if (error && typeof error === 'object' && 'status' in error && 'message' in error) {
               throw error as DomainError;
           }
           throw mapToDomainError(error, 'Failed to update category');
       }
   }

  // TODO: Add instance methods for updateBudget, deleteBudget etc. as needed
}
