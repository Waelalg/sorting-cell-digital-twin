# main.py

import asyncio

from twin_core.event_bus import EventBus
from twin_core.twin import DigitalTwin
from physical_sim.cell_sim import SortingCellSimulator
from common.logging_config import configure_logging


async def main_async() -> None:
    # Configure logging once for the CLI mode
    configure_logging()

    # Create core components
    bus = EventBus()
    twin = DigitalTwin(bus)
    sim = SortingCellSimulator(bus)

    # Start the event bus loop
    bus_task = asyncio.create_task(bus.run())

    # Start the physical simulation
    sim_task = asyncio.create_task(sim.run())

    # Simple monitoring task: periodically print twin state
    async def monitor():
        while True:
            await asyncio.sleep(2.0)
            snapshot = await twin.get_state_snapshot()
            print("[MONITOR]", snapshot)

    monitor_task = asyncio.create_task(monitor())

    # Run all tasks forever (Ctrl+C to stop)
    await asyncio.gather(bus_task, sim_task, monitor_task)


if __name__ == "__main__":
    asyncio.run(main_async())
