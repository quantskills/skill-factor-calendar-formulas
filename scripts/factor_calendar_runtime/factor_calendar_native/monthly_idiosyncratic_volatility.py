"""Factor Calendar 月度加权特质波动率因子。"""

import numpy as np

from factor_calendar_runtime import Factor

from factor_calendar_batch10_utils import finish, rolling_residuals, stock_and_market_returns


class MonthlyIdiosyncraticVolatilityFactor(Factor):
    """近一个月 CAPM 残差平方的线性时间加权均方根。"""

    def calculate(self, factors):
        stock_return, market_return = stock_and_market_returns(factors["close"] + 0)
        residual = rolling_residuals(stock_return, market_return, 60)
        window = 20
        weights = np.arange(1, window + 1, dtype=float)
        weights /= weights.sum()
        variance = residual.groupby(level="symbol", sort=False).transform(
            lambda item: (item**2).rolling(
                window, min_periods=window
            ).apply(lambda values: np.dot(values, weights), raw=True)
        )
        return finish(np.sqrt(variance.where(variance >= 0)))
