"""Factor Calendar 残差市值偏离度市场代理因子。"""

import numpy as np

from factor_calendar_runtime import Factor


class SpecificMarketCapitalizationFactor(Factor):
    """使用个股对数市值相对每日市场中位数的偏离。"""

    def calculate(self, factors):
        market_cap = factors["market_cap"] + 0
        log_cap = np.log(market_cap.where(market_cap > 0))
        market_median = log_cap.groupby(
            level="date", sort=False
        ).transform("median")
        result = log_cap - market_median
        result = result.replace([np.inf, -np.inf], np.nan).fillna(0.0)
        result.name = "value"
        return result
