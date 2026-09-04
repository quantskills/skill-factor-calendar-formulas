"""Factor Calendar 普通股股东权益回报率市场代理因子。"""

import numpy as np

from factor_calendar_runtime import Factor


class CommonStockReturnFactor(Factor):
    """使用二十日收益率除以同期波动率代理股东资本回报。"""

    def calculate(self, factors):
        close = factors["close"] + 0
        previous = close.groupby(level="symbol", sort=False).shift(20)
        period_return = (close / previous - 1).replace(
            [np.inf, -np.inf], np.nan
        ).fillna(0.0)
        daily_return = close.groupby(level="symbol", sort=False).pct_change()
        volatility = daily_return.groupby(
            level="symbol", sort=False
        ).transform(lambda item: item.rolling(20, min_periods=2).std())
        result = (period_return / volatility).where(volatility > 0)
        result = result.replace([np.inf, -np.inf], np.nan).fillna(0.0)
        result.name = "value"
        return result
