"""Factor Calendar 开盘时段主动买入强度因子。"""

import numpy as np
import pandas as pd

from factor_calendar_runtime import Factor


class OpeningBuyIntentionFactor(Factor):
    """综合隔夜跳空与日内价格位置衡量开盘买入意愿。"""

    def calculate(self, factors):
        open_price = factors["open"] + 0
        high = factors["high"] + 0
        low = factors["low"] + 0
        close = factors["close"] + 0
        previous_close = close.groupby(level="symbol", sort=False).shift(1)
        overnight_return = (open_price / previous_close - 1).where(
            (open_price > 0) & (previous_close > 0)
        )
        price_range = high - low
        intraday_position = ((close - open_price) / price_range).where(
            price_range > 0
        )
        daily_strength = overnight_return.fillna(0) + intraday_position
        result = daily_strength.groupby(
            level="symbol", sort=False
        ).transform(
            lambda values: values.rolling(20, min_periods=5).mean()
        )
        result = result.replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
