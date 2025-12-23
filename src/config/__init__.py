"""
Package: config

Responsibility:
    Centralized configuration of the backtesting and trading system.
    This package defines how simulations, strategies, risk limits, and execution
    parameters are specified and reproduced.

What belongs here:
    - Configuration schemas (dataclasses, pydantic models, or similar).
    - Loading and validation of configuration files (YAML/JSON).
    - Default parameter sets for backtests and experiments.

Invariants:
    - No execution logic.
    - Configuration is immutable once a backtest starts.
    - Enables reproducibility of experiments.
"""
