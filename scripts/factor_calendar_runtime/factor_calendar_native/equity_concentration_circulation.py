"""Factor Calendar 流通股股权集中度Top3市场代理因子。"""

import numpy as np

from factor_calendar_runtime import Factor


class EquityConcentrationCirculationFactor(Factor):
    """使用低换手率和低换手波动代理稳定集中持股。"""

    def calculate(self, factors):
        turnover = factors["turnover"] + 0
        mean_turnover = turnover.groupby(
            level="symbol", sort=False
        ).transform(lambda item: item.rolling(20, min_periods=1).mean())
        turnover_std = turnover.groupby(
            level="symbol", sort=False
        ).transform(lambda item: item.rolling(20, min_periods=2).std())
        level_rank = mean_turnover.groupby(
            level="date", sort=False
        ).rank(pct=True)
        stability_rank = turnover_std.groupby(
            level="date", sort=False
        ).rank(pct=True)
        result = 1 - (level_rank + stability_rank.fillna(0.5)) / 2
        result = result.replace([np.inf, -np.inf], np.nan).fillna(0.0)
        result.name = "value"
        return result
