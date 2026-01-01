"""
Global portfolio owning capital and positions.

Later on, I'll introduce portfolio.py whihch will represent subportfolios allowing
us to split exposure/PnLs/risk metrics... between subportfolios.
"""

from __future__ import annotations

from typing import Dict, List, Optional

from ..backtesting.context import Context
from ..execution.order import Order, OrderType, TimeInForce
from ..execution.fill import Fill


class MasterPorfolio:

    __slots__ = (
        "_cash",
        "_positions",
        "_instrument_rules",
        "_default_order_type",
        "_default_tif",
    )

    def __init__(
        self,
        *,
        initial_cash: float = 1_000_000.0,
        instrument_rules: Optional[Dict[str, Dict[str, float | bool]]] = None,
        default_order_type: OrderType = OrderType.MARKET,
        default_time_in_force: TimeInForce = TimeInForce.DAY
    ):
        self._cash = float(initial_cash)
        self._positions: Dict[str, float] = {}
        self._instrument_rules: Dict[str, Dict[str, float | bool]] = instrument_rules
        self._default_order_type: OrderType = default_order_type
        self._default_tif: TimeInForce = default_time_in_force

    # -----------------------------
    # Getter & Setter
    # -----------------------------

    @property
    def cash(self) -> float:
        return self._cash

    @property
    def positions(self) -> Dict[str, float]:
        return dict(self._positions)
    
    def equity(self, ctx: Context) -> float:
        """
        Equity = cash + sum(positions * closing_price)
        """

        eq = self._cash
        for sym, qty in self._positions.items():
            if ctx.has_symbol(sym):
                eq += qty * ctx.get_price(sym, "close")

        return eq
    
    # -----------------------------
    # Sizing helpers
    # -----------------------------
    
    def _compute_unit_size(self, sym: str, qty: float) -> float:

        rules = self._instrument_rules.get(sym, {})
        in_lots = rules.get("in_lots", False)
        lot_size = float(rules.get("lot_size", 1.0))

        if not in_lots:
            return qty
        
        if lot_size <= 0.0:
            raise ValueError(f"Invalid lot_size for symbol '{sym}': {lot_size}")
        
        return float(lot_size * qty)

    # -----------------------------
    # Oder generation
    # -----------------------------

    def build_orders(
        self,
        allocation: Dict[str, float],
        ctx: Context,
        *,
        order_type: Optional[OrderType] = None,
        time_in_force: Optional[TimeInForce] = None,
        price_time: str = "close",
        
    ) -> List[Order]:
        """
        Convert target weights into delta Orders.

        Parameters
        ----------
        allocation:
            dict[symbol: target_weight]
        order_type / time_in_force:
            Overrides for generated orders (defaults set in __init__).
        Returns
        -------
        List[Order]
        """
        if not allocation:
            return []

        ot = order_type or self._default_order_type
        tif = time_in_force or self._default_tif

        eq = self.equity(ctx)
        if eq <= 0.0:
            return []

        # 1) Compute target position per symbol (in units)
        target_pos: Dict[str, float] = {}

        for sym, weight in allocation.items():
            if not ctx.has_symbol(sym):
                continue

            px = ctx.get_price(sym, price_time)
            if px <= 0.0:
                continue

            # Raw units implied by target weight
            target_value = float(weight) * eq
            raw_units = target_value / px

            # Apply instrument conversion rule
            target_units = self._compute_unit_size(sym, raw_units)

            # Drop tiny values to reduce churn
            if abs(target_units) < 1e-12:
                target_units = 0.0

            target_pos[sym] = target_units

        # 2) Compute delta vs current positions
        orders: List[Order] = []
        for sym in (set(self._positions) | set(target_pos)):
            cur = self._positions.get(sym, 0.0)
            tgt = target_pos.get(sym, 0.0)
            delta = tgt - cur

            if abs(delta) <= 1e-12:
                continue

            orders.append(
                Order(
                    symbol=sym,
                    quantity=delta,
                    order_type=ot,
                    time_in_force=tif,
                    limit_price=None,
                    stop_price=None,
                    client_order_id=None,
                )
            )

        return orders

    # -----------------------------
    # Fill application
    # -----------------------------

    def apply_fills(self, fills: List[Fill]) -> None:
        """
        Apply fills to cash and positions.
        """
        for fill in fills:
            if fill.quantity == 0.0:
                continue

            self._cash -= fill.quantity * fill.price
            self._cash -= fill.fee

            self._positions[fill.symbol] = self._positions.get(fill.symbol, 0.0) + fill.quantity

            if abs(self._positions[fill.symbol]) < 1e-12:
                del self._positions[fill.symbol]