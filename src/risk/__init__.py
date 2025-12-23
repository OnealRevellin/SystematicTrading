"""
Package: risk

Responsibility:
    Risk control layer enforcing constraints before and after capital allocation.
    Ensures that strategy and portfolio risk limits are respected.

What belongs here:
    - risk_manager.py:
        * Strategy-level risk checks (signal limits, turnover, concentration).
    - global_risk.py:
        * Cross-strategy and portfolio-level risk controls
          (gross/net exposure, leverage, correlations).

Invariants:
    - No alpha generation.
    - No execution logic.
    - Can only scale, block, or modify proposed allocations.
"""
