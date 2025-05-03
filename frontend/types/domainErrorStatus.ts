/**
 * Represents the possible domain error statuses derived from backend exceptions.
 * These values should correspond to the snake_case representation of the
 * backend DomainError subclass names (without the 'Error' suffix).
 */
export type DomainErrorStatus =
  | 'budget_not_found'
  | 'budget_name_too_short'
  | 'budget_name_too_long'
  | 'empty_budget_name'
  | 'cannot_renew_deactivated_budget'
  | 'category_not_found'
  | 'category_limit_exceeds_budget'
  | 'category_name_too_long'
  | 'category_name_too_short'
  | 'duplicate_category_name'
  | 'empty_category_name'
  | 'max_categories_reached'
  | 'limit_error' // Generic limit error
  | 'money_error' // Generic money error
  | 'cannot_add_transaction_to_deactivated_budget'
  | 'transaction_not_found'
  | 'transaction_outside_budget_period'
  | 'transaction_transfer_policy'
  | 'statistics_record_not_found'
  | 'budget_strategy' // Generic strategy error
  | 'not_compatible_version'
  // Add other potential statuses based on backend exceptions
  | 'unknown_domain_error' // Fallback for unrecognized domain errors
  | 'network_error' // For errors before reaching the API (e.g., DNS, CORS)
  | 'validation_error' // For client-side or unexpected API response validation errors
  | 'internal_server_error'; // Generic fallback for 5xx errors without specific domain info

// You can create a helper function or type guard if needed
export function isDomainErrorStatus(status: string): status is DomainErrorStatus {
  const knownStatuses: DomainErrorStatus[] = [
    'budget_not_found', 'budget_name_too_short', 'budget_name_too_long', 'empty_budget_name',
    'cannot_renew_deactivated_budget', 'category_not_found', 'category_limit_exceeds_budget',
    'category_name_too_long', 'category_name_too_short', 'duplicate_category_name',
    'empty_category_name', 'max_categories_reached', 'limit_error', 'money_error',
    'cannot_add_transaction_to_deactivated_budget', 'transaction_not_found',
    'transaction_outside_budget_period', 'transaction_transfer_policy',
    'statistics_record_not_found', 'budget_strategy', 'not_compatible_version',
    'unknown_domain_error', 'network_error', 'validation_error', 'internal_server_error',
  ];
  return knownStatuses.includes(status as DomainErrorStatus);
}
