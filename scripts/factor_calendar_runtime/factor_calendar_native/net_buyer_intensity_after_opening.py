"""Factor Calendar 开盘后主动买入强度标准化均值因子。"""

import numpy as np
import pandas as pd

from factor_calendar_runtime import Factor


class NetBuyerIntensityAfterOpeningFactor(Factor):
    """以日 K 线位置代理开盘后净主动买入强度并进行标准化。"""

    def calculate(self, factors):
        open_price = factors["open"] + 0
        high = factors["high"] + 0
        low = factors["low"] + 0
        close = factors["close"] + 0
        price_range = high - low
        daily_strength = ((close - open_price) / price_range).where(
            price_range > 0
        )
        rolling_mean = daily_strength.groupby(
            level="symbol", sort=False
        ).transform(
            lambda values: values.rolling(20, min_periods=5).mean()
        )
        rolling_std = daily_strength.groupby(
            level="symbol", sort=False
        ).transform(
            lambda values: values.rolling(20, min_periods=5).std(ddof=0)
        )
        result = (rolling_mean / rolling_std).where(rolling_std > 0)
        result = result.fillna(daily_strength)
        result = result.replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
