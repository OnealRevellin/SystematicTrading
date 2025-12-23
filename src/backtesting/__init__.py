"""
Package: backtesting

Responsibility:
    Core orchestration layer of the backtesting system. This package controls the
    simulation timeline, coordinates data, strategies, allocation, execution, and
    accounting in a deterministic and reproducible manner.

What belongs here:
    - clock.py:
        * Definition of the simulation timeline.
        * Single source of truth for time progression.
    - context.py:
        * Read-only market view exposed to strategies.
        * Per-tick buffer for collecting strategy outputs (signals / weights).
    - engine.py:
        * Main event loop.
        * Orchestration of multi-strategy evaluation, risk, allocation, execution,
          portfolio updates, and accounting.

Invariants:
    - No trading logic inside strategies is duplicated here.
    - Capital is centrally owned and managed (never by strategies).
    - Strict ordering of operations per simulation step.

Typical outputs:
    - Complete backtest results: trades, portfolio states, accounting outputs.
"""
