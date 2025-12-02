# api/server.py

import asyncio

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from twin_core.event_bus import EventBus
from twin_core.twin import DigitalTwin
from physical_sim.cell_sim import SortingCellSimulator
from common.logging_config import configure_logging

# Configure logging once for API mode
configure_logging()

app = FastAPI(
    title="Sorting Cell Digital Twin API",
    description="Exposes the state of the digital twin of an automated sorting cell.",
    version="0.1.0",
)

# Allow CORS so a dashboard (e.g. file:// or another port) can call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # for a demo project, allow all origins
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Core components shared by the app ---

bus = EventBus()
twin = DigitalTwin(bus)
sim = SortingCellSimulator(bus)


@app.on_event("startup")
async def startup_event() -> None:
    """
    FastAPI startup hook:
    - start the EventBus dispatcher
    - start the physical simulator producing events
    """
    asyncio.create_task(bus.run())
    asyncio.create_task(sim.run())


@app.get("/state")
async def get_state():
    """
    Return the current snapshot of the Digital Twin state.
    This endpoint can be polled by a dashboard.
    """
    snapshot = await twin.get_state_snapshot()
    return snapshot
