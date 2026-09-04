"""Factor Calendar 分析师一致预期市盈率倒数市场代理因子。"""

import numpy as np
from factor_calendar_runtime import Factor


class ConsistentEPSFactor(Factor):
    """以趋势质量和相对低估值代理一致预期盈利收益率。"""

    def calculate(self, factors):
        close = factors["close"] + 0
        market_cap = factors["market_cap"] + 0
        previous = close.groupby(level="symbol", sort=False).shift(60)
        momentum = (close / previous - 1).where((close > 0) & (previous > 0))
        daily_return = close / close.groupby(level="symbol", sort=False).shift(1) - 1
        volatility = daily_return.groupby(level="symbol", sort=False).transform(lambda item: item.rolling(60, min_periods=20).std(ddof=0))
        quality = (momentum / volatility).where(volatility > 0)
        value_rank = (-np.log(market_cap.where(market_cap > 0))).groupby(level="date", sort=False).rank(pct=True)
        result = 0.65 * quality.groupby(level="date", sort=False).rank(pct=True) + 0.35 * value_rank
        result = result.replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
