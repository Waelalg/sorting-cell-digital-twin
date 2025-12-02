# twin_core/state_model.py

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Optional

from common.events import Event, EventType


class CellState(Enum):
    """High-level state of the sorting cell."""
    IDLE = "idle"
    RUNNING = "running"
    BLOCKED = "blocked"
    ERROR = "error"


class PartStatus(Enum):
    """Lifecycle status of a part inside the system."""
    CREATED = "created"
    ON_CONVEYOR = "on_conveyor"
    AT_SENSOR = "at_sensor"
    SORTED_OK = "sorted_ok"
    SORTED_NOK = "sorted_nok"


@dataclass
class Part:
    """Simplified representation of a part processed by the cell."""
    part_id: str
    status: PartStatus
    last_timestamp: float


@dataclass
class TwinState:
    """
    Internal state of the Digital Twin.

    This is a DES-like abstraction updated when events are received
    from the physical (or simulated) cell.
    """
    cell_state: CellState = CellState.IDLE
    parts: Dict[str, Part] = field(default_factory=dict)

    total_processed: int = 0
    total_rejected: int = 0

    def _get_or_create_part(self, part_id: str, timestamp: float) -> Part:
        if part_id not in self.parts:
            self.parts[part_id] = Part(
                part_id=part_id,
                status=PartStatus.CREATED,
                last_timestamp=timestamp,
            )
        return self.parts[part_id]

    def handle_event(self, event: Event) -> None:
        """
        Update the twin's internal state based on an incoming event.
        This is the core DES-style update logic.
        """
        etype = event.type
        data = event.data
        t = event.timestamp

        # By default, if we receive events, we consider the cell "running"
        if self.cell_state == CellState.IDLE:
            self.cell_state = CellState.RUNNING

        if etype == EventType.PART_ARRIVED:
            part_id: str = data["part_id"]
            part = self._get_or_create_part(part_id, t)
            part.status = PartStatus.ON_CONVEYOR
            part.last_timestamp = t

        elif etype == EventType.SENSOR_READ:
            part_id: str = data["part_id"]
            result: str = data["result"]  # "ok" or "nok"
            part = self._get_or_create_part(part_id, t)
            part.status = PartStatus.AT_SENSOR
            part.last_timestamp = t

            # We don't yet know the final bin, but we know quality
            # (this could be extended later).

        elif etype == EventType.ACTUATOR_TRIGGERED:
            part_id: str = data["part_id"]
            decision: str = data["decision"]  # "ok_bin" or "reject_bin"
            part = self._get_or_create_part(part_id, t)
            part.last_timestamp = t

            if decision == "ok_bin":
                part.status = PartStatus.SORTED_OK
            else:
                part.status = PartStatus.SORTED_NOK

        elif etype == EventType.PART_SORTED:
            part_id: str = data["part_id"]
            outcome: str = data["outcome"]  # "ok" or "nok"

            part = self._get_or_create_part(part_id, t)
            part.last_timestamp = t

            if outcome == "ok":
                part.status = PartStatus.SORTED_OK
                self.total_processed += 1
            else:
                part.status = PartStatus.SORTED_NOK
                self.total_processed += 1
                self.total_rejected += 1

        # Here we could add logic to detect BLOCKED / ERROR states later.

    def get_part(self, part_id: str) -> Optional[Part]:
        return self.parts.get(part_id)

    def snapshot(self) -> dict:
        """
        Return a serializable snapshot of the current twin state.

        Useful for APIs and dashboards.
        """
        return {
            "cell_state": self.cell_state.value,
            "total_processed": self.total_processed,
            "total_rejected": self.total_rejected,
            "parts_in_system": len(self.parts),
        }
