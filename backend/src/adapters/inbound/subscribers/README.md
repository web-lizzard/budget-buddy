# Subscribers Module Technical Documentation

## Overview

The Subscribers module implements message consumers for domain events published to RabbitMQ. It follows the event-driven architecture pattern to decouple system components and enable asynchronous processing of business operations.

## Core Components

### 1. Subscriber Main Application (`subscriber_main.py`)

The main entry point for the subscriber service that:
- Initializes dependency injection container
- Establishes connection to RabbitMQ
- Sets up all event subscribers
- Manages the lifecycle of subscriptions

### 2. Transaction Added Subscriber (`transaction_added_subscriber.py`)

This subscriber listens for `TransactionAdded` events and triggers statistics calculations:

- Binds to the "statistics_queue" queue with the `TransactionAdded` routing key
- Deserializes incoming messages into `TransactionAdded` domain events
- Creates and dispatches `CalculateStatisticsCommand` to the appropriate handler
- Implements error handling and message acknowledgment strategies

### 3. Budget Created Subscriber (`budget_created_subscriber.py`)

This subscriber listens for `BudgetCreated` events and schedules budget renewal tasks:

- Binds to the "budget_renewal_queue" queue with the `BudgetCreated` routing key
- Deserializes incoming messages into `BudgetCreated` domain events
- Schedules asynchronous Celery tasks for budget renewal with a configurable delay
- Implements error handling and message acknowledgment strategies

## Message Processing Flow

1. Domain events are published to RabbitMQ with type-specific routing keys
2. Subscribers bind to specific routing keys and receive relevant messages
3. Subscribers process messages and take appropriate actions:
   - Direct command handling (Transaction subscriber)
   - Task scheduling (Budget subscriber)
4. Messages are acknowledged upon successful processing or requeued on failure

## Integration with DI Container

Subscribers utilize dependency injection to access required services:

```python
@inject
async def on_transaction_added_message(
    message: aio_pika.IncomingMessage,
    handler: CalculateStatisticsCommandHandler = Provide[
        MainContainer.application_container.calculate_statistics_command_handler
    ],
) -> None:
    # Message handling logic
```

## Configuration

Subscribers can be configured through the container configuration:

```python
container.config.from_dict(
    {
        "rabbitmq": {
            "url": "amqp://guest:guest@rabbitmq:5672/",
            "exchange_name": "domain_events",
        }
    }
)
```

## Deployment

Subscribers run in a dedicated container that:
- Connects to RabbitMQ at startup
- Sets up all subscriber bindings
- Processes messages continuously
- Handles connection issues with automatic reconnection

## Development

### Adding a New Subscriber

1. Create a new file in the `subscribers` module (e.g., `event_name_subscriber.py`)
2. Implement the message handler function with `@inject` decorator
3. Implement a registration function that sets up the queue, bindings, and consumer
4. Add the subscriber to `subscriber_main.py`

Example:

```python
@inject
async def on_some_event_message(message: aio_pika.IncomingMessage) -> None:
    # Message handling logic

def register_some_event_subscriber(
    channel: aio_pika.abc.AbstractChannel,
    exchange: aio_pika.abc.AbstractExchange
):
    async def setup_subscriber():
        queue = await channel.declare_queue("some_event_queue", durable=True)
        await queue.bind(exchange, routing_key="SomeEvent")
        await queue.consume(on_some_event_message)

    return setup_subscriber
```

### Error Handling Strategies

Subscribers implement robust error handling:

1. **Validation errors**: Log and acknowledge (discard invalid messages)
2. **Processing errors**: Log, negative acknowledge (nack), and requeue for retry
3. **Critical errors**: Log with full context and manage graceful degradation

## Testing

Subscribers can be tested using:

1. Unit tests with mocked RabbitMQ components
2. Integration tests with test RabbitMQ instance
3. End-to-end tests using the actual event publishing flow

## Monitoring and Troubleshooting

- Message processing is logged at appropriate levels
- Connection issues are automatically handled with reconnection
- Failed message processing can be monitored in the subscriber logs
