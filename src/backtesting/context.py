"""
backtesting.context

Purpose
-------
The Context is the *only* object strategies should interact with during a simulation step.

Design constraints (multi-strategy + centralized capital allocation):
- Strategies are READ-ONLY w.r.t. market/portfolio state (no direct portfolio mutation).
- Strategies submit only *normalized intents* (e.g., target weights, scores), never cash notionals.
- The engine collects per-strategy outputs from Context, then applies:
    strategy risk -> allocation -> global risk -> order generation -> execution -> accounting.

This module therefore provides:
1) A lightweight market snapshot for the current tick (now).
2) A per-tick, per-strategy buffer for StrategyOutput objects.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Dict, Iterable, Mapping, Optional, Tuple

import math

import pandas as pd

# -----------------------------
# Domain primitives (lightweight)
# -----------------------------

@dataclass(frozen=True, slots=True)
class Bar:
    """
    Minimal OHLCV bar container (extend as needed).

    Notes:
    - Keep this small and immutable (frozen) for safety and clarity.
    - If you later move to L2/L3 or tick data, create separate containers.
    """
    open: float
    high: float
    low: float
    close: float
    volume: float = 0.0

@dataclass(frozen=True, slots=True)
class StrategyOutput:
    """
    Strategy output for a single simulation step.

    Recommended canonical format for multi-strategy allocation:
    - weights: normalized target weights per symbol (e.g. sum(abs(w)) <= 1.0)
      Interpretation: "how to allocate the strategy's risk budget across assets".

    You may extend with metadata (confidence, horizon, tags), but keep it lightweight.
    """
    weights: Mapping[str, float]
    # Optional diagnostic metadata (kept immutable / safe)
    meta: Mapping[str, float] = field(default_factory=dict)


class Context:
    """
    Per-tick runtime context exposed to strategies.

    What it stores
    -------------
    - now: current timestamp (set each tick by the engine)
    - market: per-symbol snapshot (e.g., Bar, price fields, or features)
    - universe: tuple of tradable symbols for the current run
    - _signals_by_strategy: per-tick buffer of StrategyOutput keyed by strategy_id

    What it must NOT do
    -------------------
    - Hold or expose mutable portfolio/cash state to strategies.
    - Allow direct order placement.
    - Perform allocation or risk logic.

    Lifecycle
    ---------
    Each engine step:
      ctx.reset_step(now)
      ctx.update_market(snapshot)
      strategy reads ctx.get_* and calls ctx.submit_signals(strategy_id, output)
      engine calls ctx.collect_signals() and then proceeds to risk/allocation/execution
    """

    __slots__ = (
        "now",
        "_universe",
        "_market",
        "_market_view",
        "_signals_by_strategy",
        "_strict",
    )

