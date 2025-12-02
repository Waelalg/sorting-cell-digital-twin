# twin_core/state_model.py

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Optional
import logging

from common.events import Event, EventType

logger = logging.getLogger(__name__)


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
    READY_TO_SORT = "ready_to_sort"
    SORTED_OK = "sorted_ok"
    SORTED_NOK = "sorted_nok"


@dataclass
class Part:
    """Representation of a part inside the system."""
    part_id: str
    status: PartStatus
    last_timestamp: float


@dataclass
class TwinState:
    """
    Digital Twin internal DES-style state with anomaly detection and metrics.

    - BLOCKED when no events for too long
    - ERROR when invalid event sequence detected
    - Metrics: throughput, reject rate, observation window
    """

    cell_state: CellState = CellState.IDLE
    parts: Dict[str, Part] = field(default_factory=dict)

    total_processed: int = 0
    total_rejected: int = 0

    # Anomaly + time tracking
    last_event_time: float = 0.0
    system_start_time: float = 0.0
    blocked_threshold: float = 5.0
    error_flag: bool = False

    def _get_or_create_part(self, part_id: str, timestamp: float) -> Part:
        if part_id not in self.parts:
            self.parts[part_id] = Part(
                part_id=part_id,
                status=PartStatus.CREATED,
                last_timestamp=timestamp,
            )
        return self.parts[part_id]

    def validate_sequence(self, part: Part, event_type: EventType) -> bool:
        """
        Rule-based validation of event ordering.
        This ensures the twin mirrors a realistic CPPS workflow.
        """
        valid_flow = {
            PartStatus.CREATED:        [EventType.PART_ARRIVED],
            PartStatus.ON_CONVEYOR:    [EventType.SENSOR_READ],
            PartStatus.AT_SENSOR:      [EventType.ACTUATOR_TRIGGERED],
            PartStatus.READY_TO_SORT:  [EventType.PART_SORTED],
            PartStatus.SORTED_OK:      [],
            PartStatus.SORTED_NOK:     [],
        }
        return event_type in valid_flow.get(part.status, [])

    def check_blocked(self, current_time: float):
        """Detect lack of activity → BLOCKED state."""
        if self.last_event_time == 0.0:
            return
        if (current_time - self.last_event_time) > self.blocked_threshold:
            if self.cell_state != CellState.BLOCKED:
                logger.warning(
                    "CELL BLOCKED: No events for %.2fs",
                    current_time - self.last_event_time,
                )
            self.cell_state = CellState.BLOCKED

    def handle_event(self, event: Event) -> None:
        etype = event.type
        data = event.data
        t = event.timestamp

        # Update last received activity time
        self.last_event_time = t

        # First event → running + set system start time
        if self.cell_state == CellState.IDLE:
            self.cell_state = CellState.RUNNING
            self.system_start_time = t

        part_id = data.get("part_id")
        part = self._get_or_create_part(part_id, t)

        # Validate event sequence
        if not self.validate_sequence(part, etype):
            self.cell_state = CellState.ERROR
            self.error_flag = True
            logger.error(
                "INVALID EVENT ORDER: part=%s status=%s event=%s",
                part_id,
                part.status.value,
                etype.value,
            )
            return

        # Apply transitions
        if etype == EventType.PART_ARRIVED:
            part.status = PartStatus.ON_CONVEYOR
            part.last_timestamp = t

        elif etype == EventType.SENSOR_READ:
            part.status = PartStatus.AT_SENSOR
            part.last_timestamp = t

        elif etype == EventType.ACTUATOR_TRIGGERED:
            part.status = PartStatus.READY_TO_SORT
            part.last_timestamp = t

        elif etype == EventType.PART_SORTED:
            outcome = data["outcome"]
            if outcome == "ok":
                part.status = PartStatus.SORTED_OK
                self.total_processed += 1
            else:
                part.status = PartStatus.SORTED_NOK
                self.total_processed += 1
                self.total_rejected += 1

            part.last_timestamp = t

            logger.info(
                "PART_SORTED: part=%s outcome=%s processed=%d rejected=%d",
                part_id,
                outcome,
                self.total_processed,
                self.total_rejected,
            )

        # Check if BLOCKED (based on event time)
        self.check_blocked(t)

    def get_part(self, part_id: str) -> Optional[Part]:
        return self.parts.get(part_id)

    def parts_snapshot(self) -> list[dict]:
        """
        Return a list of parts with their status and last timestamp.
        Useful for monitoring / dashboards.
        """
        return [
            {
                "part_id": part.part_id,
                "status": part.status.value,
                "last_timestamp": part.last_timestamp,
            }
            for part in self.parts.values()
        ]

    def snapshot(self) -> dict:
        """Return a JSON-serializable state."""
        return {
            "cell_state": self.cell_state.value,
            "total_processed": self.total_processed,
            "total_rejected": self.total_rejected,
            "parts_in_system": len(self.parts),
            "error": self.error_flag,
        }

    def metrics_snapshot(self) -> dict:
        """
        Compute high-level KPIs:
        - throughput: parts / second over observation window
        - reject_rate: ratio of rejected parts
        - observation_window: duration between first and last event
        """
        if self.system_start_time == 0.0 or self.last_event_time <= self.system_start_time:
            observation_window = 0.0
        else:
            observation_window = self.last_event_time - self.system_start_time

        if observation_window > 0.0:
            throughput = self.total_processed / observation_window
        else:
            throughput = 0.0

        if self.total_processed > 0:
            reject_rate = self.total_rejected / self.total_processed
        else:
            reject_rate = 0.0

        return {
            "total_processed": self.total_processed,
            "total_rejected": self.total_rejected,
            "reject_rate": reject_rate,
            "throughput": throughput,
            "observation_window": observation_window,
        }
