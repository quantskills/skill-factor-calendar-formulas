"""Factor Calendar 单季度投入资本回报率市场代理因子。"""

import numpy as np
from factor_calendar_runtime import Factor


class QuarterlyReturnOnInvestedCapitalFactor(Factor):
    """以季度收益相对资金周转强度代理资本回报效率。"""

    def calculate(self, factors):
        close = factors["close"] + 0
        turnover = factors["turnover"] + 0
        market_cap = factors["market_cap"] + 0
        previous = close.groupby(level="symbol", sort=False).shift(63)
        quarterly_return = (close / previous - 1).where((close > 0) & (previous > 0))
        capital_turnover = turnover.groupby(level="symbol", sort=False).transform(lambda item: item.rolling(63, min_periods=20).mean())
        efficiency = quarterly_return / capital_turnover.replace(0, np.nan)
        result = efficiency + np.log(market_cap.where(market_cap > 0)) * 1e-12
        result = result.replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
