This project implements a **Digital Twin** of an automated sorting cell  
(conveyor + sensor + actuator) using **Python, asyncio, FastAPI, and a small web dashboard**.

The goal is to demonstrate:

- A **simulated Cyber-Physical Production System (CPPS)**.
- A **Digital Twin core** receiving events and maintaining a synchronized state.
- **Anomaly detection** (blocked / error state).
- **KPIs**: throughput, reject rate, observation window.
- A **REST API + HTML dashboard** for monitoring and decision support.

---

## 🧱 Architecture Overview

Main components:

- `physical_sim/`
  - `SortingCellSimulator`: async simulation of the physical sorting cell.
- `twin_core/`
  - `EventBus`: asynchronous event dispatcher.
  - `TwinState`: DES-style model of the cell (parts, counters, status).
  - `DigitalTwin`: core logic + anomaly detection + KPIs.
- `api/`
  - FastAPI server exposing the Digital Twin via `/state`, `/metrics`, `/parts`.
- `dashboard/`
  - Minimal HTML/JS dashboard polling the API every 1s.

Data flow:

```mermaid
flowchart LR
    Sim[SortingCellSimulator\n(physical_sim)] -->|Events| Bus[EventBus\n(twin_core)]
    Bus --> Twin[DigitalTwin\n+ TwinState]
    Twin -->|/state\n/metrics\n/parts| API[FastAPI server]
    API --> Dashboard[HTML Dashboard\n(JavaScript)]


Event sequence for one part:

sequenceDiagram
    participant Sim as Simulator
    participant Bus as EventBus
    participant Twin as DigitalTwin

    Sim->>Bus: PART_ARRIVED(part_id)
    Bus->>Twin: PART_ARRIVED
    Sim->>Bus: SENSOR_READ(part_id, result)
    Bus->>Twin: SENSOR_READ
    Sim->>Bus: ACTUATOR_TRIGGERED(part_id, decision)
    Bus->>Twin: ACTUATOR_TRIGGERED
    Sim->>Bus: PART_SORTED(part_id, outcome)
    Bus->>Twin: PART_SORTED




**Installation **

git clone
cd sorting-cell-digital-twin

python3 -m venv .venv
source .venv/bin/activate        # On Windows: .venv\Scripts\activate

pip install -r requirements.txt


**Project Structure**

sorting-cell-digital-twin/
├── api/
│   └── server.py           # FastAPI app (/state, /metrics, /parts)
├── common/
│   ├── config.py           # Load config.yaml → AppConfig
│   ├── events.py           # Event + EventType definitions
│   └── logging_config.py   # Central logging setup
├── dashboard/
│   └── index.html          # HTML/JS dashboard (polls /state, /metrics, /parts)
├── physical_sim/
│   └── cell_sim.py         # SortingCellSimulator (async CPPS simulation)
├── twin_core/
│   ├── event_bus.py        # Asynchronous event bus
│   ├── state_model.py      # TwinState, Part, CellState, PartStatus
│   └── twin.py             # DigitalTwin orchestration + locks
├── config.yaml             # Simulation + Digital Twin thresholds
├── main.py                 # CLI runner (sim + twin + console monitor)
├── requirements.txt
└── docs/
    ├── architecture.md
    ├── api.md
    └── config.md


**Running the CLI demo **

This runs:
    EventBus
    SortingCellSimulator
    DigitalTwin
    A small monitor printing periodic snapshots

source .venv/bin/activate
python main.py

Example output:

[MONITOR] {'cell_state': 'running',
           'total_processed': 42,
           'total_rejected': 8,
           'parts_in_system': 42,
           'error': False}


**Running the API + Dashboard**
1. Start the FastAPI server
source .venv/bin/activate
uvicorn api.server:app --reload
Available endpoints:

    GET /state → current state of the Digital Twin
    GET /metrics → KPIs (throughput, reject rate, observation window)
    GET /parts → list of parts with status & last timestamps
    GET /docs → interactive Swagger UI

**Open the dashboard**

xdg-open dashboard/index.html   # Linux

The dashboard displays:

    Cell state (IDLE / RUNNING / BLOCKED / ERROR)

    Total processed / rejected / parts in system

    Throughput (parts/s), reject rate (%), observation window (s)

    Table of the latest parts (ID, status, last timestamp)

    Health summary (“No anomaly detected”, “BLOCKED”, “ERROR”)

Digital Twin Features

    DES-style state model:

        Part lifecycle:
        CREATED → ON_CONVEYOR → AT_SENSOR → READY_TO_SORT → SORTED_OK / SORTED_NOK

    Anomaly detection:

        BLOCKED: no events for more than blocked_threshold seconds

        ERROR: invalid event sequence (e.g. PART_SORTED without correct prior steps)

    KPIs:

        throughput = total_processed / observation_window

        reject_rate = total_rejected / total_processed

        observation_window = last_event_time – system_start_time

        See docs/architecture.md for a deeper technical description.

**Configuration**   
All timing and probabilities are defined in config.yaml:

simulation:
  part_interarrival: [0.5, 1.5]
  sensor_delay: [0.1, 0.3]
  actuator_delay: [0.1, 0.2]
  ok_probability: 0.8

twin:
  blocked_threshold: 5.0

The file is loaded by common/config.py and applied to:

    SortingCellSimulator (arrival rate, delays, OK probability)

    TwinState (blocked detection threshold)