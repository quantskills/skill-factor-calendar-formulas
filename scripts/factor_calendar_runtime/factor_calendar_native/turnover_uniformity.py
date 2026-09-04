"""Factor Calendar 换手率分布离散度因子。"""

import numpy as np
import pandas as pd

from factor_calendar_runtime import Factor


class TurnoverUniformityFactor(Factor):
    """以日换手率的滚动变异系数代理日内换手分布离散度。"""

    def calculate(self, factors):
        turnover = factors["turnover"] + 0
        rolling_mean = turnover.groupby(
            level="symbol", sort=False
        ).transform(
            lambda values: values.rolling(20, min_periods=5).mean()
        )
        rolling_std = turnover.groupby(
            level="symbol", sort=False
        ).transform(
            lambda values: values.rolling(20, min_periods=5).std(ddof=0)
        )
        result = (rolling_std / rolling_mean.abs()).where(
            rolling_mean != 0
        )
        result = result.replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
