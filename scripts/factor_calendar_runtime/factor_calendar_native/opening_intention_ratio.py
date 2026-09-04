"""Factor Calendar 开盘时段主动买入意愿强度市场代理因子。"""

import numpy as np

from factor_calendar_runtime import Factor


class OpeningIntentionRatioFactor(Factor):
    """综合开盘跳空和开收盘方向代理开盘买入意愿。"""

    def calculate(self, factors):
        open_price = factors["open"] + 0
        high = factors["high"] + 0
        low = factors["low"] + 0
        close = factors["close"] + 0
        previous_close = close.groupby(level="symbol", sort=False).shift(1)
        price_range = high - low
        executed_intention = ((close - open_price) / price_range).where(
            price_range > 0
        )
        order_intention = (
            (open_price - previous_close) / previous_close.abs()
        ).where(previous_close != 0)
        daily_intention = executed_intention + order_intention.clip(-1, 1)
        result = daily_intention.groupby(
            level="symbol", sort=False
        ).transform(
            lambda item: item.rolling(20, min_periods=5).mean()
        )
        result = result.replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
