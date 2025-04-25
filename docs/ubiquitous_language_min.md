# Domain Model - Minimal Version of the Budget Management Application

This document outlines the aggregates, entities, value objects, and domain events in the application domain. Methods and operational details are excluded.

## Aggregates

### Budget

**Attributes:**
- ID (UUID)
- UserId (UUID)
- TotalLimit (Limit) - total budget limit
- Currency (String) - budget currency (derived from TotalLimit)
- StartDate (DateTime) - budget start date
- EndDate (DateTime) - budget end date
- DeactivationDate (DateTime, optional) - budget deactivation date
- Categories (List[Category]) - list of budget categories
- Name (BudgetName) - validated name of the budget

### Transaction

**Attributes:**
- ID (UUID)
- CategoryId (UUID) - associated category identifier
- Amount (Money) - transaction amount
- TransactionType (TransactionType) - type of transaction (Income/Expense)
- OccurredDate (DateTime) - transaction date and time
- Description (String, optional) - transaction description
- UserId (UUID) - identifier of the user associated with the transaction

### StatisticsRecord
Represents overall financial statistics for a budget.
**Attributes:**
- ID (UUID)
- UserId (UUID) - Identifier of the user
- BudgetId (UUID)
- CurrentBalance (Money) - Current balance amount across all categories
- DailyAvailableAmount (Money) - Available daily amount for spending
- DailyAverage (Money) - Daily average expenditure
- UsedLimit (Money) - Total amount of limit used
- CreationDate (DateTime) - Record creation date
- CategoriesStatistics (List[CategoryStatisticsRecord]) - Statistics details per category

## Entities

### Category

**Attributes:**
- ID (UUID)
- BudgetId (UUID)
- Name (CategoryName) - category name
- Limit (Limit) - spending limit for the category

### CategoryStatisticsRecord
Statistics specific to a single category within a budget.
**Attributes:**
- ID (UUID)
- CategoryId (UUID)
- CurrentBalance (Money) - Current balance for the category
- DailyAvailableAmount (Money) - Available daily amount for the category
- DailyAverage (Money) - Daily average expenditure in the category
- UsedLimit (Money) - Amount of limit used in the category

## Value Objects

### BudgetStrategy

**Attributes:**
- Type (Enum) - strategy type (e.g., monthly, yearly)
- Parameters (Dict[String, Object]) - strategy parameters (e.g., start day)

### Money

**Attributes:**
- Amount (int) - monetary amount value
- Currency (String) - currency code

### Limit

**Attributes:**
- Value (Money) - limit value

### TransactionType

**Values:**
- EXPENSE
- INCOME

### TransactionTransferPolicy

**Values:**
- DELETE_TRANSACTIONS - delete all transactions
- MOVE_TO_OTHER_CATEGORY - move transactions to another category
- CategoryID - for MOVE_TO_OTHER_CATEGORY, the target category ID

### BudgetName
**Attributes:**
- Value (String) - Validated budget name (must be between 3-100 characters)

### CategoryName

**Attributes:**
- Value (String) - validated category name

## Domain Events

These events represent significant actions or changes within the domain.

### TransactionEditedEvent
Event triggered when a transaction is modified.
**Attributes:**
- TransactionId (UUID)
- ModifiedFields (Dict[String, Any]) – Changes made to the transaction details

### TransactionDeletedEvent
Event triggered when a transaction is deleted.
**Attributes:**
- TransactionId (UUID)
- Reason (String) – Reason for deletion

Additional events for Budget and Category operations may be defined in their respective contexts.
