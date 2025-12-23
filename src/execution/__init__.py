"""
Package: execution

Responsibility:
    Trade execution simulation. Translates target positions or orders into executed
    trades while modeling realistic market frictions.

What belongs here:
    - order.py:
        * Order models (market, limit, size, direction, metadata).
    - broker.py:
        * Execution logic (fills, partial fills, latency).
    - slippage.py:
        * Slippage and market impact models.
    - fill.py:
        * Executed trade representation (price, quantity, fees, timestamp).

Invariants:
    - Stateless with respect to capital ownership.
    - Does not decide position sizing or allocation.
    - Produces execution results consumed by portfolio and accounting.

Typical outputs:
    - Fills / trades with execution details and costs.
"""
