"""Factor Calendar 多时域移动平均动量因子。"""

import numpy as np
import pandas as pd

from factor_calendar_runtime import Factor


class TrendFactor(Factor):
    """以 5、10、20 日标准化移动平均刻画多时域趋势。"""

    def calculate(self, factors):
        close = factors["close"] + 0
        scores = []
        for window in (5, 10, 20):
            moving_average = close.groupby(
                level="symbol", sort=False
            ).transform(
                lambda values: values.rolling(
                    window, min_periods=max(2, window // 2)
                ).mean()
            )
            scores.append(
                ((close - moving_average) / moving_average).where(
                    moving_average > 0
                )
            )
        result = sum(scores) / len(scores)
        result = result.replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
