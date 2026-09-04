"""Factor Calendar 创新研发强度及产出综合市场代理因子。"""

import numpy as np

from factor_calendar_runtime import Factor


class InnovationCapacityFactor(Factor):
    """以交易投入、流动性增长、趋势和规模综合代理创新能力。"""

    def calculate(self, factors):
        close = factors["close"] + 0
        amount = factors["amount"] + 0
        turnover = factors["turnover"] + 0
        market_cap = factors["market_cap"] + 0
        previous_close = close.groupby(
            level="symbol", sort=False
        ).shift(60)
        amount_mean = amount.groupby(level="symbol", sort=False).transform(
            lambda item: item.rolling(20, min_periods=5).mean()
        )
        previous_amount = amount_mean.groupby(
            level="symbol", sort=False
        ).shift(60)
        momentum = (close / previous_close - 1).where(previous_close > 0)
        activity_growth = (amount_mean / previous_amount - 1).where(
            previous_amount > 0
        )
        turnover_rank = turnover.groupby(
            level="date", sort=False
        ).rank(pct=True)
        activity_rank = activity_growth.groupby(
            level="date", sort=False
        ).rank(pct=True)
        momentum_rank = momentum.groupby(
            level="date", sort=False
        ).rank(pct=True)
        size_rank = (-np.log(market_cap.where(market_cap > 0))).groupby(
            level="date", sort=False
        ).rank(pct=True)
        result = (
            turnover_rank + activity_rank + momentum_rank + size_rank
        ) / 4
        result = result.replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
