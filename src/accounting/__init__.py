"""
Package: accounting

Responsibility:
    Economic truth layer of the system. This package is responsible for transforming
    executed trades and portfolio states into financial reality: PnL, costs, funding,
    and exposures.

What belongs here:
    - pnl.py:
        * Realized and unrealized PnL calculations.
        * Mark-to-market logic.
        * Aggregation by instrument and (when available) by strategy.
    - costs.py:
        * Transaction cost models: commissions, fees, funding, borrow costs.
        * Application of costs to fills/trades in a consistent and auditable manner.
    - exposure.py:
        * Portfolio exposures: gross/net exposure, leverage, delta notionals.
        * Aggregations by asset, sector, or strategy to support risk and analytics.

Invariants:
    - Does not generate orders or decide allocations.
    - Consumes execution results (fills) and portfolio states.
    - Deterministic, auditable, and reproducible outputs.

Typical outputs:
    - Equity curve and PnL time series.
    - Cost breakdowns.
    - Exposure time series used by risk and analytics.
"""
