"""
backtesting.engine

Purpose
-------
Main orchestration loop for the backtesting system.

This engine is designed for:
- Multi-strategy execution (N strategies evaluated per tick)
- Centralized capital ownership (MasterPortfolio is the single source of truth)
- Cross-strategy capital allocation (AllocationEngine)
- Risk overlays (strategy-level and global)
- Execution simulation (Broker + Slippage)
- Accounting updates (PnL, costs, exposure)
- Deterministic, reproducible runs
"""


from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Mapping, Optional, Protocol, Tuple

import time
import pandas as pd

from context import Context, StrategyOutput

