import pandas as pd
from typing import Dict
from ..backtesting.context import Context
from .master import MasterPorfolio


class PortfolioRecorder:
    """
    Records portfolio value over time.
    """

    def __init__(self) -> None:
        self._positions: Dict[pd.Timestamp, Dict[str, float]] = {}
        self._metrics: Dict[pd.Timestamp, Dict[str, float]] = {}

    def record(
        self,
        ts: pd.Timestamp,
        portfolio: MasterPorfolio,
        ctx: Context
    ) -> None:
        self._positions[ts] = portfolio.positions.copy()
        self._metrics[ts] = {
            "cash": portfolio.cash,
            "total_equity": portfolio.equity(ctx),
        }

