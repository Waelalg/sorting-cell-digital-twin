# common/events.py

from enum import Enum
from dataclasses import dataclass
from typing import Dict, Any


class EventType(Enum):
    """Types of events exchanged between the physical cell and the digital twin."""
    PART_ARRIVED = "part_arrived"
    SENSOR_READ = "sensor_read"
    ACTUATOR_TRIGGERED = "actuator_triggered"
    PART_SORTED = "part_sorted"


@dataclass
class Event:
    """
    Generic event structure.

    - type: category of the event (from EventType)
    - timestamp: simulation time (float) or real time in seconds
    - data: payload with event-specific information (e.g. part_id, result, etc.)
    """
    type: EventType
    timestamp: float
    data: Dict[str, Any]
