"""Factor Calendar 隔夜新闻情感偏向市场代理因子。"""

import numpy as np

from factor_calendar_runtime import Factor


class OvernightNewsSentimentFactor(Factor):
    """以隔夜跳空相对市场偏离代理隔夜新闻情绪。"""

    def calculate(self, factors):
        open_price = factors["open"] + 0
        close = factors["close"] + 0
        previous_close = close.groupby(level="symbol", sort=False).shift(1)
        overnight_return = (open_price / previous_close - 1).where(
            (open_price > 0) & (previous_close > 0)
        )
        market_overnight = overnight_return.groupby(
            level="date", sort=False
        ).transform("mean")
        result = overnight_return - market_overnight
        result = result.replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
