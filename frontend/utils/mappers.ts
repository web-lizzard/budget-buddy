import type { BudgetFormInput } from "@/schemas/createBudgetSchemas";
import type {
    CreateBudgetRequestPayload,
    CreateCategoryRequestPayload,
    MoneyPayload,
    StrategyPayload
} from "~/types/api"; // Assuming API types are defined here
import { formatDateToYYYYMMDD } from "@/utils/dateHelpers";

/**
 * Maps the validated form input data (BudgetFormInput) to the API request payload (CreateBudgetRequestPayload).
 * It first parses the input data using the Zod schema to get the transformed data (BudgetFormData)
 * with correct Date objects, then maps it to the API structure.
 *
 * @param formData - The raw, validated input data from the form (BudgetFormInput).
 * @returns The mapped CreateBudgetRequestPayload object, or null if parsing fails.
 */
export const mapBudgetFormToRequestPayload = (
    formData: BudgetFormInput
): CreateBudgetRequestPayload | null => {
    try {

        // 2. Map the validated and transformed data to the API payload structure
        const totalLimitPayload: MoneyPayload = {
            // Ensure totalLimit is not null before accessing it, though schema should guarantee positivity
            amount: formData.totalLimit ?? 0, // Default to 0 if null, though validation should prevent this
            currency: formData.currency,
        };

        const categoriesPayload: CreateCategoryRequestPayload[] = (formData.categories ?? []).map(cat => ({
            name: cat.name,
            limit: {
                amount: cat.limit, // categorySchema ensures this is a positive number
                currency: formData.currency, // Use the main budget currency
            } as MoneyPayload,
        }));

        const strategyPayload: StrategyPayload = {
            budget_strategy_type: formData.strategyType,
            // parameters: {} // Add parameters if needed in the future
        };

        const requestPayload: CreateBudgetRequestPayload = {
            name: formData.name,
            total_limit: totalLimitPayload,
            start_date: formatDateToYYYYMMDD(formData.startDate),
            categories: categoriesPayload,
            strategy: strategyPayload,
        };

        // Basic validation for formatted dates (should not be empty if Date was valid)
        if (!requestPayload.start_date) {
             console.error("Mapping error: Start date could not be formatted.");
             return null;
        }

        return requestPayload;

    } catch (error) {
        console.error("Error parsing or mapping form data:", error);
        return null; // Return null if Zod parsing fails
    }
};
