"""Factor Calendar 前三大自由流通股东持股比例市场代理因子。"""

import numpy as np
from factor_calendar_runtime import Factor


class Top3FreeFloatShareRatioFactor(Factor):
    """以公司规模和低换手特征代理自由流通股权集中度。"""

    def calculate(self, factors):
        market_cap = factors["market_cap"] + 0
        turnover = factors["turnover"] + 0
        average_turnover = turnover.groupby(level="symbol", sort=False).transform(lambda item: item.rolling(20, min_periods=5).mean())
        size_rank = market_cap.groupby(level="date", sort=False).rank(pct=True)
        stability_rank = (-average_turnover).groupby(level="date", sort=False).rank(pct=True)
        result = 0.6 * size_rank + 0.4 * stability_rank + np.log(market_cap.where(market_cap > 0)) * 1e-12
        result = result.replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
