"""Factor Calendar 流通股东户数市场代理因子。"""

import numpy as np

from factor_calendar_runtime import Factor


class ShareholderNumberFactor(Factor):
    """以规模和换手活跃度代理流通股东户数。"""

    def calculate(self, factors):
        market_cap = factors["market_cap"] + 0
        turnover = factors["turnover"] + 0
        average_turnover = turnover.groupby(
            level="symbol", sort=False
        ).transform(lambda item: item.rolling(20, min_periods=5).mean())
        size_rank = market_cap.groupby(level="date", sort=False).rank(pct=True)
        activity_rank = average_turnover.groupby(
            level="date", sort=False
        ).rank(pct=True)
        result = 10000 * np.sqrt(size_rank * activity_rank)
        result = result.replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
