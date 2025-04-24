# Command Handler - Architectural Description

## Introduction

The Command Handler is a key element of the hexagonal architecture, acting as a coordinator between the application layer and the domain. It is responsible for processing a specific command, orchestrating calls to domain logic, and managing side effects (e.g., saving to a repository or publishing events).

## Characteristics of a Command Handler

1. **Single Responsibility** - each handler processes exactly one command
2. **Independence** - handlers do not depend on each other
3. **Orchestration** - coordinates calls to both domain and infrastructure components
4. **No Business Logic** - business logic belongs to the domain; the handler only orchestrates
5. **Use Case Implementation** - directly implements the use case as described in user stories

## CommandHandler

The base Command Handler is an abstract class that provides common behavior for processing commands. This class uses the UnitOfWork port (uow), which is responsible for:
- Publishing events
- Committing transactions
- Performing rollbacks in case of errors

### Pseudocode

```python
class CommandHandler(ABC):
    _uow: UnitOfWork  # Port for handling transactions and publishing events

    async def handle(self, command: Command) -> None
        try:
            event = await self._handle(command)  # Process the command to produce an event
            await self._uow.commit(event)  # Should publish the event and commit changes to the DB
        except Exception as e:
            await self._uow.rollback()
            raise e

    @abstractmethod
    async def _handle(self, command: Command) -> DomainEvent:
         ...
```

In the above pseudocode, the `_handle(command)` method represents the internal logic for processing the command. The `handle` method, which is inherited from CommandHandler, returns the generated event.

## Required Ports

Based on the analysis of the existing code and user stories, the following ports are defined:

```python
# Budget Repository
class BudgetRepository:
    async def save(self, budget, version: int = 0): ...
    async def get_by_id(self, budget_id): ...
    async def get_by_user_id(self, user_id): ...
    async def update(self, budget, version: int): ...

# Transaction Repository
class TransactionRepository:
    async def save(self, transaction): ...
    async def get_by_id(self, transaction_id): ...
    async def get_by_budget_id(self, budget_id): ...
    async def update(self, transaction): ...
    async def delete(self, transaction_id): ...

# Domain Publisher
class DomainPublisher:
    async def publish(self, event): ...

# Category Repository
class CategoryRepository:
    async def save(self, category): ...
    async def get_by_id(self, category_id): ...
    async def update(self, category): ...
    async def delete(self, category_id): ...

# UnitOfWork
class UnitOfWork:
    async def commit(self, event) -> None: ...
    async def rollback(self) -> None: ...
```

## Commands and Handlers

Based on user stories, the following commands and handlers are defined:

### Budget Management (US-001, US-002, US-003, US-012)

```python
# Commands
class CreateBudgetCommand:
    user_id: str
    total_limit: float
    currency: str
    strategy_input: StrategyInput
    start_date: date
    categories: list[CategoryData]

class DeactivateBudgetCommand:
    budget_id: str
    user_id: str

class RenewBudgetCommand:
    budget_id: str
    user_id: str

# Handlers
class CreateBudgetCommandHandler: ...
class DeactivateBudgetCommandHandler: ...
class RenewBudgetCommandHandler: ...
```

### Category Management (US-004, US-005, US-006)

```python
# Commands
class AddCategoryCommand:
    budget_id: str
    user_id: str
    name: str
    limit: float

class EditCategoryCommand:
    category_id: str
    budget_id: str
    user_id: str
    name: str
    limit: float

class RemoveCategoryCommand:
    category_id: str
    budget_id: str
    user_id: str
    handle_transactions: str  # "delete" or "move"
    target_category_id: Optional[str]  # Required if handle_transactions="move"

# Handlers
class AddCategoryCommandHandler: ...
class EditCategoryCommandHandler: ...
class RemoveCategoryCommandHandler: ...
```

### Transaction Management (US-007, US-008, US-009)

```python
# Commands
class CreateTransactionCommand:
    budget_id: str
    category_id: str
    user_id: str
    amount: float
    currency: str
    transaction_type: str  # "EXPENSE" or "INCOME"
    occurred_date: date
    description: Optional[str]

class EditTransactionCommand:
    transaction_id: str
    budget_id: str
    user_id: str
    category_id: str
    amount: float
    transaction_type: str
    occurred_date: date
    description: Optional[str]

class DeleteTransactionCommand:
    transaction_id: str
    budget_id: str
    user_id: str

# Handlers
class CreateTransactionCommandHandler: ...
class EditTransactionCommandHandler: ...
class DeleteTransactionCommandHandler: ...
```

## Sample Pseudocode for a Command Handler

Below are updated pseudocode examples for selected handlers demonstrating inheritance from CommandHandler and returning the appropriate event via the _handle method.

### CreateBudgetCommandHandler

```python
class CreateBudgetCommandHandler(CommandHandler):
    def __init__(self,
                 budget_repository: BudgetRepository,
                 budget_factory: BudgetFactory):
        self._budget_repository = budget_repository
        self._budget_factory = budget_factory

    async def _handle(self, command: CreateBudgetCommand) -> DomainEvent:
        # 1. Prepare input data
        category_inputs = [self._prepare_category_input(category, command.currency)
                           for category in command.categories]
        total_limit = Limit(Money.mint(command.total_limit, command.currency))

        # 2. Create the budget aggregate
        budget = await self._budget_factory.create_budget(
            user_id=command.user_id,
            total_limit=total_limit,
            budget_strategy_input=command.strategy_input,
            start_date=command.start_date,
            categories=category_inputs
        )

        # 3. Save to repository
        await self._budget_repository.save(budget=budget, version=0)

        # 4. Create and return the event
        event = BudgetCreated(
            budget_id=str(budget.id),
            user_id=str(budget.user_id),
            total_limit=total_limit.value.amount,
            start_date=budget.start_date,
            strategy=str(command.strategy_input.strategy_type)
        )
        return event
```

### EditCategoryCommandHandler

```python
class EditCategoryCommandHandler(CommandHandler):
    def __init__(self,
                 budget_repository: BudgetRepository):
        self._budget_repository = budget_repository

    async def _handle(self, command: EditCategoryCommand) -> DomainEvent:
        # 1. Retrieve the budget aggregate
        budget = await self._budget_repository.get_by_id(command.budget_id)

        # 2. Validate owner
        if str(budget.user_id) != command.user_id:
            raise PermissionError("User is not the owner of this budget")

        # 3. Prepare new values
        new_name = CategoryName(command.name)
        new_limit = Limit(Money.mint(command.limit, budget.total_limit.value.currency))

        # 4. Edit the category in the aggregate
        current_version = budget.version
        budget.edit_category(
            category_id=command.category_id,
            name=new_name,
            limit=new_limit
        )

        # 5. Save changes
        await self._budget_repository.update(budget, current_version)

        # 6. Create and return the event
        event = CategoryEdited(
            budget_id=str(budget.id),
            category_id=command.category_id,
            name=command.name,
            limit=command.limit
        )
        return event
```

### DeleteTransactionCommandHandler

```python
class DeleteTransactionCommandHandler(CommandHandler):
    def __init__(self,
                 transaction_repository: TransactionRepository,
                 budget_repository: BudgetRepository):
        self._transaction_repository = transaction_repository
        self._budget_repository = budget_repository

    async def _handle(self, command: DeleteTransactionCommand) -> DomainEvent:
        # 1. Retrieve the transaction
        transaction = await self._transaction_repository.get_by_id(command.transaction_id)

        # 2. Validate owner
        if str(transaction.user_id) != command.user_id:
            raise PermissionError("User is not the owner of this transaction")

        # 3. Retrieve the budget aggregate
        budget = await self._budget_repository.get_by_id(command.budget_id)

        # 4. Remove the transaction from the aggregate
        current_version = budget.version
        budget.remove_transaction(transaction.id)
        await self._budget_repository.update(budget, current_version)

        # 5. Delete the transaction from repository
        await self._transaction_repository.delete(command.transaction_id)

        # 6. Create and return the event
        event = TransactionDeleted(
            transaction_id=str(transaction.id),
            budget_id=str(budget.id),
            category_id=str(transaction.category_id),
            amount=transaction.amount.amount
        )
        return event
```

## Summary

The Command Handler is a key element of the architecture, which:

1. Implements a specific use case
2. Orchestrates calls to domain objects
3. Manages side effects (saving to the database, publishing events)
4. Ensures data consistency
5. Isolates application logic from business logic

When implementing, remember to:
- Limit the handler's responsibility to orchestration
- Use ports (repositories, publishers) instead of direct implementations
- Publish domain events
- Validate permissions and input data
