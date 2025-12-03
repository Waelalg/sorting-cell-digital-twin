# Sorting Cell Digital Twin 🔧

A **Digital Twin** of an automated sorting cell (conveyor → sensor → actuator → sorter), implemented in **Python + asyncio + FastAPI**, with a **live dashboard**.  
This project simulates a Cyber-Physical Production System (CPPS), tracks state and KPIs, and exposes a clean REST API + UI for monitoring and analysis.

---<img width="1842" height="974" alt="Screenshot From 2025-12-02 19-21-17" src="https://github.com/user-attachments/assets/31b89bb0-6b7f-44eb-a7f1-51c511e07c45" />


## ✅ Why this project matters

- Demonstrates **real-time synchronization** between a simulated physical system and its Digital Twin  
- Implements **anomaly detection** (blocked conveyor, invalid event sequences)  
- Computes **KPIs** (throughput, reject rate, processing latency) to assess system performance  
- Provides a **REST API + dashboard** to expose live data — useful for research, demonstration, or integration  

---

## 🚀 Quick Start

```bash
git clone https://github.com/Waelalg/sorting-cell-digital-twin.git
cd sorting-cell-digital-twin

python3 -m venv .venv
source .venv/bin/activate      # On Windows use .venv\Scripts\activate
pip install -r requirements.txt
```

### Run simulation + twin (CLI mode)

```bash
python main.py
```

You should see periodic monitor output like:

```
[MONITOR] {'cell_state': 'running', 'total_processed': 42, 'total_rejected': 8, 'parts_in_system': 42, 'error': False}
```

### Run API + Dashboard

```bash
uvicorn api.server:app --reload
```

Then open in browser:

```
dashboard/index.html
```

Dashboard displays:

- Cell state (IDLE / RUNNING / BLOCKED / ERROR)  
- Total processed / rejected / parts in system  
- Throughput (parts/s), reject rate %, processing window  
- Table of recent parts (ID, status, last update)  
- Health status & anomaly warnings  

---

## 📂 Project Structure

```
sorting-cell-digital-twin/
├── api/              # FastAPI endpoints
├── common/           # shared config, events, logging  
├── dashboard/        # HTML + JS dashboard  
├── physical_sim/     # simulated sorting cell  
├── twin_core/        # Digital Twin core logic  
├── config.yaml       # simulation & twin parameters  
├── main.py           # CLI demo runner  
├── requirements.txt  # dependencies  
└── docs/             # (optional) more detailed docs  
```

---

## 🧑‍💻 Core Concepts  

- **DES-style Part Lifecycle**:  
  CREATED → ON_CONVEYOR → AT_SENSOR → READY_TO_SORT → SORTED_OK / SORTED_NOK  

- **Anomaly Detection**  
  - `BLOCKED`: triggered when no events happen for more than `blocked_threshold` seconds  
  - `ERROR`: triggered if an event sequence is invalid (e.g. PART_SORTED without prior sensor/actuator events)  

- **KPIs (via /metrics)**  
  - `throughput` = processed parts / observation window  
  - `reject_rate` = rejected parts / processed parts  
  - `observation_window` = time since first event  

- **API endpoints**  
  - `GET /state`  → high-level twin status  
  - `GET /metrics` → performance KPIs  
  - `GET /parts` → list of all parts with status & last timestamp  

---

## 🛠️ Configuration  

All simulation parameters and twin thresholds are configurable in `config.yaml`:

```yaml
simulation:
  part_interarrival: [0.5, 1.5]   # seconds between new parts  
  sensor_delay:       [0.1, 0.3]   # sensor processing delay  
  actuator_delay:     [0.1, 0.2]   # actuator delay  
  ok_probability:      0.8        # probability a part is accepted  

twin:
  blocked_threshold:   5.0        # seconds before marking as BLOCKED  
```

Adjust these values and rerun to model different load and system behaviors.

---

## 🎯 Possible Improvements / Future Work

- Limit memory usage by keeping only last N parts (instead of storing all)  
- Add pause/resume or speed-control endpoints for the simulator  
- Export metrics to a time-series database (InfluxDB, Prometheus) + real-time monitoring (Grafana)  
- Add unit tests covering twin logic and API endpoints  
- Provide a full “report” + usage examples (e.g. high-load scenario, fault injection)  

---

## 🙋 Contact & Credits

Created by **Waelalg**.  
Feel free to open issues or PRs — feedback is welcome!  
