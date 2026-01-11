from __future__ import annotations

from ...backtesting.context import Context, StrategyOutput
from ..base import Strategy


class AlwaysLong(Strategy):
    """
    Example strategy that always generates long signals for all instruments.
    """

    def __init__(self, symbol: str, weight: float = 1.0) -> None:
        self._symbol = symbol
        self._weight = float(weight)

    def on_data(
        self,
        ctx: Context,
    ) -> StrategyOutput:
        """
        Generate long signals for the specified symbol.
        """
        if not ctx.has_symbol(self._symbol):
            return StrategyOutput(weights={})
        
        return StrategyOutput({self._symbol: self._weight})
    
class AlwaysShort(Strategy):
    """
    Example strategy that always generates short signals for all instruments.
    """

    def __init__(self, symbol: str, weight: float = -1.0) -> None:
        self._symbol = symbol
        self._weight = float(weight)

    def on_data(
        self,
        ctx: Context,
    ) -> StrategyOutput:
        """
        Generate short signals for the specified symbol.
        """
        if not ctx.has_symbol(self._symbol):
            return StrategyOutput(weights={})
        
        return StrategyOutput({self._symbol: self._weight})
    

class DollarCostAveraging(Strategy):
    """
    Example strategy that implements Dollar-Cost Averaging (DCA).
    Invests a fixed amount at regular intervals.
    """

    def __init__(
        self, 
        symbol: str, 
        *,
        interval_ticks: int = 20,
        weight: float = 0.1, 
        max_weight: float = 1.0,
    ) -> None:
        self._symbol = symbol
        self._weight = float(weight)
        self._interval_ticks = interval_ticks
        self._max_weight = float(max_weight)
        self._current_year_month = None

        self._current_tick = 0
        self._ctr = 0

    def on_data(
        self,
        ctx: Context,
    ) -> StrategyOutput:
        """
        Generate DCA signals for the specified symbol.
        """
        if not ctx.has_symbol(self._symbol):
            return StrategyOutput(weights={})
                
        if self._weight * self._ctr >= self._max_weight:
            return StrategyOutput(weights={self._symbol: self._max_weight})
        
        if self._ctr * self._weight < self._max_weight:
            if self._current_tick % self._interval_ticks == 0:
                self._ctr += 1

        self._current_tick += 1

        return StrategyOutput(weights={self._symbol: self._weight * self._ctr})