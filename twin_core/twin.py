# twin_core/twin.py

from __future__ import annotations

import asyncio
from typing import Any

from common.events import Event
from twin_core.event_bus import EventBus
from twin_core.state_model import TwinState


class DigitalTwin:
    """
    Digital Twin core.

    - Subscribes to events from the EventBus.
    - Updates its internal TwinState.
    - Exposes methods to query the current state (for APIs, dashboards, etc.).
    """

    def __init__(self, bus: EventBus) -> None:
        self._bus = bus
        self._state = TwinState()
        # Register our async handler to the bus
        self._bus.subscribe(self._handle_event)

        # This lock protects state reads/writes if needed
        self._lock = asyncio.Lock()

    async def _handle_event(self, event: Event) -> None:
        """Callback invoked by the EventBus for each new event."""
        async with self._lock:
            self._state.handle_event(event)

    async def get_state_snapshot(self) -> dict:
        """Return a thread-safe snapshot of the twin state."""
        async with self._lock:
            return self._state.snapshot()

    # Later we can add:
    # - methods for predictions / what-if scenarios
    # - state congruence checks
    # - anomaly detection, etc.
