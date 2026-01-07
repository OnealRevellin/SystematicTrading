from dataclasses import dataclass
from typing import Optional, Dict, Any

import pandas as pd


@dataclass
class PerformanceData:
	"""Container for backtest performance outputs consumed by analytics.

	Fields are intentionally simple pandas objects so analytics functions
	remain pure and serializable.
	"""
	equity: pd.Series
	positions: pd.DataFrame
	metrics: pd.DataFrame
	summary: Optional[Dict[str, Any]] = None
	meta: Optional[Dict[str, Any]] = None


class PerformanceAnalyzer:
    """
    Analyze performance data and compute common metrics.
    """

    def __init__(
        self,
        PerformanceData: PerformanceData,
    ):
        self._data = PerformanceData

    def compute_cagr(self) -> float:
        """
        Compute Compound Annual Growth Rate (CAGR).
        """
        equity = self._data.equity
        if equity.empty:
            return 0.0

        start_value = equity.iloc[0]
        end_value = equity.iloc[-1]
        num_years = (equity.index[-1] - equity.index[0]).days / 365.25
        if start_value <= 0 or num_years <= 0:
            return 0.0

        cagr = (end_value / start_value) ** (1 / num_years) - 1
        return cagr
    
    def compute_max_drawdown(self) -> float:
        """
        Compute Maximum Drawdown.
        """
        equity = self._data.equity
        if equity.empty:
            return 0.0

        rolling_max = equity.cummax()
        drawdowns = (equity - rolling_max) / rolling_max
        max_drawdown = drawdowns.min()
        return max_drawdown

    def compute_sharpe_ratio(self, risk_free_rate: float = 0.0) -> float:
        """
        Compute Sharpe Ratio.
        """
        returns = self._data.equity.pct_change().dropna()
        if returns.empty:
            return 0.0

        excess_returns = returns - risk_free_rate / 252  # assuming daily returns
        avg_excess_return = excess_returns.mean()
        std_excess_return = excess_returns.std()

        if std_excess_return == 0:
            return 0.0

        sharpe_ratio = (avg_excess_return / std_excess_return) * (252 ** 0.5)  # annualized
        return sharpe_ratio

if __name__ == "__main__":
    import pandas as pd

    # Example usage
    dates = pd.date_range(start="2020-01-01", periods=5, freq='D')
    equity = pd.Series([1000, 1100, 1050, 1200, 1150], index=dates)
    positions = pd.DataFrame()
    metrics = pd.DataFrame()

    perf_data = PerformanceData(
        equity=equity,
        positions=positions,
        metrics=metrics
    )

    analyzer = PerformanceAnalyzer(perf_data)
    print("CAGR:", analyzer.compute_cagr())
    print("Max Drawdown:", analyzer.compute_max_drawdown())
    print("Sharpe Ratio:", analyzer.compute_sharpe_ratio(risk_free_rate=0.04))
