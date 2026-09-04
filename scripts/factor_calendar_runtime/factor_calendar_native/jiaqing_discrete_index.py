"""Factor Calendar 佳庆波动率离散指标。"""

import numpy as np
import pandas as pd

from factor_calendar_runtime import Factor


class JiaqingDiscreteIndexFactor(Factor):
    """十日振幅 EMA 相对十日前水平的百分比变化。"""

    def calculate(self, factors):
        amplitude = (factors["high"] + 0) - (factors["low"] + 0)
        rem = amplitude.groupby(level="symbol", sort=False).transform(
            lambda item: item.ewm(
                span=10, adjust=False, min_periods=10
            ).mean()
        )
        delayed_rem = rem.groupby(level="symbol", sort=False).shift(10)
        result = (100 * (rem - delayed_rem) / delayed_rem).where(
            delayed_rem > 0
        )
        result = result.replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
