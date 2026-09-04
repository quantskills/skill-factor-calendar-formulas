"""Factor Calendar 个股特质波动率因子。"""

from factor_calendar_runtime import Factor

from factor_calendar_batch10_utils import (
    finish,
    rolling_residuals,
    rolling_std,
    stock_and_market_returns,
)


class IdiosyncraticVolatilityFactor(Factor):
    """CAPM 滚动回归残差的近一个月标准差。"""

    def calculate(self, factors):
        stock_return, market_return = stock_and_market_returns(factors["close"] + 0)
        residual = rolling_residuals(stock_return, market_return, 60)
        return finish(rolling_std(residual, 20, min_periods=20, ddof=1))
