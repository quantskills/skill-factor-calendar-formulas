"""Factor Calendar 关注度校正预期收益率市场代理因子。"""

import numpy as np

from factor_calendar_runtime import Factor


class FocusCorrectionExpectedYieldFactor(Factor):
    """二十日动量排名与成交额关注度排名的乘积。"""

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
        momentum_rank = momentum.groupby(
            level="date", sort=False
        ).transform(lambda item: item.rank(method="average", pct=True))
        attention_rank = attention.groupby(
            level="date", sort=False
        ).transform(lambda item: item.rank(method="average", pct=True))
        result = momentum_rank * attention_rank
        result = result.replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
