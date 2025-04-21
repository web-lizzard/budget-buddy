# Domain Model of the Budget Management Application

## Aggregates

### Budget

The main aggregate representing a user's financial plan for a specified period.

**Attributes:**

- ID (UUID)
- UserId (User ID)
- TotalLimit (Money) - total budget limit
- Currency (String) - budget currency
- StartDate (Date) - budget start date
- EndDate (Date) - budget end date (calculated based on strategy)
- DeactivationDate (Date, optional) - budget deactivation date

**Methods:**

- AddCategory(name, limit) - adds a new category with a limit, checking if the limit doesn't exceed the available budget, if the name is unique, and if the category count doesn't exceed the maximum (5)
- RemoveCategory(Category) - removes a category with a selected transaction transfer policy
- DeactivateBudget() - deactivates the budget
- ValidateTransactionDate(Transaction) - checks if the transaction date is within the budget period

### Transaction

Represents a single financial operation.

**Attributes:**

- ID (UUID)
- CategoryId (Category ID)
- Amount (Money) - transaction amount
- Type (TransactionType) - transaction type (Income/Expense)
- Date (DateTime) - transaction date and time
- Description (String, optional) - transaction description

**Methods:**

- UpdateTransaction(amount, type, date, description) - updates the transaction

## Entities

### Category

Part of the Budget aggregate, representing an area of spending.

**Attributes:**

- ID (UUID)
- BudgetId (Budget ID)
- Name (String) - category name (unique within the budget)
- Limit (Money) - spending limit for the category

**Methods:**

- ChangeName(newName) - changes the category name
- ChangeLimit(newLimit) - changes the category limit

### StatisticsRecord

Stores financial statistics after each operation.

**Attributes:**

- ID (UUID)
- BudgetId (Budget ID)
- CategoryId (Category ID)
- CreationDate (DateTime) - record creation date
- CurrentBalance (Money) - current balance
- DailyAvailableAmount (Money) - available daily amount
- DailyAverage (Money) - daily average for the budget/category

## Value Objects

### BudgetStrategy

Defines rules regarding the budget lifecycle.

**Attributes:**

- Type (Enum) - strategy type (e.g., monthly, yearly)
- Parameters (Map<String, Object>) - strategy parameters (e.g., start day)

**Methods:**

- CalculateEndDate(startDate) - calculates the budget end date
- CreateNextBudgetStartDate(endDate) - calculates the start date for the next budget

### Money

Represents an amount in a specific currency.

**Attributes:**

- Amount (int) - amount value
- Currency (String) - currency code

**Methods:**

- Add(money) - adds the amount
- Subtract(money) - subtracts the amount
- MultiplyBy(factor) - multiplies the amount by a factor
- DivideBy(divisor) - divides the amount by a divisor
- mint(self, float) - static method to create an object from a float

### Limit

Represents a spending limit.

**Attributes:**

- Value (Money) - limit value

**Methods:**

- IsExceeded(currentSpending) - checks if the limit is exceeded
- RemainingAmount(currentSpending) - calculates the remaining amount

### TransactionType

Enum representing transaction types.

**Values:**

- EXPENSE
- INCOME

### TransactionTransferPolicy

Defines how transactions are handled when a category is deleted.

**Values:**

- DELETE_TRANSACTIONS - delete all transactions
- MOVE_TO_OTHER_CATEGORY - move transactions to another category
- CategoryID - for MOVE_TO_OTHER_CATEGORY, the target category ID

## Domain Services

### BudgetRenewalService

Responsible for automatically creating new budgets.

**Methods:**

- RenewBudget(expiredBudget) - creates a new budget based on an expired one
- CopyCategories(sourceBudget, targetBudget) - copies categories from one budget to another

### TransactionCategoryReassignmentService

Manages moving transactions between categories.

**Methods:**

- ReassignTransactions(sourceCategory, targetCategory, budget) - moves transactions from one category to another
- DeleteTransactions(category) - deletes all transactions from a category

### StatisticsCalculationService

Calculates statistics based on transactions.

**Methods:**

- CalculateStatistics(budgetId, categoryId) - calculates statistics for a budget/category
- CalculateDailyAvailableAmount(budget, category, currentDate) - calculates the daily available amount

## Factories

- CreateBudgetFactory - creates a new budget
- CreateTransactionFactory - creates a new transaction

## Repositories

### BudgetRepository

**Methods:**

- FindById(id, user_id)
- Save(budget)

### TransactionRepository

**Methods:**

- FindById(id)
- FindByCategoryId(categoryId)
- FindByBudgetId(budgetId)
- Save(transaction)
- Delete(transaction)

### StatisticsRepository

**Methods:**

- FindByBudgetId(budgetId)
- FindByCategoryId(categoryId)
- FindByDateRange(startDate, endDate)
- Save(statisticsRecord)

## Domain Events

1. **BudgetCreated** - a new budget has been created
    - BudgetId, UserId, TotalLimit, StartDate, Strategy
2. **BudgetExpired** - budget has completed its lifecycle
    - BudgetId, EndDate
3. **BudgetDeactivated** - budget has been deactivated
    - BudgetId, DeactivationDate
4. **CategoryAdded** - a new category has been added
    - CategoryId, BudgetId, Name, Limit
5. **CategoryRemoved** - a category has been removed
    - CategoryId, BudgetId, TransferPolicy
6. **TransactionAdded** - a transaction has been added
    - TransactionId, CategoryId, Amount, Type, Date
7. **TransactionUpdated** - a transaction has been updated
    - TransactionId, CategoryId, Amount, Type, Date
8. **TransactionRemoved** - a transaction has been removed
    - TransactionId, CategoryId
9. **StatisticsUpdated** - statistics have been updated
    - StatisticsId, BudgetId, CategoryId, CurrentBalance, DailyAvailableAmount
10. **BudgetLimitExceeded** - budget limit exceeded
    - BudgetId, CurrentAmount, Limit
11. **CategoryLimitExceeded** - category limit exceeded
    - CategoryId, BudgetId, CurrentAmount, Limit

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