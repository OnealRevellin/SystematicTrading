"""
Package: portfolio

Responsibility:
    Capital ownership and position management layer.
    This package is the single source of truth for cash, positions, and target
    allocations across all strategies.

What belongs here:
    - master.py:
        * MasterPortfolio owning all capital and net positions.
    - portfolio.py:
        * Sub-portfolio or strategy-level views for attribution.
    - allocation.py:
        * Capital allocation logic across strategies.
        * Conversion of normalized strategy outputs into target notionals.

Invariants:
    - Capital is owned centrally (never by strategies).
    - Positions are netted across strategies.
    - Allocation decisions are explicit and auditable.
"""
