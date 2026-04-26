from typing import Dict, Any

import matplotlib.pyplot as plt
import pandas as pd

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
    
    def plot_equity_line(self) -> None:
        plt.figure(figsize=(12, 6))
    
        # Get equity data
        equity = self.metrics_df()["total_equity"]
        
        # Calculate running maximum (high watermark)
        running_max = equity.expanding().max()
        
        # Calculate drawdown
        drawdown = (equity - running_max) / running_max
        
        # Plot equity curve
        plt.plot(equity, linewidth=2, color="#1f77b4", label="Total Equity")
        
        # Fill drawdown area
        plt.fill_between(equity.index, equity, running_max, 
                        where=(equity <= running_max), 
                        alpha=0.3, color="#d62728", label="Drawdown")
        
        # Calculate and display max drawdown
        max_drawdown = drawdown.min()
        max_drawdown_pct = max_drawdown * 100
        max_drawdown_idx = drawdown.idxmin()
        max_drawdown_value = equity.loc[max_drawdown_idx]
        
        plt.axhline(y=running_max.iloc[-1], color="gray", linestyle="--", 
                    alpha=0.5, linewidth=1)
        
        # Mark max drawdown point with a cross/arrow
        plt.plot(
            max_drawdown_idx, 
            max_drawdown_value, 
            marker='X', 
            markersize=12, 
            color="red", 
            markeredgecolor="darkred", 
            markeredgewidth=1.5, 
            label=f"Max Drawdown ({max_drawdown_pct:.2f}%)"
        )

        plt.annotate(
            f"Max DD\n{max_drawdown_pct:.2f}%", 
            xy=(max_drawdown_idx, max_drawdown_value),
            xytext=(10, -20), 
            textcoords="offset points",
            bbox=dict(boxstyle="round,pad=0.5", facecolor="yellow", alpha=0.7),
            arrowprops=dict(arrowstyle="->", color="red", lw=1.5)
        )
        
        plt.xlabel("Timestamp", fontsize=12)
        plt.ylabel("Total Equity ($)", fontsize=12)
        
        plt.title(
            f"Strategy Equity Curve | Max Drawdown: {max_drawdown_pct:.2f}%", 
            fontsize=14, 
            fontweight="bold"
        )

        plt.grid(True, alpha=0.3)
        plt.legend(loc="upper left")
        plt.tight_layout()
        plt.show()