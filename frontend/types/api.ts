/**
 * Represents a monetary amount with its currency.
 * Used in API request payloads.
 */
export interface MoneyPayload {
    amount: number;   // Amount as a number (e.g., 100.50)
    currency: string; // Currency code (e.g., 'PLN', 'USD')
}

/**
 * Represents the budget strategy type for API requests.
 */
export interface StrategyPayload {
    budget_strategy_type: 'monthly' | 'yearly';
    parameters?: Record<string, unknown>; // Use unknown instead of any
}

/**
 * Represents a category to be created within a budget request.
 */
export interface CreateCategoryRequestPayload {
    name: string;
    limit: MoneyPayload;
}

/**
 * Main payload structure for the POST /api/budgets request.
 */
export interface CreateBudgetRequestPayload {
    name: string;                 // Budget name (3-100 chars)
    total_limit: MoneyPayload;    // Overall budget limit
    start_date: string;           // Start date formatted as 'YYYY-MM-DD'
    categories: CreateCategoryRequestPayload[]; // List of categories (max 5)
    strategy: StrategyPayload;
}
