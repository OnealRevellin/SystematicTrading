"""
Package: common

Responsibility:
    Shared domain objects and utilities used across multiple layers of the system.
    This package exists to avoid circular dependencies and duplicated definitions.

What belongs here:
    - Core data models (e.g. Bar, MarketSnapshot, Signal, StrategyOutput).
    - Shared enums, constants, and lightweight helpers.
    - Types used by multiple packages (execution, portfolio, accounting, strategy).

Invariants:
    - No business logic tied to a specific layer.
    - No side effects or stateful services.
    - Pure, reusable components only.
"""
