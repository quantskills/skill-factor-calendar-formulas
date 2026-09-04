"""Factor Calendar 日内开盘净委买增额成交额比率代理因子。"""

import numpy as np
import pandas as pd

from factor_calendar_runtime import Factor


class NetBidIncreaseRatioFactor(Factor):
    """以开收盘方向在日内振幅中的位置代理净委买增额比率。"""

    def calculate(self, factors):
        open_price = factors["open"] + 0
        high = factors["high"] + 0
        low = factors["low"] + 0
        close = factors["close"] + 0
        price_range = high - low
        daily_ratio = ((close - open_price) / price_range).where(
            price_range > 0
        )
        result = daily_ratio.groupby(
            level="symbol", sort=False
        ).transform(
            lambda values: values.rolling(20, min_periods=5).mean()
        )
        result = result.replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
