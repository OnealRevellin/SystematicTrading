"""
Package: metrics

Responsibility:
    Online metrics computed during the backtest run.
    These metrics are typically lightweight and updated incrementally per tick.

What belongs here:
    - stats.py:
        * Rolling statistics (returns, volatility, drawdown).
        * Lightweight metrics needed during the simulation.

Invariants:
    - Computed during the backtest (not post-analysis).
    - Must be fast and memory-efficient.
    - Feeds risk management and monitoring.
"""
