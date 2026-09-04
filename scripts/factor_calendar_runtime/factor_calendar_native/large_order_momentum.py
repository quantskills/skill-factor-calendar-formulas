"""Factor Calendar 大单成交量价动量因子。"""

import numpy as np
import pandas as pd

from factor_calendar_runtime import Factor


class LargeOrderMomentumFactor(Factor):
    """以成交额横截面分位加权日内收益近似大单量价动量。"""

    def calculate(self, factors):
        open_price = factors["open"] + 0
        close = factors["close"] + 0
        amount = factors["amount"] + 0
        daily_return = (close / open_price - 1).where(
            (close > 0) & (open_price > 0)
        )
        amount_percentile = amount.groupby(
            level="date", sort=False
        ).rank(pct=True)
        weighted_return = daily_return * amount_percentile
        log_growth = np.log1p(weighted_return.clip(lower=-0.999999))
        rolling_growth = log_growth.groupby(
            level="symbol", sort=False
        ).transform(
            lambda values: values.rolling(20, min_periods=5).sum()
        )
        result = np.expm1(rolling_growth)
        result = result.replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
