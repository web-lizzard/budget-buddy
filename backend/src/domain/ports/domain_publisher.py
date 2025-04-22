from abc import ABC, abstractmethod
from typing import Callable

from domain.events.domain_event import DomainEvent


class DomainPublisher(ABC):
    """Port for publishing domain events."""

    @abstractmethod
    async def publish(self, event: DomainEvent) -> None:
        """Publish a domain event to registered subscribers.

        Args:
            event: The domain event to publish
        """
        pass

    @abstractmethod
    def subscribe(
        self, event_type: type[DomainEvent], subscriber: Callable[[DomainEvent], None]
    ) -> None:
        """Subscribe to a specific type of domain event.

        Args:
            event_type: The type of domain event to subscribe to
            subscriber: The callable that will be invoked when an event of the specified type is published
        """
        pass

    @abstractmethod
    def unsubscribe(
        self, event_type: type[DomainEvent], subscriber: Callable[[DomainEvent], None]
    ) -> None:
        """Unsubscribe from a specific type of domain event.

        Args:
            event_type: The type of domain event to unsubscribe from
            subscriber: The callable to remove from the subscribers list
        """
        pass

    @abstractmethod
    def get_subscribers(
        self, event_type: type[DomainEvent]
    ) -> list[Callable[[DomainEvent], None]]:
        """Get all subscribers for a specific event type.

        Args:
            event_type: The type of domain event

        Returns:
            A list of callables that are subscribed to the event type
        """
        pass
