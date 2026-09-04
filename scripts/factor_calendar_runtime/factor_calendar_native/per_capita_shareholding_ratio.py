"""Factor Calendar 股东户均持股比例市场代理因子。"""

import numpy as np

from factor_calendar_runtime import Factor


class PerCapitaShareholdingRatioFactor(Factor):
    """以规模和换手活跃度估计股东户数，再计算其倒数。"""

    def calculate(self, factors):
        market_cap = factors["market_cap"] + 0
        turnover = factors["turnover"] + 0
        average_turnover = turnover.groupby(
            level="symbol", sort=False
        ).transform(lambda item: item.rolling(20, min_periods=5).mean())
        size_rank = market_cap.groupby(
            level="date", sort=False
        ).rank(pct=True)
        activity_rank = average_turnover.groupby(
            level="date", sort=False
        ).rank(pct=True)
        estimated_shareholder_count = 10000 * np.sqrt(
            (size_rank * activity_rank).where(
                (size_rank > 0) & (activity_rank > 0)
            )
        )
        result = 1 / estimated_shareholder_count
        result = result.replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
