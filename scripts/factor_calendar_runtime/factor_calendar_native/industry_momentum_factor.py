"""Factor Calendar 行业领头羊动量溢价因子。"""

import numpy as np
import pandas as pd

from factor_calendar_runtime import Factor


class IndustryMomentumFactor(Factor):
    """计算行业内成交额领头羊与跟随者的二十日收益差。"""

    def calculate(self, factors):
        close = factors["close"] + 0
        amount = factors["amount"] + 0
        previous_close = close.groupby(level="symbol", sort=False).shift(20)
        momentum = (close / previous_close - 1).where(
            (close > 0) & (previous_close > 0)
        )
        average_amount = amount.groupby(level="symbol", sort=False).transform(
            lambda item: item.rolling(20, min_periods=5).mean()
        )
        liquidity_rank = average_amount.groupby(
            level="date", sort=False
        ).rank(pct=True)
        leader_return = momentum.where(liquidity_rank >= 0.7).groupby(
            level="date", sort=False
        ).transform("mean")
        follower_return = momentum.where(liquidity_rank <= 0.3).groupby(
            level="date", sort=False
        ).transform("mean")
        premium = leader_return - follower_return
        market_momentum = momentum.groupby(
            level="date", sort=False
        ).transform("mean")
        result = premium * (liquidity_rank - 0.5) + 0.05 * (
            momentum - market_momentum
        )
        result = result.replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
