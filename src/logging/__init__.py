"""
Package: logging

Responsibility:
    Structured logging and diagnostics for the backtesting system.
    Provides consistent and configurable logging across all layers.

What belongs here:
    - Logger configuration (format, levels, handlers).
    - Utilities for structured logs (per strategy, per tick).
    - Optional performance and timing diagnostics.

Invariants:
    - No business logic.
    - Logging should not affect determinism of simulations.
"""
