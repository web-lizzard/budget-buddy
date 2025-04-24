# Domain Model of the Budget Management Application

## Aggregates

### Budget
The Budget aggregate represents a user's financial plan for a defined period. It governs overall budgeting operations including category management and transaction validations.

**Attributes:**
- ID (UUID)
- UserId (UUID)
- TotalLimit (Money) - The overall budget limit.
- Currency (String) - Currency used for the budget.
- StartDate (Date) - Budget start date.
- EndDate (Date) - Calculated end date based on the applied strategy.
- DeactivationDate (Date, optional) - Date when the budget was deactivated.

**Methods:**
- add_category(name, limit) -> Category: Adds a new spending category ensuring that the cumulative limits and name uniqueness constraints are met.
- remove_category(category) -> None: Removes an existing category from the budget.
- deactivate_budget() -> None: Deactivates the budget.
- validate_transaction_date(transaction) -> bool: Validates if a transaction falls within the defined budget period.

### Transaction
The Transaction aggregate captures individual financial operations within a budget.

**Attributes:**
- ID (UUID)
- CategoryId (UUID) - The identifier of the category associated with the transaction.
- Amount (Money) - The transaction amount.
- Type (TransactionType) - Indicates if the transaction is an Expense or Income.
- Date (DateTime) - Date and time of the transaction.
- Description (String, optional) - Additional details regarding the transaction.

**Methods:**
- (Additional methods can be implemented as necessary to encapsulate behavior.)

## Entities

### Category
Represents a spending category within a budget.

**Attributes:**
- ID (UUID)
- BudgetId (UUID) - The identifier of the associated budget.
- Name (String) - A unique name within the budget.
- Limit (Money) - Spending limit assigned to this category.

**Methods:**
- change_name(new_name) -> None: Updates the category's name.
- change_limit(new_limit) -> None: Adjusts the category's spending limit.

### StatisticsRecord
Stores financial statistics after each operation.

**Attributes:**
- ID (UUID)
- BudgetId (UUID) - The identifier of the associated budget.
- CategoryId (UUID) - The identifier of the associated category.
- CreationDate (DateTime) - Timestamp of record creation.
- CurrentBalance (Money) - The current balance.
- DailyAvailableAmount (Money) - Available amount on a daily basis.
- DailyAverage (Money) - Average daily spending or income.

## Services

### TransactionTransferService
Handles the logic for transferring or deleting transactions when a category is modified (e.g., removed or merged).

**Methods:**
- transfer_transactions(source_category, target_category) -> None: Moves transactions from the source category to the target category.
- delete_transactions(category) -> None: Deletes all transactions associated with the given category.

### StatisticsCalculationService
Calculates statistics based on transactions.

**Methods:**
- calculate_statistics(budget_id, category_id) -> StatisticsRecord: Calculates statistics for a given budget/category.
- calculate_daily_available_amount(budget, category, current_date) -> Money: Determines the daily available amount.

## Ports

### TransactionRepository
Defines the interface for storing and retrieving transaction data from the persistence layer.

**Methods:**
- find_by_id(id) -> Transaction
- find_by_budget_id(budget_id) -> List[Transaction]
- save(transaction) -> None
- delete(transaction) -> None
- delete_bulk(transactions) -> None
- save_bulk(transactions) -> None

### BudgetRepository
Defines the interface for managing budget data.

**Methods:**
- find_by_id(id, user_id) -> Budget
- save(budget) -> None

### StatisticsRepository
Defines the interface for managing statistics records.

**Methods:**
- find_by_budget_id(budget_id) -> List[StatisticsRecord]
- find_by_category_id(category_id) -> List[StatisticsRecord]
- find_by_date_range(start_date, end_date) -> List[StatisticsRecord]
- save(statistics_record) -> None

### DomainPublisher
Provides an interface for publishing domain events triggered by changes in aggregates.

**Methods:**
- publish(event) -> None

## Value Objects

### Money
Represents a monetary amount in a specific currency.

**Attributes:**
- Amount (int) - The numeric value.
- Currency (String) - The currency code.

**Methods:**
- add(money) -> Money: Adds two monetary amounts.
- subtract(money) -> Money: Subtracts one monetary amount from another.
- multiply_by(factor) -> Money: Multiplies the amount by a given factor.
- divide_by(divisor) -> Money: Divides the amount by a divisor.
- mint(value: float) -> Money: Creates a Money instance from a float value.

### TransactionType
Enumeration for transaction types.

**Values:**
- EXPENSE
- INCOME

### BudgetStrategy
Encapsulates the rules determining the lifecycle of a budget.

**Attributes:**
- Type (Enum) - For example, monthly or yearly.
- Parameters (Map<String, Object>) - Additional strategy parameters (e.g., starting day).

**Methods:**
- calculate_end_date(start_date) -> Date: Computes the budget's end date based on the strategy.
- create_next_budget_start_date(end_date) -> Date: Determines the start date for the subsequent budget period.

### Limit
Represents a spending constraint for a category.

**Attributes:**
- Value (Money) - The maximum allowed spending amount.

**Methods:**
- is_exceeded(current_spending) -> bool: Checks if the current spending surpasses the limit.
- remaining_amount(current_spending) -> Money: Calculates the remaining spendable amount before reaching the limit.
- add(limit) -> current_spending: Current spending as Money object
## Domain Events

Domain events capture significant state changes within the system and are communicated via the DomainPublisher.

**Events:**
- BudgetCreated: Triggered when a new budget is established.
- BudgetDeactivated: Triggered when a budget is deactivated.
- CategoryAdded: Triggered upon adding a new category to a budget.
- CategoryRemoved: Triggered when a category is removed from a budget.
- TransactionAdded: Triggered when a new transaction is recorded.
- TransactionDeleted: Triggered when a transaction is removed.
- TransactionsTransferred: Triggered when transactions are moved between categories.

## Associations

1. **User → Budget**: one-to-many (a user can have multiple budgets)
2. **Budget → Category**: one-to-many (a budget can have up to 5 categories)
3. **Category → Transaction**: one-to-many (a category can have many transactions)
4. **Budget → StatisticsRecord**: one-to-many (a budget has many statistical records)
5. **Category → StatisticsRecord**: one-to-many (a category has many statistical records)

## Business Rules

1. Users can only view their own budgets
2. A budget has a limit and a start date
3. A budget has a strategy defining its length
4. When a budget ends, a new one is created automatically (if active)
5. A budget can have a maximum of 5 categories
6. The sum of category limits cannot exceed the budget limit
7. Category names must be unique within a budget
8. Transactions may exceed category limits (the system logs the excess)
9. When deleting a category, either all transactions are deleted or moved to another category
10. Each operation generates a statistical record
11. Transactions can only be added to a deactivated budget if they have a date before deactivation
12. A deactivated budget does not auto-generate a new budget
13. Transaction currency must match the budget currency
