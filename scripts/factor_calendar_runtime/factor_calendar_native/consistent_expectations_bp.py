"""Factor Calendar 一致预期账面市值比市场代理因子。"""

import numpy as np
from factor_calendar_runtime import Factor


class ConsistentExpectationsBPFactor(Factor):
    """以低估值、低波动和中期趋势代理一致预期账面市值比。"""

    def calculate(self, factors):
        close = factors["close"] + 0
        market_cap = factors["market_cap"] + 0
        previous = close.groupby(level="symbol", sort=False).shift(60)
        momentum = (close / previous - 1).where((close > 0) & (previous > 0))
        daily_return = close / close.groupby(level="symbol", sort=False).shift(1) - 1
        volatility = daily_return.groupby(level="symbol", sort=False).transform(lambda item: item.rolling(60, min_periods=20).std(ddof=0))
        value_rank = (-np.log(market_cap.where(market_cap > 0))).groupby(level="date", sort=False).rank(pct=True)
        trend_rank = momentum.groupby(level="date", sort=False).rank(pct=True)
        quality_rank = (-volatility).groupby(level="date", sort=False).rank(pct=True)
        result = 0.5 * value_rank + 0.3 * trend_rank + 0.2 * quality_rank
        result = result.replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
