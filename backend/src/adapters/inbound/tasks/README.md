# Tasks Module Technical Documentation

## Overview

The Tasks module provides asynchronous task processing capabilities for the Budget Buddy application using Celery. It allows for the execution of long-running or resource-intensive operations outside the main request/response cycle, ensuring responsive user interfaces and reliable background processing.

## Core Components

### 1. Celery Application (`celery_app.py`)

The Celery application is configured in `celery_app.py` with the following features:

- RabbitMQ as the message broker
- JSON serialization for task payloads
- Task routing configuration
- Retry mechanisms for failed tasks

```python
# Example usage of the Celery app
from celery_app import app

# Get the configured Celery application
celery = app
```

### 2. Budget Tasks (`budget_tasks.py`)

This module contains task definitions related to budget operations, including:

#### `renew_budget_task`

A Celery task that handles budget renewal operations with the following features:
- Dependency injection for handler components
- Automatic retry mechanism for failed tasks (max 3 retries with increasing delay)
- Error handling and logging
- Asynchronous execution with proper event loop management

```python
# Example of scheduling the task
from adapters.inbound.tasks.budget_tasks import renew_budget_task

# Schedule the task with a 30-second delay
renew_budget_task.apply_async(
    args=["budget-uuid", "user-uuid"],
    countdown=30
)
```

## Integration with Event System

Tasks are typically triggered as a result of domain events, creating a decoupled architecture:

1. Domain events (e.g., `BudgetCreated`) are published to RabbitMQ
2. Event subscribers consume these events and schedule appropriate Celery tasks
3. Celery workers execute the tasks asynchronously

## Configuration

Tasks can be configured through environment variables:

- `BUDGETBUDDY_RABBITMQ_URL`: The connection URL for RabbitMQ (default: `amqp://guest:guest@rabbitmq:5672//`)

## Deployment

Tasks run in dedicated Celery worker containers, with monitoring provided by Flower:

- Celery worker: Processes the scheduled tasks
- Flower: Provides a web UI for monitoring tasks at port 5555

## Development

### Adding a New Task

1. Create a new task function in an appropriate module with the `@shared_task` decorator
2. Configure routing in `celery_app.py` for optimal task distribution
3. Use dependency injection for required services
4. Implement proper error handling and retry logic

Example:

```python
@shared_task(bind=True, max_retries=3)
@inject
def process_something(
    self,
    item_id: str,
    handler: SomeHandler = Provide[Container.some_handler],
):
    try:
        # Task implementation
        pass
    except Exception as exc:
        self.retry(exc=exc, countdown=60 * (self.request.retries + 1))
```

### Testing Tasks

Tasks can be tested by:

1. Mocking dependencies for unit tests
2. Using test-specific task queues for integration tests
3. Setting up a dedicated test RabbitMQ instance

## Monitoring and Troubleshooting

- Task status and results are available through the Flower UI (port 5555)
- Logs are available in the Celery worker container
- Failed tasks are automatically retried according to their configuration
