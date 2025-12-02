# common/config.py

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Tuple

import yaml

logger = logging.getLogger(__name__)


@dataclass
class SimulationConfig:
    part_interarrival: Tuple[float, float]
    sensor_delay: Tuple[float, float]
    actuator_delay: Tuple[float, float]
    ok_probability: float


@dataclass
class TwinConfig:
    blocked_threshold: float


@dataclass
class AppConfig:
    simulation: SimulationConfig
    twin: TwinConfig


def _default_config() -> AppConfig:
    """Fallback configuration if config.yaml is missing or invalid."""
    logger.warning("Using default configuration (no config.yaml found or parse error).")
    return AppConfig(
        simulation=SimulationConfig(
            part_interarrival=(0.5, 1.5),
            sensor_delay=(0.1, 0.3),
            actuator_delay=(0.1, 0.2),
            ok_probability=0.8,
        ),
        twin=TwinConfig(
            blocked_threshold=5.0,
        ),
    )


def load_config(path: str | Path = "config.yaml") -> AppConfig:
    cfg_path = Path(path)
    if not cfg_path.exists():
        return _default_config()

    try:
        with cfg_path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
    except Exception as exc:
        logger.error("Failed to parse config file %s: %s", cfg_path, exc)
        return _default_config()

    sim_cfg = data.get("simulation", {})
    twin_cfg = data.get("twin", {})

    part_interarrival = tuple(sim_cfg.get("part_interarrival", [0.5, 1.5]))
    sensor_delay = tuple(sim_cfg.get("sensor_delay", [0.1, 0.3]))
    actuator_delay = tuple(sim_cfg.get("actuator_delay", [0.1, 0.2]))
    ok_prob = float(sim_cfg.get("ok_probability", 0.8))

    blocked_threshold = float(twin_cfg.get("blocked_threshold", 5.0))

    return AppConfig(
        simulation=SimulationConfig(
            part_interarrival=(float(part_interarrival[0]), float(part_interarrival[1])),
            sensor_delay=(float(sensor_delay[0]), float(sensor_delay[1])),
            actuator_delay=(float(actuator_delay[0]), float(actuator_delay[1])),
            ok_probability=ok_prob,
        ),
        twin=TwinConfig(
            blocked_threshold=blocked_threshold,
        ),
    )
