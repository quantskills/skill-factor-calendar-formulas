"""Factor Calendar 实体 K 线一致性买入强度因子。"""

import numpy as np
import pandas as pd

from factor_calendar_runtime import Factor


class ConsistentBuyTransactionFactor(Factor):
    """上涨实体 K 线出现频率的二十日均值。"""

    def calculate(self, factors):
        open_price = factors["open"] + 0
        high = factors["high"] + 0
        low = factors["low"] + 0
        close = factors["close"] + 0
        price_range = high - low
        body = (close - open_price).abs()
        consistent_buy = (
            (body <= 0.3 * price_range)
            & (close > open_price)
            & (price_range > 0)
        ).astype(float)
        result = consistent_buy.groupby(
            level="symbol", sort=False
        ).transform(
            lambda values: values.rolling(20, min_periods=5).mean()
        )
        result = result.replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
