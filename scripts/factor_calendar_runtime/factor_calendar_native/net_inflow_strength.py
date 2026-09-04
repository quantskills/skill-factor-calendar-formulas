"""Factor Calendar 陆股通净流入强度比率市场代理因子。"""

import numpy as np

from factor_calendar_runtime import Factor


class NetInflowStrengthFactor(Factor):
    """以收盘位置估计净流入占当日成交额的强度。"""

    def calculate(self, factors):
        high = factors["high"] + 0
        low = factors["low"] + 0
        close = factors["close"] + 0
        amount = factors["amount"] + 0
        price_range = high - low
        direction = ((2 * close - high - low) / price_range).where(
            price_range > 0
        )
        signed_flow = direction * amount
        rolling_signed = signed_flow.groupby(
            level="symbol", sort=False
        ).transform(lambda item: item.rolling(5, min_periods=3).sum())
        rolling_amount = amount.groupby(
            level="symbol", sort=False
        ).transform(lambda item: item.rolling(5, min_periods=3).sum())
        result = (rolling_signed / rolling_amount).where(rolling_amount > 0)
        result = result.replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
