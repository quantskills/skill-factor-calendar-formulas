"""Factor Calendar 季度投入资本回报率市场代理因子。"""

import numpy as np

from factor_calendar_runtime import Factor


class SingleReturnOnInvestedCapitalFactor(Factor):
    """以季度价格回报相对资本周转强度代理季度 ROIC。"""

    def calculate(self, factors):
        close = factors["close"] + 0
        turnover = factors["turnover"] + 0
        previous = close.groupby(level="symbol", sort=False).shift(60)
        short_previous = close.groupby(level="symbol", sort=False).shift(20)
        previous = previous.fillna(short_previous).fillna(close)
        quarterly_return = (close / previous - 1).where(
            (close > 0) & (previous > 0)
        )
        capital_turnover = turnover.groupby(
            level="symbol", sort=False
        ).transform(lambda item: item.rolling(60, min_periods=1).mean())
        result = quarterly_return / capital_turnover.replace(0, np.nan)
        result = result.replace([np.inf, -np.inf], np.nan).fillna(0.0)
        result.name = "value"
        return result
