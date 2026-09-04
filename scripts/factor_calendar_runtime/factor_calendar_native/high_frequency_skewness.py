"""Factor Calendar 收益偏度因子。"""

import numpy as np
import pandas as pd

from factor_calendar_runtime import Factor


class HighFrequencySkewnessFactor(Factor):
    """以日收益滚动偏度代理高频日内收益偏度。"""

    def calculate(self, factors):
        close = factors["close"] + 0
        returns = close.groupby(
            level="symbol", sort=False
        ).pct_change(fill_method=None)
        result = returns.groupby(
            level="symbol", sort=False
        ).transform(
            lambda values: values.rolling(20, min_periods=5).skew()
        )
        result = result.replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
