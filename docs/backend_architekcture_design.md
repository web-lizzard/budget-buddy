# Hexagonal Architecture Implementation with FastAPI, RabbitMQ, and SQLAlchemy

## Tech Stack Overview

Our architecture implements a modular system based on the Hexagonal Architecture pattern (also known as Ports and Adapters). The core technologies include:

- **Web Framework**: FastAPI - high-performance async framework
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Message Broker**: RabbitMQ
- **Task Queue**: Celery with Flower monitoring
- **Dependency Injection**: Dependency Injector library
- **Architecture Pattern**: Hexagonal Architecture with Command Bus


## Architecture Diagram

```
┌───────────────────────────────────────────────────────────────────┐
│                           DOMAIN                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌───────────────────────────┐  │
│  │   Budget    │  │  Category   │  │    EventPublisher Port    │  │
│  │  Aggregate  │  │   Entity    │  │     publish(event)        │  │
│  └─────────────┘  └─────────────┘  └───────────┬───────────────┘  │
└───────────────────────────────────────────────┬─────────────────┘
                                               │
┌──────────────────────────────────────────────▼──────────────────┐
│                        APPLICATION                               │
│  ┌─────────────────────┐     ┌────────────────────────────────┐ │
│  │   CommandHandlers   │     │         Services               │ │
│  │ (entry points)      │     │                                │ │
│  └─────────┬───────────┘     └────────────────────────────────┘ │
└────────────┬──────────────────────────────────────────────────┘
             │
┌────────────▼──────────────────────────────────────────────────┐
│                          ADAPTERS                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐    │
│  │RabbitMQ     │  │SQLAlchemy   │  │Event Publisher      │    │
│  │Adapter      │  │Repository   │  │Implementation       │    │
│  └──────┬──────┘  └─────────────┘  └─────────────────────┘    │
└─────────┬────────────────────────────────────────────────────┘
          │
┌─────────▼────────┐     ┌─────────────┐    ┌─────────────┐
│     RabbitMQ     │◄───►│   Celery    │◄───┤   FastAPI   │
└──────────────────┘     └─────────────┘    └─────────────┘
```

In this architecture:

- The **Domain** layer contains business logic with no external dependencies
- The **Application** layer coordinates use cases through command handlers
- The **Adapters** layer connects the application to external systems (DB, messaging, etc.)
- Command Handlers serve as uniform entry points for different clients


## Implementation Examples

### 1. RabbitMQ + Celery Integration

First, let's set up Celery with RabbitMQ in a FastAPI application:

```python
# app/config/celery_config.py
from celery import Celery

# Create a Celery instance
celery_app = Celery(
    "budget_app",
    broker="amqp://guest:guest@localhost:5672//",
    backend="rpc://",
    include=["app.tasks.celery_tasks"]
)

# Optional configurations
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Europe/Warsaw",
    enable_utc=True,
    task_routes={
        'app.tasks.celery_tasks.renew_budget': {'queue': 'budget_operations'},
        'app.tasks.celery_tasks.calculate_statistics': {'queue': 'statistics'},
    }
)
```

```python
# app/tasks/celery_tasks.py
from app.config.celery_config import celery_app
from app.application.commands.budget_commands import RenewBudgetCommand
from app.application.command_bus import command_bus

@celery_app.task(name="renew_budget")
def renew_budget(budget_id: str):
    """Celery task to renew a budget based on its strategy"""
    command = RenewBudgetCommand(budget_id=budget_id)
    return command_bus.handle(command)

@celery_app.task(name="calculate_statistics")
def calculate_statistics(budget_id: str):
    """Celery task to calculate budget statistics"""
    # Command implementation here
    pass
```

```python
# app/adapters/inbound/http/budget_controller.py
from fastapi import APIRouter, Depends
from app.config.celery_config import celery_app
from app.application.command_bus import command_bus
from app.application.commands.budget_commands import CreateBudgetCommand

router = APIRouter(prefix="/budgets", tags=["budgets"])

@router.post("/")
async def create_budget(budget_data: dict):
    command = CreateBudgetCommand(**budget_data)
    budget = command_bus.handle(command)
    
    # Schedule automatic statistics calculation
    celery_app.send_task(
        "calculate_statistics",
        args=[str(budget.id)],
        countdown=10  # Run after 10 seconds
    )
    
    return {"id": str(budget.id), "message": "Budget created successfully"}
```


### 2. Dependency Injector Setup

Here's how to use Dependency Injector to manage dependencies:

```python
# app/infrastructure/container.py
from dependency_injector import containers, providers
from app.adapters.outbound.persistence.sqlalchemy_budget_repository import SQLAlchemyBudgetRepository
from app.adapters.outbound.persistence.sqlalchemy_transaction_repository import SQLAlchemyTransactionRepository
from app.adapters.outbound.messaging.rabbitmq_event_publisher import RabbitMQEventPublisher
from app.application.services.budget_service import BudgetService
from app.application.services.transaction_service import TransactionService
from app.application.command_handlers.budget_command_handlers import CreateBudgetCommandHandler
from app.application.command_handlers.transaction_command_handlers import AddTransactionCommandHandler

class Container(containers.DeclarativeContainer):
    config = providers.Configuration()
    
    # Database
    db_session_factory = providers.Singleton(
        # Session factory implementation
    )
    
    # Event Publisher
    event_publisher = providers.Singleton(
        RabbitMQEventPublisher,
        host=config.rabbitmq.host,
        port=config.rabbitmq.port,
        username=config.rabbitmq.username,
        password=config.rabbitmq.password
    )
    
    # Repositories
    budget_repository = providers.Singleton(
        SQLAlchemyBudgetRepository,
        session_factory=db_session_factory
    )
    
    transaction_repository = providers.Singleton(
        SQLAlchemyTransactionRepository,
        session_factory=db_session_factory
    )
    
    # Services
    budget_service = providers.Factory(
        BudgetService,
        budget_repository=budget_repository,
        event_publisher=event_publisher
    )
    
    transaction_service = providers.Factory(
        TransactionService,
        transaction_repository=transaction_repository,
        budget_repository=budget_repository,
        event_publisher=event_publisher
    )
    
    # Command Handlers
    create_budget_command_handler = providers.Factory(
        CreateBudgetCommandHandler,
        budget_service=budget_service
    )
    
    add_transaction_command_handler = providers.Factory(
        AddTransactionCommandHandler,
        transaction_service=transaction_service
    )
```

Usage in a FastAPI controller:

```python
# app/main.py
from fastapi import FastAPI, Depends
from dependency_injector.wiring import inject, Provide
from app.infrastructure.container import Container
from app.application.services.budget_service import BudgetService

app = FastAPI()
container = Container()
container.config.from_dict({
    "rabbitmq": {
        "host": "localhost",
        "port": 5672,
        "username": "guest",
        "password": "guest"
    }
})

@app.get("/budgets/{budget_id}")
@inject
async def get_budget(
    budget_id: str, 
    budget_service: BudgetService = Depends(Provide[Container.budget_service])
):
    budget = budget_service.get_budget_by_id(budget_id)
    return budget
```


### 3. SQLAlchemy ORM with Value Objects

Example of mapping value objects using SQLAlchemy:

```python
# app/domain/model/valueObjects/money.py
from dataclasses import dataclass
from decimal import Decimal

@dataclass(frozen=True)  # Immutable value object
class Money:
    amount: Decimal
    currency: str
    
    def __post_init__(self):
        if not isinstance(self.amount, Decimal):
            object.__setattr__(self, 'amount', Decimal(str(self.amount)))
    
    def add(self, other):
        if self.currency != other.currency:
            raise ValueError(f"Cannot add money with different currencies: {self.currency} and {other.currency}")
        return Money(amount=self.amount + other.amount, currency=self.currency)
    
    def subtract(self, other):
        if self.currency != other.currency:
            raise ValueError(f"Cannot subtract money with different currencies: {self.currency} and {other.currency}")
        return Money(amount=self.amount - other.amount, currency=self.currency)
    
    def multiply(self, factor):
        return Money(amount=self.amount * Decimal(str(factor)), currency=self.currency)
```

```python
# app/domain/model/aggregates/budget.py
from sqlalchemy import Column, String, Numeric, Date, Boolean, Integer, ForeignKey
from sqlalchemy.orm import relationship, composite
from app.infrastructure.database import Base
from app.domain.model.valueObjects.money import Money
from datetime import date

class Budget(Base):
    __tablename__ = "budgets"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    is_active = Column(Boolean, default=True)
    
    # Value object mapping using composite
    _amount = Column("amount", Numeric(precision=10, scale=2), nullable=False)
    _currency = Column("currency", String(3), nullable=False)
    total_limit = composite(
        Money,
        _amount,
        _currency
    )
    
    # Relationships
    categories = relationship("Category", back_populates="budget", cascade="all, delete-orphan")
    
    def __init__(self, id, user_id, start_date, end_date, total_limit):
        self.id = id
        self.user_id = user_id
        self.start_date = start_date
        self.end_date = end_date
        self.total_limit = total_limit
        self.is_active = True
```

Alternatively, using a custom SQL type for the value object:

```python
# app/infrastructure/database/custom_types.py
from sqlalchemy.types import TypeDecorator, VARCHAR
import json
from decimal import Decimal
from app.domain.model.valueObjects.money import Money

class MoneyType(TypeDecorator):
    impl = VARCHAR
    
    def process_bind_param(self, value, dialect):
        if value is not None:
            return json.dumps({
                'amount': str(value.amount),
                'currency': value.currency
            })
        return None
    
    def process_result_value(self, value, dialect):
        if value is not None:
            data = json.loads(value)
            return Money(
                amount=Decimal(data['amount']),
                currency=data['currency']
            )
        return None
```

```python
# Usage in model
from app.infrastructure.database.custom_types import MoneyType

class Category(Base):
    __tablename__ = "categories"
    
    id = Column(String, primary_key=True)
    budget_id = Column(String, ForeignKey("budgets.id"), nullable=False)
    name = Column(String, nullable=False)
    limit = Column(MoneyType, nullable=False)  # Using custom type
    
    # Relationships
    budget = relationship("Budget", back_populates="categories")
    transactions = relationship("Transaction", back_populates="category", cascade="all, delete-orphan")
```


## Command Bus Implementation

The Command Bus pattern is central to this architecture:

```python
# app/application/command_bus.py
from typing import Dict, Type, Any
from app.application.commands.base_command import BaseCommand
from app.application.command_handlers.base_command_handler import BaseCommandHandler

class CommandBus:
    def __init__(self):
        self._handlers: Dict[Type[BaseCommand], BaseCommandHandler] = {}
    
    def register(self, command_type: Type[BaseCommand], handler: BaseCommandHandler) -&gt; None:
        self._handlers[command_type] = handler
    
    def handle(self, command: BaseCommand) -&gt; Any:
        handler = self._handlers.get(type(command))
        if not handler:
            raise ValueError(f"No handler registered for command {type(command).__name__}")
        return handler.handle(command)

# Singleton instance
command_bus = CommandBus()
```


## Startup Configuration

To wire everything together:

```python
# app/main.py
from fastapi import FastAPI
from app.infrastructure.container import Container
from app.adapters.inbound.http import budget_router, transaction_router
from app.application.command_bus import command_bus
from app.application.commands.budget_commands import CreateBudgetCommand
from app.application.commands.transaction_commands import AddTransactionCommand

app = FastAPI(title="Budget Management API")

# Initialize container
container = Container()
container.config.from_dict({
    "rabbitmq": {"host": "localhost", "port": 5672, "username": "guest", "password": "guest"},
    "database": {"url": "postgresql+asyncpg://user:password@localhost:5432/budget_db"}
})

# Register command handlers
def register_command_handlers():
    command_bus.register(
        CreateBudgetCommand, 
        container.create_budget_command_handler()
    )
    command_bus.register(
        AddTransactionCommand,
        container.add_transaction_command_handler()
    )
    # Register other handlers

@app.on_event("startup")
async def startup():
    register_command_handlers()
    # Additional startup tasks

# Register routers
app.include_router(budget_router)
app.include_router(transaction_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

This architecture provides a clean separation of concerns while maintaining flexibility. The domain logic remains independent of external systems, while adapters handle the integration with databases, message queues, and other external services. Command handlers provide a uniform entry point for application use cases, regardless of whether they're triggered by HTTP requests, scheduled tasks, or message consumers.
