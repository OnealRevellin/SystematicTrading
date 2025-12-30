"""
execution.broker

Execution logic + fee model.
"""

from __future__ import annotations
from typing import List

from .order import Order, OrderType
from .fill import Fill
from ..backtesting.context import Context


class Broker:
    """
    Simple broker model.

    Responsibilities:
    - decide if order fills
    - decide execution price
    - compute fees
    """

    def __init__(
        self,
        *,
        fee_rate: float = 0.0,
        min_fee: float = 0.0
    ) -> None:
        self._fee_rate = float(fee_rate)
        self._min_fee = float(min_fee)

    def execute_orders(
        self,
        orders: List[Order],
        ctx: Context
    ) -> List[Fill]:
        fills: List[Fill] = []

        for order in orders:
            if not ctx.has_symbol(order.symbol):
                continue  # skip unknown symbols

            if order.order_type != OrderType.MARKET:
                raise NotImplementedError(
                    "Market order execution not implemented yet."
                )
            
            price = ctx.get_price(order.symbol, "close")
            notional = price * abs(order.quantity)
            fee = max(self._fee_rate * notional, self._min_fee)

            fills.append(
                Fill(
                    symbol=order.symbol,
                    quantity=order.quantity,
                    price=price,
                    fee=fee,
                    order_type=order.order_type,
                    time_in_force=order.time_in_force,
                    order_id=order.order_id
                )
            )

        return fills
    

if __name__ == "__main__":
    from ..backtesting.context import Context
    import pandas as pd
    from ..data.market_data import Bar

    broker = Broker(fee_rate=0.001, min_fee=1.0)
    print(broker)

    ctx = Context(universe=["ES", "NQ", "CL"], strict=True)

    ts = pd.Timestamp("2022-01-03 10:00")

    market_snapshot = {
        "ES": Bar(open=4700, high=4710, low=4690, close=4705, volume=1_000),
        "NQ": Bar(open=16000, high=16050, low=15900, close=16020, volume=800),
        "CL": Bar(open=75.0, high=76.0, low=74.5, close=75.4, volume=2_000),
    }

    # -----------------------------
    # Tick 1
    # -----------------------------
    ctx.reset_step(ts)
    ctx.update_market(market_snapshot)

    orders_list = [
        Order(symbol="ES", quantity=100, order_type=OrderType.MARKET),
        Order(symbol="NQ", quantity=50, order_type=OrderType.MARKET),
    ]

    fills = broker.execute_orders(orders_list, ctx)
    for fill in fills:
        print(fill)