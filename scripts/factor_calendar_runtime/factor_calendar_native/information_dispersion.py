"""Factor Calendar 收益动量一致性因子。"""

import numpy as np
import pandas as pd

from factor_calendar_runtime import Factor


class InformationDispersionFactor(Factor):
    """累计收益方向乘以负收益日占比减正收益日占比。"""

    def calculate(self, factors):
        close = factors["close"] + 0
        daily_return = close.groupby(
            level="symbol", sort=False
        ).pct_change(fill_method=None)
        positive = (daily_return > 0).astype(float).where(
            daily_return.notna()
        )
        negative = (daily_return < 0).astype(float).where(
            daily_return.notna()
        )
        positive_share = positive.groupby(
            level="symbol", sort=False
        ).transform(
            lambda values: values.rolling(20, min_periods=5).mean()
        )
        negative_share = negative.groupby(
            level="symbol", sort=False
        ).transform(
            lambda values: values.rolling(20, min_periods=5).mean()
        )
        delayed_close = close.groupby(level="symbol", sort=False).shift(20)
        momentum = (close / delayed_close - 1).where(
            (close > 0) & (delayed_close > 0)
        )
        result = np.sign(momentum) * (negative_share - positive_share)
        result = result.replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
