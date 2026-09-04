"""Factor Calendar 分析师覆盖率市场代理因子。"""

import numpy as np

from factor_calendar_runtime import Factor


class TotalAnalystCoverageFactor(Factor):
    """使用二十日平均换手率相对市场均值代理分析师覆盖率。"""

    def calculate(self, factors):
        turnover = factors["turnover"] + 0
        average_turnover = turnover.groupby(
            level="symbol", sort=False
        ).transform(
            lambda item: item.rolling(20, min_periods=10).mean()
        )
        market_turnover = average_turnover.groupby(
            level="date", sort=False
        ).transform("mean")
        result = (average_turnover / market_turnover).where(
            market_turnover > 0
        )
        result = result.replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
