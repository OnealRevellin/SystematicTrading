"""
Package: strategy

Responsibility:
    Alpha generation layer. Contains all trading strategies and the infrastructure
    required to standardize their outputs.

What belongs here:
    - base.py:
        * Abstract strategy interface.
        * Defines how strategies consume Context and produce outputs.
    - node.py:
        * StrategyNode wrapper for normalization, validation, and bookkeeping.
        * Isolates strategy-specific state and metrics.
    - signals.py:
        * Definitions of signal and strategy output structures.

Invariants:
    - Strategies do not own capital.
    - Strategies do not place orders.
    - Strategies only emit normalized intents (signals, weights, scores).
"""
