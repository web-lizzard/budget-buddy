# Domain Model of the Budget Management Application

This document outlines the core concepts of the application's domain using Domain-Driven Design principles along with robust error handling and clean coding practices. It is maintained to reflect the current state of the domain implementation.

## Aggregates

### Budget
The Budget aggregate represents a user's financial plan for a defined period. It governs overall budgeting operations including category management and transaction validations.

**Attributes:**
- ID (UUID)
- UserId (UUID)
- TotalLimit (Money) – The overall budget limit.
- Currency (String) – Currency used for the budget.
- StartDate (Date) – Budget start date.
- EndDate (Date) – Calculated end date based on the applicable strategy.
- DeactivationDate (Date, optional) – Date when the budget was deactivated.

**Methods:**
- add_category(name: str, limit: Money) -> Category: Adds a new spending category ensuring that the cumulative limits and name uniqueness constraints are met.
- remove_category(category: Category) -> None: Removes an existing category from the budget.
- deactivate_budget() -> None: Deactivates the budget.
- validate_transaction_date(transaction: Transaction) -> bool: Validates if a transaction falls within the defined budget period.
- edit_category(category: Category, new_name: str, new_limit: Money) -> Category: Edits an existing category's details, ensuring uniqueness and that the new limit complies with overall budget constraints.

### Transaction
The Transaction aggregate captures individual financial operations within a budget.

**Attributes:**
- ID (UUID)
- CategoryId (UUID) – An identifier for the associated category.
- Amount (Money) – The transaction amount.
- Type (TransactionType) – Indicates if the transaction is an Expense or Income.
- Date (DateTime) – Timestamp of the transaction.
- Description (Optional String) – Additional details regarding the transaction.

**Methods:**
- Additional behaviors may be implemented to enforce business rules as needed.
- update_transaction(new_amount: Optional[Money], new_date: Optional[DateTime], new_description: Optional[str]) -> None: Updates the transaction's details while ensuring consistency with the associated budget.

### StatisticsRecord
The StatisticsRecord aggregate stores financial statistics resulting from budget operations. It is generated independently and provides an overview of the budget's performance and trends.

**Attributes:**
- ID (UUID)
- BudgetId (UUID) – Identifier for the associated budget.
- CategoryId (UUID) – Identifier for an associated category, if applicable.
- CreationDate (DateTime) – Timestamp when the record was created.
- CurrentBalance (Money) – The current balance after operations.
- DailyAvailableAmount (Money) – The available amount for the day.
- DailyAverage (Money) – The average daily spending or income.
- UsedLimit(Money) - The Used limit from the budget

**Methods:**
- (Additional behaviors may be implemented as necessary to calculate and update statistics.)

## Entities

### Category
Represents a spending category within a budget.

**Attributes:**
- ID (UUID)
- BudgetId (UUID) – Identifier of the associated budget.
- Name (String) – Unique name within the budget.
- Limit (Money) – Assigned spending limit.

**Methods:**
- change_name(new_name: str) -> None: Updates the category's name.
- change_limit(new_limit: Money) -> None: Adjusts the spending limit.

## Value Objects

### Money
Represents a monetary amount in a specific currency.

**Attributes:**
- Amount (int) – The numeric value.
- Currency (String) – The currency code.

**Methods:**
- add(money: Money) -> Money: Returns a Money object representing the summed value.
- subtract(money: Money) -> Money: Returns a Money object representing the difference.
- multiply_by(factor: float) -> Money: Scales the amount by the given factor.
- divide_by(divisor: float) -> Money: Divides the amount while ensuring division safety.
- mint(value: float) -> Money: Instantiates a Money object from a float value.

### TransactionType
Enumeration for transaction types.

**Values:**
- EXPENSE
- INCOME

### BudgetStrategy
Encapsulates the rules for determining a budget's lifecycle.

**Attributes:**
- Type (Enum) – For example, Monthly, Yearly, etc.
- Parameters (dict) – Additional strategy parameters.

### Limit
Represents a spending constraint for a category.

**Attributes:**
- Value (Money) – The maximum allowed spending amount.

**Methods:**
- is_exceeded(current_spending: Money) -> bool: Checks if the spending limit is exceeded.
- remaining_amount(current_spending: Money) -> Money: Computes the remaining allowable amount before reaching the limit.

## Domain Services

### TransactionTransferService
Handles the logic for transferring or deleting transactions when a category is modified (e.g., removed or merged).

**Methods:**
- transfer_transactions(source_category: Category, target_category: Category) -> None: Moves transactions from the source category to the target category.
- delete_transactions(category: Category) -> None: Deletes all transactions associated with the given category.

### StatisticsCalculationService
Calculates statistical data based on transactions. (Note: Implementation is not yet complete.)

**Methods:**
- calculate_statistics(budget, transactions) -> StatisticsRecord: Calculates statistics for a given budget/category.


## Factories

Factories are responsible for creating instances of aggregates and value objects while enforcing invariants and preconditions.

Examples include BudgetFactory and TransactionFactory, which ensure correct instantiation and validation of domain objects.

## Exceptions

Domain exceptions are defined to handle business rule violations and system errors. They provide early error detection, proper error logging, and user-friendly error messages.

Common exceptions include:
- InvalidTransactionException
- BudgetLimitExceededException
- DuplicateCategoryException
- CategoryNotFoundException

## Ports (Interfaces)

Interfaces define contracts for external operations, usually implemented in the infrastructure layer.

### TransactionRepository
Interface for managing transaction persistence.

**Methods:**
- find_by_id(id: UUID, user_id: UUID) -> Transaction
- find_by_budget_id(budget_id: UUID, user_id: UUID) -> List[Transaction]
- save(transaction: Transaction) -> None
- delete(transaction: Transaction) -> None
- delete_bulk(transactions: List[Transaction]) -> None
- save_bulk(transactions: List[Transaction]) -> None

### BudgetRepository
Interface for managing budget persistence.

**Methods:**
- find_by_id(id: UUID, user_id: UUID) -> Budget
- save(budget: Budget) -> None

### StatisticsRepository
Interface for managing statistics records.

**Methods:**
- find_by_id(statistic_id: UUID, user_id: UUID) -> StatisticsRecord
- find_by_budget_id(budget_id: UUID, user_id: UUID) -> List[StatisticsRecord]
- find_by_category_id(category_id: UUID, user_id: UUID) -> List[StatisticsRecord]
- find_by_date_range(start_date: date, end_date: date, user_id: UUID) -> List[StatisticsRecord]
- find_by_budget_id_and_date_range(budget_id: UUID, start_date: date, end_date: date, user_id: UUID) -> List[StatisticsRecord]
- save(statistics_record: StatisticsRecord) -> None

### DomainPublisher
Interface for publishing domain events triggered by changes in aggregates.

**Methods:**
- publish(event: DomainEvent) -> None

## Domain Events

Domain events capture significant state changes within the system and are communicated via the DomainPublisher. They facilitate decoupling and event-driven integrations.

**Events Include:**
- BudgetCreated
- BudgetDeactivated
- CategoryAdded
- CategoryRemoved
- TransactionAdded
- TransactionDeleted
- TransactionsTransferred

## Strategies

Strategies encapsulate the rules that determine the lifecycle of a budget. They handle the computation of start and end dates and can incorporate custom parameters.

Implemented strategies include those managing monthly and yearly budget cycles, ensuring that budgets adhere to predefined durations and transitions.

## Associations

- User → Budget: one-to-many (a user can have multiple budgets).
- Budget → StatisticsRecord Aggregate: one-to-many (a budget can generate multiple statistical records).
- Category → StatisticsRecord Aggregate: one-to-many (a category can be associated with multiple statistical records).
- Budget → Category: one-to-many (a budget can have up to 5 categories).
- Category → Transaction: one-to-many (a category can have many transactions).

## Business Rules

1. Users can only access their own budgets.
2. A budget must have a defined limit and start date.
3. A budget employs a strategy that determines its duration.
4. When a budget period ends, an active budget may trigger the creation of a new budget.
5. A budget can have a maximum of 5 categories.
6. The sum of category spending limits must not exceed the overall budget limit.
7. Category names must be unique within a budget.
8. Transactions may exceed category limits; excessive amounts are logged for review.
9. When a category is deleted, its transactions are either removed or transferred.
10. Each budget operation can generate a statistical record (with statistics entities/services remaining to be fully implemented).
11. Transactions added to a deactivated budget must have dates preceding deactivation.
12. A deactivated budget does not auto-generate subsequent budgets.
13. The currency for transactions must match the budget's currency.
14. Robust error handling, including early returns and proper logging, is implemented throughout the domain.

*This document is continuously updated to mirror the evolution of the domain model, ensuring that aggregates, entities, value objects, services, events, repositories, and strategies remain accurately documented.*
