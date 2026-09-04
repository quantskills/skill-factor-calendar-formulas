"""Factor Calendar 分析师共识覆盖加权动量市场代理因子。"""

import numpy as np

from factor_calendar_runtime import Factor


class AnalystCoverageMomentumFactor(Factor):
    """使用成交额关注度加权二十日动量代理共识覆盖动量。"""

    def calculate(self, factors):
        close = factors["close"] + 0
        amount = factors["amount"] + 0
        previous_close = close.groupby(level="symbol", sort=False).shift(20)
        momentum = (close / previous_close - 1).where(
            (close > 0) & (previous_close > 0)
        )
        attention = amount.groupby(
            level="symbol", sort=False
        ).transform(
            lambda item: item.rolling(20, min_periods=10).mean()
        )
        market_attention = attention.groupby(
            level="date", sort=False
        ).transform("sum")
        weight = (attention / market_attention).where(market_attention > 0)
        result = momentum * weight
        result = result.replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
