import logging
from typing import Callable

from domain.events.domain_event import DomainEvent
from domain.ports.domain_publisher import DomainPublisher


class InMemoryDomainPublisher(DomainPublisher):
    """In-memory implementation of DomainPublisher."""

    _subscribers: dict[type[DomainEvent], list[Callable[[DomainEvent], None]]]

    def __init__(self):
        self._subscribers = {}
        self._logger = logging.getLogger(__name__)

    async def publish(self, event: DomainEvent) -> None:
        """Publish an event to all subscribers.

        Args:
            event: The domain event to publish
        """
        event_type = type(event)
        subscribers = self.get_subscribers(event_type)

        if not subscribers:
            self._logger.debug(f"No subscribers for event {event_type.__name__}")
            return

        self._logger.info(
            f"Publishing event {event_type.__name__} to {len(subscribers)} subscribers"
        )

        for subscriber in subscribers:
            try:
                subscriber(event)
            except Exception as e:
                self._logger.error(
                    f"Error in subscriber when handling {event_type.__name__}: {str(e)}"
                )

    def subscribe(
        self, event_type: type[DomainEvent], subscriber: Callable[[DomainEvent], None]
    ) -> None:
        """Subscribe to a specific event type.

        Args:
            event_type: The type of domain event to subscribe to
            subscriber: The callable that will be invoked when an event of the specified type is published
        """
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []

        if subscriber not in self._subscribers[event_type]:
            self._subscribers[event_type].append(subscriber)
            self._logger.debug(f"Subscriber added for event {event_type.__name__}")

    def unsubscribe(
        self, event_type: type[DomainEvent], subscriber: Callable[[DomainEvent], None]
    ) -> None:
        """Unsubscribe from a specific event type.

        Args:
            event_type: The type of domain event to unsubscribe from
            subscriber: The callable to remove from the subscribers list
        """
        if (
            event_type in self._subscribers
            and subscriber in self._subscribers[event_type]
        ):
            self._subscribers[event_type].remove(subscriber)
            self._logger.debug(f"Subscriber removed for event {event_type.__name__}")

    def get_subscribers(
        self, event_type: type[DomainEvent]
    ) -> list[Callable[[DomainEvent], None]]:
        """Get all subscribers for a specific event type.

        Args:
            event_type: The type of domain event

        Returns:
            A list of callables that are subscribed to the event type
        """
        return self._subscribers.get(event_type, [])
