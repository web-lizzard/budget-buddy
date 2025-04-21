
# User Stories for the Budget Management System

## Budget Management

**US-001**: As a user, I want to create a new budget so I can manage my finances within a specified time frame.

- I can specify the total budget limit
- I can specify the currency of the budget
- I can choose a time strategy for the budget (e.g., monthly, yearly)
- I can set the start date of the budget
- I can add categories (bulk)

**US-002**: As a user, I want to view a list of my budgets so that I have an overview of my finances.

- I can see active budgets
- I can see expired budgets
- I can see the total limit and current usage of each budget

**US-003**: As a user, I want to deactivate a budget to stop its automatic renewal.

- After deactivation, I can still add transactions dated before deactivation
- The system will not automatically create a new budget after expiration

## Category Management

**US-004**: As a user, I want to add categories to my budget so I can better organize my expenses.

- I can specify a category name (unique within the budget)
- I can specify a limit for the category (not exceeding the total budget limit)
- The system ensures the total category limits do not exceed the budget limit
- I can add up to 5 categories per budget

**US-005**: As a user, I want to edit existing categories so I can adjust fund allocation according to changing needs.

- I can change the category name
- I can change the limit assigned to the category

**US-006**: As a user, I want to remove categories from the budget when they are no longer needed.

- I can choose how to handle existing transactions (delete or move to another category)

## Transaction Management

**US-007**: As a user, I want to add transactions to categories in my budget to track my expenses and income.

- I can specify the transaction amount
- I can choose the transaction type (Expense or Income)
- I can specify the transaction date
- The system verifies if the transaction currency matches the budget currency
- The system verifies if the transaction date is within the budget's active period

**US-008**: As a user, I want to edit existing transactions so I can correct any errors.

- I can change the transaction amount
- I can change the transaction category
- I can change the transaction date
- I can change the transaction type

**US-009**: As a user, I want to delete transactions to correct incorrect entries.

- After deleting a transaction, the system updates the budget and category statistics

## Viewing Statistics and Reports

**US-010**: As a user, I want to view budget and category statistics so I can analyze my financial situation.

- I can check the current balance of the budget and each category
- I can check how much I can spend daily without exceeding the limit
- I can check average daily spending for the budget and individual categories

**US-011**: As a user, I want to receive notifications about limit exceedances so I can quickly respond to financial issues.

- The system notifies me when a category limit is exceeded
- The system notifies me when the total budget limit is exceeded

## Budget Automation

**US-012**: As a user, I want the system to automatically create a new budget after the current one ends so I can continuously manage my finances.

- The new budget should be created based on the strategy defined in the previous one
- Categories from the previous budget should be copied to the new one with their limits
- Transactions should not be copied to the new budget
- Automatic creation should not happen for deactivated budgets

**US-013**: As a user, I want to be able to add transactions to expired budgets (before deactivation or end date) to enter late entries.

- I can add a transaction dated earlier than the budget's end date
- The system updates the statistics after adding such a transaction
