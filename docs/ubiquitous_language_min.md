# Domain Model - Minimal Version of the Budget Management Application

This document outlines only the aggregates, entities, and value objects with their attributes in the application domain. Methods and operational details are excluded.

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

### Transaction

**Attributes:**
- ID (UUID)
- CategoryId (UUID) - associated category identifier
- Amount (Money) - transaction amount
- TransactionType (TransactionType) - type of transaction (Income/Expense)
- OccurredDate (DateTime) - transaction date and time
- Description (String, optional) - transaction description
- UserId (UUID) - identifier of the user associated with the transaction

## Entities

### Category

**Attributes:**
- ID (UUID)
- BudgetId (UUID)
- Name (CategoryName) - category name
- Limit (Limit) - spending limit for the category

### StatisticsRecord

**Attributes:**
- ID (UUID)
- BudgetId (UUID)
- CategoryId (UUID)
- CreationDate (DateTime) - record creation date
- CurrentBalance (Money) - current balance amount
- DailyAvailableAmount (Money) - available daily amount
- DailyAverage (Money) - daily average expenditure

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

### CategoryName

**Attributes:**
- Value (String) - validated category name
