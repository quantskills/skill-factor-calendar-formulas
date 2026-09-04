"""Factor Calendar 综合质量市场代理因子。"""

import numpy as np
import pandas as pd

from factor_calendar_runtime import Factor


class QualityFactor(Factor):
    """从盈利趋势、成长动量和资本稳健性构建综合质量代理。"""

    def calculate(self, factors):
        close = factors["close"] + 0
        amount = factors["amount"] + 0
        turnover = factors["turnover"] + 0
        market_cap = factors["market_cap"] + 0
        previous = close.groupby(level="symbol", sort=False).shift(20)
        momentum = (close / previous - 1).replace(
            [np.inf, -np.inf], np.nan
        ).fillna(0.0)
        liquidity = (amount / market_cap).where(market_cap > 0)
        daily_return = close.groupby(level="symbol", sort=False).pct_change()
        volatility = daily_return.groupby(
            level="symbol", sort=False
        ).transform(lambda item: item.rolling(20, min_periods=2).std())
        turnover_stability = turnover.groupby(
            level="symbol", sort=False
        ).transform(lambda item: item.rolling(20, min_periods=2).std())
        components = pd.concat(
            [momentum, liquidity, -volatility, -turnover_stability], axis=1
        )
        ranks = components.groupby(level="date", sort=False).rank(pct=True)
        result = ranks.mean(axis=1).fillna(0.0)
        result.name = "value"
        return result
