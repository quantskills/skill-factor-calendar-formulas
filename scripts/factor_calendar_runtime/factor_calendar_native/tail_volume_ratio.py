"""Factor Calendar 尾盘成交量比率市场代理因子。"""

import numpy as np

from factor_calendar_runtime import Factor


class TailVolumeRatioFactor(Factor):
    """使用收盘价在日内区间的位置代理尾盘成交量占比。"""

    def calculate(self, factors):
        high = factors["high"] + 0
        low = factors["low"] + 0
        close = factors["close"] + 0
        price_range = high - low
        daily_tail_ratio = ((close - low) / price_range).where(
            price_range > 0
        )
        result = daily_tail_ratio.groupby(
            level="symbol", sort=False
        ).transform(
            lambda item: item.rolling(20, min_periods=10).mean()
        )
        result = result.clip(lower=0, upper=1)
        result = result.replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
