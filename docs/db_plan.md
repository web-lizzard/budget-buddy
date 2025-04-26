# PostgreSQL Database Schema Plan

This document outlines the database schema for the Budget Buddy application, based on planning sessions, domain models, and API requirements.

## 1. Tables

### `budgets`
Stores information about user budgets.

| Column Name              | Data Type        | Constraints                               | Description                                      |
|--------------------------|------------------|-------------------------------------------|--------------------------------------------------|
| `id`                     | UUID             | PRIMARY KEY                               | Unique identifier for the budget                 |
| `user_id`                | UUID             | NOT NULL                                  | Identifier of the user owning the budget         |
| `name`                   | VARCHAR(100)     | NOT NULL                                  | Name of the budget                               |
| `total_limit_amount`     | INTEGER          | NOT NULL                                  | Total budget limit amount (smallest unit)      |
| `total_limit_currency`   | VARCHAR(3)       | NOT NULL                                  | Currency code for the total limit (ISO 4217)    |
| `strategy_type`          | VARCHAR(10)      | NOT NULL CHECK (strategy_type IN ('monthly', 'yearly')) | Type of budget renewal strategy          |
| `strategy_parameters`    | JSONB            | NULL                                      | Parameters for the chosen strategy (e.g., {'start_day': 1}) |
| `start_date`             | DATE             | NOT NULL                                  | Start date of the budget period                |
| `end_date`               | DATE             | NOT NULL                                  | End date of the budget period                  |
| `deactivation_date`      | DATE             | NULL                                      | Date when the budget was deactivated (soft delete) |
| `version`                | INTEGER          | NOT NULL DEFAULT 1                        | Optimistic locking version counter             |
| `created_at`             | DATE             | NOT NULL DEFAULT CURRENT_DATE             | Date of budget creation                        |
| `updated_at`             | DATE             | NOT NULL DEFAULT CURRENT_DATE             | Date of last budget update                     |

*Note on strategy columns:* `strategy_parameters` structure depends on `strategy_type`. Application enforces consistency.

### `categories`
Stores categories within budgets.

| Column Name      | Data Type   | Constraints                               | Description                                       |
|------------------|-------------|-------------------------------------------|---------------------------------------------------|
| `id`             | UUID        | PRIMARY KEY                               | Unique identifier for the category                |
| `budget_id`      | UUID        | NOT NULL, FOREIGN KEY REFERENCES budgets(id) ON DELETE RESTRICT | Budget this category belongs to                |
| `user_id`        | UUID        | NOT NULL                                  | Identifier of the user owning the category      |
| `name`           | VARCHAR(100)| NOT NULL                                  | Name of the category (unique within budget enforced by app) |
| `limit_amount`   | INTEGER     | NOT NULL                                  | Category spending limit amount (smallest unit)    |
| `limit_currency` | VARCHAR(3)  | NOT NULL                                  | Currency code for the category limit (ISO 4217)   |
| `version`        | INTEGER     | NOT NULL DEFAULT 1                        | Optimistic locking version counter                |
| `created_at`     | DATE        | NOT NULL DEFAULT CURRENT_DATE             | Date of category creation                       |
| `updated_at`     | DATE        | NOT NULL DEFAULT CURRENT_DATE             | Date of last category update                    |

### `transactions`
Stores individual income or expense transactions.

| Column Name        | Data Type   | Constraints                                    | Description                                      |
|--------------------|-------------|------------------------------------------------|--------------------------------------------------|
| `id`               | UUID        | PRIMARY KEY                                    | Unique identifier for the transaction            |
| `category_id`      | UUID        | NOT NULL, FOREIGN KEY REFERENCES categories(id) ON DELETE RESTRICT | Category this transaction belongs to           |
| `user_id`          | UUID        | NOT NULL                                       | Identifier of the user owning the transaction    |
| `amount_amount`    | INTEGER     | NOT NULL                                       | Transaction amount (positive for income, negative for expense - smallest unit) |
| `amount_currency`  | VARCHAR(3)  | NOT NULL                                       | Currency code for the transaction (ISO 4217)      |
| `transaction_type` | VARCHAR(10) | NOT NULL CHECK (transaction_type IN ('INCOME', 'EXPENSE')) | Type of transaction                          |
| `occurred_date`    | DATE        | NOT NULL                                       | Date when the transaction occurred               |
| `description`      | TEXT        | NULL                                           | Optional description for the transaction         |
| `version`          | INTEGER     | NOT NULL DEFAULT 1                             | Optimistic locking version counter               |
| `created_at`       | DATE        | NOT NULL DEFAULT CURRENT_DATE                  | Date of transaction creation                   |
| `updated_at`       | DATE        | NOT NULL DEFAULT CURRENT_DATE                  | Date of last transaction update                |

### `statistics_records`
Stores snapshots of budget statistics at specific times.

| Column Name                       | Data Type   | Constraints                               | Description                                         |
|-----------------------------------|-------------|-------------------------------------------|-----------------------------------------------------|
| `id`                              | UUID        | PRIMARY KEY                               | Unique identifier for the statistics record       |
| `budget_id`                       | UUID        | NOT NULL, FOREIGN KEY REFERENCES budgets(id) ON DELETE CASCADE | Budget these statistics belong to                 |
| `user_id`                         | UUID        | NOT NULL                                  | Identifier of the user owning the statistics      |
| `current_balance_amount`          | INTEGER     | NOT NULL                                  | Current balance amount snapshot (smallest unit)   |
| `current_balance_currency`        | VARCHAR(3)  | NOT NULL                                  | Currency code for the balance (ISO 4217)          |
| `daily_available_amount_amount`   | INTEGER     | NOT NULL                                  | Daily available amount snapshot (smallest unit) |
| `daily_available_amount_currency` | VARCHAR(3)  | NOT NULL                                  | Currency code for daily available amount          |
| `daily_average_amount`            | INTEGER     | NOT NULL                                  | Daily average spending snapshot (smallest unit) |
| `daily_average_currency`          | VARCHAR(3)  | NOT NULL                                  | Currency code for daily average                   |
| `used_limit_amount`               | INTEGER     | NOT NULL                                  | Used limit amount snapshot (smallest unit)        |
| `used_limit_currency`             | VARCHAR(3)  | NOT NULL                                  | Currency code for used limit                      |
| `creation_date`                   | DATE        | NOT NULL                                  | Date when the statistics snapshot was created     |
| `version`                         | INTEGER     | NOT NULL DEFAULT 1                        | Optimistic locking version counter                |
| `created_at`                      | DATE        | NOT NULL DEFAULT CURRENT_DATE             | Date of record creation                         |

*Note:* Statistics records are snapshots, so `updated_at` is not included.

### `category_statistics_records`
Stores detailed statistics for categories within a statistics snapshot.

| Column Name                       | Data Type   | Constraints                                     | Description                                           |
|-----------------------------------|-------------|-------------------------------------------------|-------------------------------------------------------|
| `id`                              | UUID        | PRIMARY KEY                                     | Unique identifier for the category statistics record |
| `statistics_record_id`            | UUID        | NOT NULL, FOREIGN KEY REFERENCES statistics_records(id) ON DELETE CASCADE | Parent statistics record this belongs to          |
| `category_id`                     | UUID        | NOT NULL, FOREIGN KEY REFERENCES categories(id) ON DELETE CASCADE | Category these statistics relate to               |
| `user_id`                         | UUID        | NOT NULL                                        | Identifier of the user owning the statistics        |
| `current_balance_amount`          | INTEGER     | NOT NULL                                        | Category balance snapshot (smallest unit)         |
| `current_balance_currency`        | VARCHAR(3)  | NOT NULL                                        | Currency code for the balance (ISO 4217)            |
| `daily_available_amount_amount`   | INTEGER     | NOT NULL                                        | Category daily available amount (smallest unit)   |
| `daily_available_amount_currency` | VARCHAR(3)  | NOT NULL                                        | Currency code for daily available amount            |
| `daily_average_amount`            | INTEGER     | NOT NULL                                        | Category daily average spending (smallest unit)   |
| `daily_average_currency`          | VARCHAR(3)  | NOT NULL                                        | Currency code for daily average                     |
| `used_limit_amount`               | INTEGER     | NOT NULL                                        | Category used limit amount (smallest unit)          |
| `used_limit_currency`             | VARCHAR(3)  | NOT NULL                                        | Currency code for used limit                        |
| `version`                         | INTEGER     | NOT NULL DEFAULT 1                              | Optimistic locking version counter                  |
| `created_at`                      | DATE        | NOT NULL DEFAULT CURRENT_DATE                   | Date of record creation                         |

*Note:* Category statistics records are snapshots, so `updated_at` is not included.
*Note on `amount` columns:* Stored as INTEGER representing the smallest currency unit (e.g., cents for USD/EUR, grosze for PLN). Application layer handles conversion.
*Note on `ON DELETE` for `categories` FK in `category_statistics_records`: Set to CASCADE assuming if a category is deleted, its historical stats records are no longer relevant or should be cleaned up. This differs from the `transactions` FK which is RESTRICT as transaction handling on category delete is managed by the app.
*Note on timestamps:* Changed `created_at` and `updated_at` to `DATE` for simplicity. `updated_at` should be automatically updated via a trigger or application logic (see Section 5).

## 2. Relationships

*   **`budgets` 1 <-> N `categories`**: A budget can have multiple categories. A category belongs to exactly one budget. (FK: `categories.budget_id` -> `budgets.id`)
*   **`categories` 1 <-> N `transactions`**: A category can have multiple transactions. A transaction belongs to exactly one category. (FK: `transactions.category_id` -> `categories.id`)
*   **`budgets` 1 <-> N `statistics_records`**: A budget can have multiple statistic snapshots over time. A statistics record belongs to exactly one budget. (FK: `statistics_records.budget_id` -> `budgets.id`)
*   **`statistics_records` 1 <-> N `category_statistics_records`**: A statistics snapshot contains statistics for multiple categories. A category statistics record belongs to exactly one snapshot. (FK: `category_statistics_records.statistics_record_id` -> `statistics_records.id`)
*   **`categories` 1 <-> N `category_statistics_records`**: A category can appear in multiple statistic snapshots. A category statistics record refers to exactly one category. (FK: `category_statistics_records.category_id` -> `categories.id`)

## 3. Indexes

Based on planning recommendations and common query patterns (filtering, sorting, joins):

*   **`budgets`**:
    *   `idx_budgets_user_id_deactivation_date` ON `budgets` (`user_id`, `deactivation_date` DESC NULLS LAST) -- For filtering active/inactive budgets per user.
    *   `idx_budgets_user_id_start_date` ON `budgets` (`user_id`, `start_date` DESC) -- For sorting/filtering by start date per user.
    *   `idx_budgets_user_id` ON `budgets` (`user_id`) -- General index for RLS and user lookups.
*   **`categories`**:
    *   `idx_categories_budget_id` ON `categories` (`budget_id`) -- For joining and filtering by budget.
    *   `idx_categories_user_id` ON `categories` (`user_id`) -- For RLS.
*   **`transactions`**:
    *   `idx_transactions_category_id` ON `transactions` (`category_id`) -- For joining and filtering by category.
    *   `idx_transactions_occurred_date` ON `transactions` (`occurred_date` DESC) -- For filtering by date range.
    *   `idx_transactions_user_id` ON `transactions` (`user_id`) -- For RLS.
    *   `idx_transactions_category_id_occurred_date` ON `transactions` (`category_id`, `occurred_date` DESC) -- Combined index for common queries.
*   **`statistics_records`**:
    *   `idx_statistics_records_budget_id_creation_date` ON `statistics_records` (`budget_id`, `creation_date` DESC) -- For retrieving latest stats per budget.
    *   `idx_statistics_records_user_id` ON `statistics_records` (`user_id`) -- For RLS.
*   **`category_statistics_records`**:
    *   `idx_cat_stats_records_stat_record_id` ON `category_statistics_records` (`statistics_record_id`) -- For joining to parent record.
    *   `idx_cat_stats_records_category_id` ON `category_statistics_records` (`category_id`) -- For querying stats by category.
    *   `idx_cat_stats_records_user_id` ON `category_statistics_records` (`user_id`) -- For RLS.

*Note:* PostgreSQL automatically creates indexes on PRIMARY KEY columns. Indexes on FOREIGN KEY columns are generally recommended and included above.

## 4. Row Level Security (RLS) Policies

RLS must be enabled for each table below (`ALTER TABLE <table_name> ENABLE ROW LEVEL SECURITY; ALTER TABLE <table_name> FORCE ROW LEVEL SECURITY;`). A mechanism to set `current_setting('app.current_user_id', true)` for the current user's UUID within the session is assumed.

*   **`budgets`**:
    ```sql
    CREATE POLICY select_budgets ON budgets FOR SELECT
    USING (user_id = UUID(current_setting('app.current_user_id', true)));

    CREATE POLICY insert_budgets ON budgets FOR INSERT
    WITH CHECK (user_id = UUID(current_setting('app.current_user_id', true)));

    CREATE POLICY update_budgets ON budgets FOR UPDATE
    USING (user_id = UUID(current_setting('app.current_user_id', true)));

    -- DELETE policy is not defined as budgets use soft delete (update deactivation_date).
    ```
*   **`categories`**:
    ```sql
    CREATE POLICY select_categories ON categories FOR SELECT
    USING (user_id = UUID(current_setting('app.current_user_id', true)));

    CREATE POLICY insert_categories ON categories FOR INSERT
    WITH CHECK (user_id = UUID(current_setting('app.current_user_id', true)));

    CREATE POLICY update_categories ON categories FOR UPDATE
    USING (user_id = UUID(current_setting('app.current_user_id', true)));

    CREATE POLICY delete_categories ON categories FOR DELETE
    USING (user_id = UUID(current_setting('app.current_user_id', true)));
    ```
*   **`transactions`**:
    ```sql
    CREATE POLICY select_transactions ON transactions FOR SELECT
    USING (user_id = UUID(current_setting('app.current_user_id', true)));

    CREATE POLICY insert_transactions ON transactions FOR INSERT
    WITH CHECK (user_id = UUID(current_setting('app.current_user_id', true)));

    CREATE POLICY update_transactions ON transactions FOR UPDATE
    USING (user_id = UUID(current_setting('app.current_user_id', true)));

    CREATE POLICY delete_transactions ON transactions FOR DELETE
    USING (user_id = UUID(current_setting('app.current_user_id', true)));
    ```
*   **`statistics_records`**:
    ```sql
    CREATE POLICY select_statistics_records ON statistics_records FOR SELECT
    USING (user_id = UUID(current_setting('app.current_user_id', true)));

    CREATE POLICY insert_statistics_records ON statistics_records FOR INSERT
    WITH CHECK (user_id = UUID(current_setting('app.current_user_id', true)));

    -- UPDATE/DELETE policies are omitted as statistics records are typically immutable snapshots.
    -- Deletion is handled via CASCADE from the parent budget.
    ```
*   **`category_statistics_records`**:
    ```sql
    CREATE POLICY select_category_stats ON category_statistics_records FOR SELECT
    USING (user_id = UUID(current_setting('app.current_user_id', true)));

    CREATE POLICY insert_category_stats ON category_statistics_records FOR INSERT
    WITH CHECK (user_id = UUID(current_setting('app.current_user_id', true)));

    -- UPDATE/DELETE policies are omitted as statistics records are typically immutable snapshots.
    -- Deletion is handled via CASCADE from the parent statistics_record or category.
    ```

## 5. Additional Notes

*   **UUID Generation**: UUIDs should ideally be generated by the application (e.g., using `uuid.uuid4()` in Python) before inserting into the database.
*   **Money Representation**: Using `INTEGER` for monetary values (smallest unit) is chosen for precision. The application layer handles currency context and formatting.
*   **Soft Delete**: The `budgets` table uses a `deactivation_date` column for soft deletes. Active budgets have `deactivation_date IS NULL`.
*   **Constraints**: Most business rule validations (e.g., uniqueness of category names within a budget, limit checks) are handled at the application layer. Basic `NOT NULL` and `CHECK` constraints are used in the database.
*   **Timestamps**: `created_at` and `updated_at` columns are included for auditing, now using `DATE`. An automatic update mechanism for `updated_at` (e.g., a trigger) should be implemented using `CURRENT_DATE`.
    ```sql
    -- Example Trigger Function for updated_at (using DATE)
    CREATE OR REPLACE FUNCTION update_updated_at_column()
    RETURNS TRIGGER AS $$
    BEGIN
       -- Check if NEW has the updated_at column before trying to set it
       IF TG_OP = 'UPDATE' AND NEW IS DISTINCT FROM OLD THEN
           NEW.updated_at = CURRENT_DATE; -- Use CURRENT_DATE for DATE type
       END IF;
       RETURN NEW;
    END;
    $$ language 'plpgsql';

    -- Apply trigger to tables with updated_at (e.g., budgets)
    -- Ensure the trigger function exists before creating triggers
    CREATE TRIGGER update_budgets_updated_at
    BEFORE UPDATE ON budgets
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

    CREATE TRIGGER update_categories_updated_at
    BEFORE UPDATE ON categories
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

    CREATE TRIGGER update_transactions_updated_at
    BEFORE UPDATE ON transactions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
    ```
*   **Statistics Calculation**: The `statistics_records` and `category_statistics_records` tables store *snapshots*. Calculation logic resides within the application.
*   **ON DELETE Behavior**: The choice of `RESTRICT` vs `CASCADE` for foreign keys reflects planning decisions, balancing data integrity with application-managed deletion logic.
*   **RLS Implementation**: Assumes a session variable `app.current_user_id` is set containing the authenticated user's UUID. The application connection pool or middleware needs to handle setting this variable appropriately for each session/request.
*   **Versioning**: A `version` column (integer, default 1) is added to all tables to support optimistic concurrency control mechanisms if needed later by the application.
