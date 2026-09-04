"""Factor Calendar 归母净利润增长率因子。"""

import numpy as np
import pandas as pd

from factor_calendar_runtime import Factor


class NetProfitGrowthRateFactor(Factor):
    """以约一季度前的归母净利润作为有限回溯下的增长代理。"""

    def calculate(self, factors):
        current = factors["net_profit_parent"] + 0
        previous = current.groupby(level="symbol", sort=False).shift(63)
        result = ((current - previous) / previous.abs()).where(
            previous != 0
        )
        result = result.replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
