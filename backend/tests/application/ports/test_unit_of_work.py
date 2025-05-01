from typing import Callable

import pytest
from adapters.outbound.persistence.in_memory.uow import InMemoryUnitOfWork
from domain.events.domain_event import DomainEvent
from domain.ports.domain_publisher import DomainPublisher


class MockEvent(DomainEvent):
    """A simple event for testing."""

    event_type: str = "test"


class MockDomainPublisher(DomainPublisher):
    """Mock domain publisher for testing."""

    def __init__(self):
        self.published_events = []
        self.subscribers = {}

    async def publish(self, event: DomainEvent) -> None:
        """Publish a domain event by adding it to the published_events list."""
        self.published_events.append(event)

    def subscribe(
        self, event_type: type[DomainEvent], subscriber: Callable[[DomainEvent], None]
    ) -> None:
        """Subscribe to a specific type of domain event."""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(subscriber)

    def unsubscribe(
        self, event_type: type[DomainEvent], subscriber: Callable[[DomainEvent], None]
    ) -> None:
        """Unsubscribe from a specific type of domain event."""
        if (
            event_type in self.subscribers
            and subscriber in self.subscribers[event_type]
        ):
            self.subscribers[event_type].remove(subscriber)

    def get_subscribers(
        self, event_type: type[DomainEvent]
    ) -> list[Callable[[DomainEvent], None]]:
        """Get all subscribers for a specific event type."""
        return self.subscribers.get(event_type, [])


class TestInMemoryUnitOfWork:
    """Tests for the InMemoryUnitOfWork."""

    @pytest.mark.asyncio
    async def test_commit_sets_flag_and_publishes_event(self):
        """Test that commit sets is_committed flag and publishes event."""
        # Arrange
        publisher = MockDomainPublisher()
        uow = InMemoryUnitOfWork(publisher)
        event = MockEvent()

        # Act
        await uow.commit(event)

        # Assert
        assert uow.is_committed is True
        assert len(publisher.published_events) == 1
        assert publisher.published_events[0] is event

    @pytest.mark.asyncio
    async def test_rollback_sets_flag(self):
        """Test that rollback sets is_rolled_back flag."""
        # Arrange
        publisher = MockDomainPublisher()
        uow = InMemoryUnitOfWork(publisher)

        # Act
        await uow.rollback()

        # Assert
        assert uow.is_rolled_back is True
