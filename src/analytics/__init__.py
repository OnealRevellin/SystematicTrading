"""
Package: analytics

Responsibility:
    Post-backtest analysis and evaluation of strategy and portfolio performance.
    This package focuses on summarizing and interpreting results, not on real-time
    decision-making.

What belongs here:
    - performance.py:
        * Performance metrics: Sharpe, Sortino, CAGR, volatility, max drawdown.
        * Rolling and aggregate statistics computed after the simulation.
    - attribution.py:
        * Performance attribution by strategy, asset, or risk factor.
        * Decomposition of portfolio returns into contributing components.

Invariants:
    - No impact on trading decisions or execution.
    - Operates on outputs produced by accounting and portfolio layers.
    - Can be recomputed independently from the backtest engine.

Typical outputs:
    - Performance reports and summary tables.
    - Attribution breakdowns for analysis and presentation.
"""
