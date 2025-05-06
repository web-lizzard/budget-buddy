# Prompt: Implement Statistics Record Update on Transaction Edit

<role>
You are a Senior Backend Engineer experienced in Python, FastAPI, Domain-Driven Design (DDD), Hexagonal Architecture, SQLAlchemy, RabbitMQ, and Celery. You are tasked with extending the Budget Buddy application's functionality.
</role>

<context>
The application uses a Hexagonal Architecture. Domain events trigger actions via RabbitMQ subscribers. Statistics (`StatisticsRecord`) for a budget are currently calculated and stored when a `TransactionAdded` event occurs, creating a snapshot of the budget's state *after* that transaction. This is handled by `backend/src/adapters/inbound/subscribers/transaction_added_subscriber.py` which dispatches a `CalculateStatisticsCommand`. The core calculation logic resides in `domain/services/statistics_calculation_service.py`, utilized by `backend/src/application/commands/handlers/calculate_statistics_command_handler.py`.

Relevant Files:
- Domain Aggregate: `backend/src/domain/aggregates/statistics_record.py`
- Domain Event: `backend/src/domain/events/transaction/transaction_updated.py`
- Domain Service: `backend/src/domain/services/statistics_calculation_service.py`
- Existing Subscriber: `backend/src/adapters/inbound/subscribers/transaction_added_subscriber.py`
- Existing Command Handler: `backend/src/application/commands/handlers/calculate_statistics_command_handler.py`
- Repositories: `backend/src/adapters/outbound/persistence/sql_alchemy/repositories/` (`budget_repository.py`, `transaction_repository.py`, `statistics_repository.py`)
- SQLAlchemy Models: `backend/src/adapters/outbound/persistence/sql_alchemy/models.py`
- DI Container: `backend/src/infrastructure/container/main_container.py` (or similar)
- Application Startup: `backend/src/main.py` (or where subscribers/handlers are registered)
- Command Handler Base/Docs: `backend/src/application/commands/README.md`
- Ports: `backend/src/domain/ports/`
</context>

<task>
Implement the functionality to find and update the specific `StatisticsRecord` associated with an edited `Transaction`. The update should recalculate statistics based on all transactions up to the **occurrence date** of the edited transaction. This process should be triggered by the `TransactionUpdated` domain event.
</task>

<implementation_plan>
Follow these steps to implement the feature:

1.  **Modify Domain & Persistence for Linking:**
    *   **`StatisticsRecord` Aggregate:** Add an optional `transaction_id: uuid.UUID | None` field to `backend/src/domain/aggregates/statistics_record.py::StatisticsRecord`.
    *   **SQLAlchemy Model:** Add a corresponding `transaction_id: Mapped[uuid.UUID | None]` column to `backend/src/adapters/outbound/persistence/sql_alchemy/models.py::StatisticsRecordModel`. Consider adding a foreign key constraint (`ForeignKey("transactions.id")`) and an index. Decide if the relationship should be nullable or if a record *must* be linked to a transaction.
    *   **Update Existing Handler (`CalculateStatisticsCommandHandler`):** Modify `backend/src/application/commands/handlers/calculate_statistics_command_handler.py`.
        *   Ensure the `CalculateStatisticsCommand` receives the `transaction_id` of the newly added transaction (update the command definition and how it's populated by the `transaction_added_subscriber.py`).
        *   When creating the `StatisticsRecord` domain object within the `_handle` method, pass the `transaction_id` to its constructor.

2.  **Add New Repository Methods:**
    *   **`StatisticsRepository`:**
        *   Define `find_by_transaction_id(self, transaction_id: uuid.UUID, user_id: uuid.UUID) -> StatisticsRecord` in the interface (`domain/ports/outbound/statistics_repository.py`).
        *   Implement this method in the SQLAlchemy repository (`adapters/outbound/persistence/sql_alchemy/repositories/statistics_repository.py`) to fetch the specific record linked to the transaction. Handle `NotFound` cases appropriately.
    *   **`TransactionRepository`:**
        *   Define `find_by_budget_id_and_date_range(self, budget_id: uuid.UUID, user_id: uuid.UUID, end_date: datetime) -> list[Transaction]` in the interface (`domain/ports/transaction_repository.py`).
        *   Implement this method in the SQLAlchemy repository (`adapters/outbound/persistence/sql_alchemy/repositories/transaction_repository.py`) to fetch transactions for the budget up to and including the specified `end_date`.

3.  **Create New Subscriber:**
    *   Create `backend/src/adapters/inbound/subscribers/transaction_updated_subscriber.py`.
    *   Implement `on_transaction_updated_message` similar to the existing `on_transaction_added_message`.
    *   Consume messages from the `statistics_queue` with routing key `TransactionUpdated`.
    *   Deserialize the message into a `TransactionUpdated` event object. Extract `transaction_id`, `budget_id`, `user_id`, and the **new `date`** of the transaction.
    *   Dispatch a `RecalculateStatisticsAfterUpdateCommand` (see step 4) with this information.
    *   Implement error handling and address the `aio_pika` callback signature as noted previously.

4.  **Define New Command:**
    *   Create `RecalculateStatisticsAfterUpdateCommand` (e.g., in `backend/src/application/commands/statistics_commands.py`).
    *   Include `transaction_id: UUID`, `budget_id: UUID`, `user_id: UUID`, and `transaction_occurred_date: datetime`.

5.  **Create New Command Handler:**
    *   Create `backend/src/application/commands/handlers/recalculate_statistics_after_update_command_handler.py`.
    *   Define `RecalculateStatisticsAfterUpdateCommandHandler` inheriting from `CommandHandler[RecalculateStatisticsAfterUpdateCommand]`.
    *   Inject dependencies: `UnitOfWork`, `BudgetRepository`, `TransactionRepository`, `StatisticsRepository`, `StatisticsCalculationService`, `Clock`.
    *   Implement the `_handle(self, command: RecalculateStatisticsAfterUpdateCommand)` method:
        *   Fetch the *specific* `StatisticsRecord` to update using `_statistics_repository.find_by_transaction_id(command.transaction_id, command.user_id)`.
        *   Fetch the `Budget` using `_budget_repository.find_by(command.budget_id, command.user_id)`.
        *   Fetch relevant `Transaction`s using `_transaction_repository.find_by_budget_id_and_date_range(budget_id=command.budget_id, user_id=command.user_id, end_date=command.transaction_occurred_date)`.
        *   Recalculate the statistics values using `_statistics_calculation_service.calculate_statistics(budget=budget, transactions=transactions)`.
        *   **Update the fields** of the fetched `statistics_record` domain object with the newly calculated values (e.g., `current_balance`, `daily_average`, etc.). You might also want to update a timestamp field like `updated_at` if it exists, or reuse `creation_date` if appropriate for the domain logic.
        *   Save the **updated** `statistics_record` object using `_statistics_repository.save(statistics_record)`. Ensure the repository's `save` method correctly handles updates (e.g., via `session.merge`).
        *   Return an appropriate domain event, e.g., `StatisticsRecalculated`, using the injected `Clock`.

6.  **Dependency Injection and Registration:**
    *   In the main DI container, register the new `RecalculateStatisticsAfterUpdateCommandHandler` and map the `RecalculateStatisticsAfterUpdateCommand` to it.
    *   In the application startup sequence, register the new `transaction_updated_subscriber`.

7.  **Testing:**
    *   Add unit tests for `RecalculateStatisticsAfterUpdateCommandHandler`, including tests for the new repository methods.
    *   Add integration tests simulating a `TransactionUpdated` event and verifying that the correct `StatisticsRecord` is updated with the recalculated values based on the correct transaction date range.

8.  **Coding Standards:**
    *   Adhere to PEP 8, type hints, and project-specific clean code practices.
    *   Ensure robust logging.
</implementation_plan>

<output_format>
Apply the changes directly to the codebase. Create new files as specified. Update existing files (domain, models, repositories, DI container, startup script, existing handler/command) as needed.
</output_format>
