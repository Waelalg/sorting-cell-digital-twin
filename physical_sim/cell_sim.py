# physical_sim/cell_sim.py

import asyncio
import random
import logging
from typing import Tuple

from common.events import Event, EventType
from twin_core.event_bus import EventBus

logger = logging.getLogger(__name__)


class SortingCellSimulator:
    """
    Asynchronous simulation of a simple sorting cell:

    - Parts arrive on a conveyor.
    - A sensor evaluates each part as "ok" or "nok".
    - An actuator sends the part to the appropriate bin.
    - Events are published to the EventBus at each step.

    This plays the role of the "physical" system in our Digital Twin.
    """

    def __init__(
        self,
        bus: EventBus,
        part_interarrival: Tuple[float, float] = (0.5, 1.5),
        sensor_delay: Tuple[float, float] = (0.1, 0.3),
        actuator_delay: Tuple[float, float] = (0.1, 0.2),
        ok_probability: float = 0.8,
    ) -> None:
        self._bus = bus
        self.part_interarrival = part_interarrival
        self.sensor_delay = sensor_delay
        self.actuator_delay = actuator_delay
        self.ok_probability = ok_probability
        self._part_counter = 0

        logger.info(
            "SortingCellSimulator initialized "
            f"(interarrival={part_interarrival}, ok_prob={ok_probability})"
        )

    async def run(self) -> None:
        """
        Main loop: generates parts at random intervals and
        launches a processing coroutine for each part.
        """
        loop = asyncio.get_running_loop()
        logger.info("SortingCellSimulator run loop started")

        while True:
            # Wait for the next part to arrive
            dt = random.uniform(*self.part_interarrival)
            await asyncio.sleep(dt)

            part_id = f"P{self._part_counter}"
            self._part_counter += 1
            t = loop.time()

            logger.info("PART_ARRIVED part_id=%s t=%.3f", part_id, t)

            # Emit PART_ARRIVED event
            event = Event(
                type=EventType.PART_ARRIVED,
                timestamp=t,
                data={"part_id": part_id},
            )
            await self._bus.publish(event)

            # Start processing this part asynchronously
            asyncio.create_task(self._process_part(part_id))

    async def _process_part(self, part_id: str) -> None:
        """
        Process a single part through:
        - sensor reading
        - actuator decision
        - final sorted outcome
        """
        loop = asyncio.get_running_loop()

        # Sensor phase
        await asyncio.sleep(random.uniform(*self.sensor_delay))
        is_ok = random.random() < self.ok_probability
        sensor_result = "ok" if is_ok else "nok"

        logger.info(
            "SENSOR_READ part_id=%s result=%s t=%.3f",
            part_id,
            sensor_result,
            loop.time(),
        )

        e_sensor = Event(
            type=EventType.SENSOR_READ,
            timestamp=loop.time(),
            data={"part_id": part_id, "result": sensor_result},
        )
        await self._bus.publish(e_sensor)

        # Actuator phase
        await asyncio.sleep(random.uniform(*self.actuator_delay))
        decision = "ok_bin" if is_ok else "reject_bin"

        logger.info(
            "ACTUATOR_TRIGGERED part_id=%s decision=%s t=%.3f",
            part_id,
            decision,
            loop.time(),
        )

        e_act = Event(
            type=EventType.ACTUATOR_TRIGGERED,
            timestamp=loop.time(),
            data={"part_id": part_id, "decision": decision},
        )
        await self._bus.publish(e_act)

        # Final outcome
        outcome = "ok" if is_ok else "nok"

        logger.info(
            "PART_SORTED part_id=%s outcome=%s t=%.3f",
            part_id,
            outcome,
            loop.time(),
        )

        e_sorted = Event(
            type=EventType.PART_SORTED,
            timestamp=loop.time(),
            data={"part_id": part_id, "outcome": outcome},
        )
        await self._bus.publish(e_sorted)
