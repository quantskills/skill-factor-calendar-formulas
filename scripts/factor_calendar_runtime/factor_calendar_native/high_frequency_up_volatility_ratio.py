"""Factor Calendar 高频上行已实现波动占比因子（日频基础行情代理）。"""

import numpy as np
import pandas as pd

from factor_calendar_runtime import Factor


class HighFrequencyUpVolatilityRatioFactor(Factor):
    """以日收益替代分钟收益计算二十日上行已实现波动占比。"""

    def calculate(self, factors):
        close = factors["close"] + 0
        previous_close = close.groupby(level="symbol", sort=False).shift(1)
        daily_return = (close / previous_close - 1).where(
            (close > 0) & (previous_close > 0)
        )
        squared_return = daily_return**2
        upward_squared_return = squared_return.where(daily_return > 0, 0)
        upward_variance = upward_squared_return.groupby(
            level="symbol", sort=False
        ).transform(lambda values: values.rolling(20, min_periods=20).sum())
        total_variance = squared_return.groupby(
            level="symbol", sort=False
        ).transform(lambda values: values.rolling(20, min_periods=20).sum())
        result = (upward_variance / total_variance).where(total_variance > 0)
        result = result.clip(0, 1).replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
