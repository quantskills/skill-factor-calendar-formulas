"""Factor Calendar 投入资本回报率变动市场代理因子。"""

import numpy as np

from factor_calendar_runtime import Factor


class QualityReturnOnInvestedCapitalFactor(Factor):
    """以短期与季度资本回报效率之差代理 ROIC 变化。"""

    def calculate(self, factors):
        close = factors["close"] + 0
        turnover = factors["turnover"] + 0
        previous_short = close.groupby(level="symbol", sort=False).shift(20)
        previous_long = close.groupby(level="symbol", sort=False).shift(60)
        previous_short = previous_short.fillna(close)
        previous_long = previous_long.fillna(previous_short)
        short_return = (close / previous_short - 1).where(
            (close > 0) & (previous_short > 0)
        )
        long_return = (close / previous_long - 1).where(
            (close > 0) & (previous_long > 0)
        )
        short_turnover = turnover.groupby(
            level="symbol", sort=False
        ).transform(lambda item: item.rolling(20, min_periods=1).mean())
        long_turnover = turnover.groupby(
            level="symbol", sort=False
        ).transform(lambda item: item.rolling(60, min_periods=1).mean())
        short_efficiency = short_return / short_turnover.replace(0, np.nan)
        long_efficiency = long_return / long_turnover.replace(0, np.nan)
        result = short_efficiency - long_efficiency
        result = result.replace([np.inf, -np.inf], np.nan).fillna(0.0)
        result.name = "value"
        return result
