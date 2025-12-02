# twin_core/event_bus.py

import asyncio
from typing import Awaitable, Callable, List

from common.events import Event


SubscriberCallback = Callable[[Event], Awaitable[None]]


class EventBus:
    """
    Simple asynchronous event bus.

    - Producers publish Event objects.
    - Consumers subscribe with async callbacks.
    - The bus runs a loop that dispatches each event to all subscribers.
    """

    def __init__(self) -> None:
        self._queue: asyncio.Queue[Event] = asyncio.Queue()
        self._subscribers: List[SubscriberCallback] = []

    def subscribe(self, callback: SubscriberCallback) -> None:
        """Register an async callback that will be called for every event."""
        self._subscribers.append(callback)

    async def publish(self, event: Event) -> None:
        """Publish an event to the internal queue."""
        await self._queue.put(event)

    async def _dispatch(self, event: Event) -> None:
        """Send an event to all subscribers."""
        for callback in self._subscribers:
            await callback(event)

    async def run(self) -> None:
        """
        Main loop of the bus.

        This should typically be run in an asyncio task:
            asyncio.create_task(bus.run())
        """
        while True:
            event = await self._queue.get()
            await self._dispatch(event)
