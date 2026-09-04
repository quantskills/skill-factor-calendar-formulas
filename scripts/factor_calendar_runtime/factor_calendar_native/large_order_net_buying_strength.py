"""Factor Calendar 开盘时段大单净买入强度标准化均值因子。"""

import numpy as np
import pandas as pd

from factor_calendar_runtime import Factor


class LargeOrderNetBuyingStrengthFactor(Factor):
    """以成交额加权开收盘方向代理大单净买入强度。"""

    def calculate(self, factors):
        open_price = factors["open"] + 0
        high = factors["high"] + 0
        low = factors["low"] + 0
        close = factors["close"] + 0
        amount = factors["amount"] + 0
        price_range = high - low
        net_buy_amount = (
            amount * (close - open_price) / price_range
        ).where((price_range > 0) & (amount > 0))
        average_amount = amount.groupby(
            level="symbol", sort=False
        ).transform(
            lambda values: values.rolling(20, min_periods=5).mean()
        )
        normalized = (net_buy_amount / average_amount).where(
            average_amount > 0
        )
        result = normalized.groupby(
            level="symbol", sort=False
        ).transform(
            lambda values: values.rolling(20, min_periods=5).mean()
        )
        result = result.replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
