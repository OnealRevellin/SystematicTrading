"""
Package: data

Responsibility:
    Market data access and preparation layer. Provides a clean, time-aligned stream
    of market data to the backtesting engine.

What belongs here:
    - market_data.py:
        * DataHandler / iterator aligned with the Clock.
        * Access to OHLCV, prices, and precomputed features.
    - Storage and loading logic (CSV, Parquet, database, API).
    - Optional resampling or alignment utilities.

Invariants:
    - Read-only from the engine/strategy perspective.
    - No trading or portfolio logic.
    - Data is aligned to the simulation timeline (Clock-driven).

Typical outputs:
    - Per-tick market snapshots consumed by Context.
"""
