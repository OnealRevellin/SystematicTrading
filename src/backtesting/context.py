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

    def __init__(self, universe: Iterable[str], strict: bool = True) -> None:
        """
        Parameters
        ----------
        universe:
            Iterable of tradable symbols (strings). Stored as an immutable tuple.
        strict:
            If True, invalid symbols/NaNs raise errors.
            If False, they are silently filtered out where possible.
        """

        u = tuple(universe)
        if not u:
            raise ValueError("Universe cannot be empty.")
        self._universe: Tuple[str, ...] = u
        self._strict: bool = strict

        self.now: Optional[pd.Timestamp] = None

        # Market snapshot and strategy outputs initialized per step
        # _market is mutable internally, _market_view is read-only for strategies
        self._market: Dict[str, object] = {}
        self._market_view: Mapping[str, object] = MappingProxyType(self._market)
        self._signals_by_strategy: Dict[str, StrategyOutput] = {}

        self._strict: bool = strict

    # -----------------------------
    # Tick control APIs
    # -----------------------------

    def reset_step(self, now: pd.Timestamp) -> None:
        """
        Prepare context for a new simulation step.

        Parameters
        ----------
        now:
            Current timestamp for the simulation step.
        """
        self.now = now
        self._market.clear()
        self._signals_by_strategy.clear()
    
    def update_market(self, market_snapshot: Mapping[str, object]) -> None:
        """
        Update the market snapshot for the current tick.

        Parameters
        ----------
        market_snapshot:
            Mapping of symbol to Bar (or other market data container).
        """
        
        if self.now is None:
            raise RuntimeError(
                "Context step not initialized. Call reset_step(now) first."
            )
        
        self._market.update(market_snapshot)

        if self._strict:
            u = set(self._universe)
            for sym in self._market.keys():
                if sym not in u:
                    raise ValueError(f"Symbol '{sym}' not in universe.")
                
    # -----------------------------
    # Strategy read APIs
    # -----------------------------
    
    @property
    def universe(self) -> Tuple[str, ...]:
        """Immutable tuple of tradable symbols for the current run."""
        return self._universe
    
    @property
    def market(self) -> Mapping[str, object]:
        """Read-only market snapshot for the current tick."""
        return self._market_view

    def has_symbol(self, symbol: str) -> bool:
        """Check if a symbol is in the current market snapshot."""
        return symbol in self._market_view
    
    def get_bar(self, symbol: str) -> Optional[Bar]:
        """Get the Bar for a symbol, if it exists in the current market snapshot."""

        obj = self._market_view.get(symbol)

        if not isinstance(obj, Bar):
            raise ValueError(f"Market data for symbol '{symbol}' is not a Bar.")
        
        if obj is None:
            raise ValueError(f"Symbol '{symbol}' not found in market snapshot.")

        return self._market_view.get(symbol)
    
    def get_price(self, symbol: str, field: Optional[str] = "close") -> Optional[float]:
        """
        Get the price for a symbol, if it exists in the current market snapshot.
        Supported fields: open, high, low, close, adj_close
        """

        bar = self.get_bar(symbol)
        try:
            px = getattr(bar, field, None)
        except AttributeError:
            raise ValueError(f"Bar has no field '{field}'.")
        
        return float(px)
    

     # -----------------------------
    # Strategy write API (signals buffer)
    # -----------------------------

    def submit_signals(self, strategy_id: str, output: StrategyOutput) -> None:
        """
        Submit the per-tick output for a given strategy.

        Constraints:
        - One output per strategy per tick (last write wins in non-strict mode).
        - Symbols must belong to universe (strict) or will be filtered (non-strict).
        - Weights must be finite numbers (no NaN/inf).
        """
        if self.now is None:
            raise RuntimeError("Context.submit_signals() called before reset_step(now).")

        if not strategy_id:
            raise ValueError("strategy_id must be a non-empty string.")

        cleaned = self._clean_output(output)
        if self._strict and strategy_id in self._signals_by_strategy:
            raise ValueError(f"Duplicate submission for strategy_id='{strategy_id}' at {self.now}.")

        # In non-strict mode, we overwrite (useful during development).
        self._signals_by_strategy[strategy_id] = cleaned

    def collect_signals(self) -> Mapping[str, StrategyOutput]:
        """
        Return a read-only mapping of strategy_id -> StrategyOutput for the current tick.

        The engine should call this after all strategies have run.
        """
        return MappingProxyType(self._signals_by_strategy)

    # -----------------------------
    # Internal helpers
    # -----------------------------

    def _clean_output(self, output: StrategyOutput) -> StrategyOutput:
        if output is None:
            raise ValueError("StrategyOutput cannot be None.")

        weights = output.weights
        if weights is None:
            raise ValueError("StrategyOutput.weights cannot be None.")

        # Filter/validate weights
        u = set(self._universe)
        cleaned: Dict[str, float] = {}
        for sym, w in weights.items():
            if sym not in u:
                if self._strict:
                    raise KeyError(f"Strategy output symbol '{sym}' not in universe.")
                continue

            try:
                wf = float(w)
            except (TypeError, ValueError):
                if self._strict:
                    raise ValueError(f"Non-numeric weight for symbol '{sym}': {w!r}")
                continue

            if not math.isfinite(wf):
                if self._strict:
                    raise ValueError(f"Non-finite weight for symbol '{sym}': {wf}")
                continue

            # Keep zeros out (optional). Helps downstream performance.
            if wf != 0.0:
                cleaned[sym] = wf

        # Optional: enforce a soft convention that weights are "normalized-ish".
        # Hard enforcement is often better in StrategyNode, but you can uncomment if desired.
        # if self._strict:
        #     gross = sum(abs(x) for x in cleaned.values())
        #     if gross > 1.000001:
        #         raise ValueError(f"Gross weight > 1.0 (got {gross}). Normalize in StrategyNode.")

        # Ensure meta is a mapping (and immutable view)
        meta = output.meta if output.meta is not None else {}
        if not isinstance(meta, Mapping):
            if self._strict:
                raise TypeError("StrategyOutput.meta must be a mapping.")
            meta = {}

        return StrategyOutput(weights=MappingProxyType(cleaned), meta=MappingProxyType(dict(meta)))
    

if __name__ == "__main__":
    # -----------------------------
    # Setup
    # -----------------------------
    universe = ["ES", "NQ", "CL"]
    ctx = Context(universe=universe, strict=True)

    ts = pd.Timestamp("2022-01-03 10:00")

    market_snapshot = {
        "ES": Bar(open=4700, high=4710, low=4690, close=4705, volume=1_000),
        "NQ": Bar(open=16000, high=16050, low=15900, close=16020, volume=800),
        "CL": Bar(open=75.0, high=76.0, low=74.5, close=75.4, volume=2_000),
    }

    # -----------------------------
    # Tick 1
    # -----------------------------
    ctx.reset_step(ts)
    ctx.update_market(market_snapshot)

    # Read API checks
    assert ctx.now == ts
    assert ctx.get_price("ES") == 4705
    assert ctx.get_price("CL", field="open") == 75.0
    assert ctx.has_symbol("NQ")
    assert not ctx.has_symbol("GC")

    # Submit strategy outputs
    out_a = StrategyOutput(weights={"ES": 0.6, "NQ": 0.4})
    out_b = StrategyOutput(weights={"CL": -1.0})

    ctx.submit_signals("trend_following", out_a)
    ctx.submit_signals("mean_reversion", out_b)

    signals = ctx.collect_signals()

    assert set(signals.keys()) == {"trend_following", "mean_reversion"}
    assert signals["trend_following"].weights["ES"] == 0.6
    assert signals["mean_reversion"].weights["CL"] == -1.0

    print("Tick 1 passed.")

    # -----------------------------
    # Duplicate submission check
    # -----------------------------
    try:
        ctx.submit_signals("trend_following", out_a)
        raise RuntimeError("Duplicate submission should have failed in strict mode.")
    except ValueError:
        print("Duplicate submission correctly rejected.")

    # -----------------------------
    # Tick 2 (buffer reset check)
    # -----------------------------
    ts2 = pd.Timestamp("2022-01-03 11:00")
    ctx.reset_step(ts2)
    ctx.update_market(market_snapshot)

    assert ctx.now == ts2
    assert len(ctx.collect_signals()) == 0  # previous tick cleared

    ctx.submit_signals(
        "trend_following",
        StrategyOutput(weights={"ES": -0.5}),
    )

    signals = ctx.collect_signals()
    assert list(signals.keys()) == ["trend_following"]
    assert signals["trend_following"].weights["ES"] == -0.5

    print("Tick 2 passed.")

    # -----------------------------
    # Invalid symbol check
    # -----------------------------
    try:
        ctx.submit_signals(
            "bad_strategy",
            StrategyOutput(weights={"INVALID": 1.0}),
        )
        raise RuntimeError("Invalid symbol should have failed in strict mode.")
    except KeyError:
        print("Invalid symbol correctly rejected.")

    print("\nAll Context tests passed successfully.")