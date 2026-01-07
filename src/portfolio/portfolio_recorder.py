import pandas as pd
from typing import Dict, Any
from ..backtesting.context import Context
from ..portfolio.master import MasterPortfolio
from ..analytics.performance import PerformanceData


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
        portfolio: MasterPortfolio,
        ctx: Context
    ) -> None:
        self._positions[ts] = portfolio.positions.copy()
        self._metrics[ts] = {
            "cash": portfolio.cash,
            "market_value": portfolio.market_value(ctx),
            "total_equity": portfolio.equity(ctx),
            "fees_paid": portfolio.fees_paid,
        }

    def positions_df(self) -> pd.DataFrame:
        return pd.DataFrame.from_dict(self._positions, orient="index").fillna(0.0).sort_index()

    def metrics_df(self) -> pd.DataFrame:
        df = pd.DataFrame.from_dict(self._metrics, orient="index").sort_index()
        return df

    def to_parquet(self, path: str):
        self.positions_df().to_parquet(path + ".positions.parquet")
        self.metrics_df().to_parquet(path + ".metrics.parquet")

    def export_performance_data(self) -> PerformanceData:
        """
        Export that will be used by analytics consumers.

        Returns a dict with the following keys:
        - `equity`: pd.Series of `total_equity` indexed by timestamp
        - `returns`: pd.Series of period returns (pct_change) indexed by timestamp
        - `positions`: pd.DataFrame of positions over time
        - `metrics`: pd.DataFrame of raw metrics
        """
        metrics = self.metrics_df()
        equity = metrics["total_equity"].copy()
        positions = self.positions_df()

        return PerformanceData(
            equity=equity,
            positions=positions,
            metrics=metrics,
        )