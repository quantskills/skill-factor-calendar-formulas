"""Factor Calendar 综合公司治理质量市场代理因子。"""

import numpy as np
import pandas as pd

from factor_calendar_runtime import Factor


class CompanyGovernanceFactor(Factor):
    """合成低换手、低波动和高流动性代理治理质量。"""

    def calculate(self, factors):
        close = factors["close"] + 0
        amount = factors["amount"] + 0
        turnover = factors["turnover"] + 0
        market_cap = factors["market_cap"] + 0
        daily_return = close.groupby(level="symbol", sort=False).pct_change()
        volatility = daily_return.groupby(
            level="symbol", sort=False
        ).transform(lambda item: item.rolling(20, min_periods=2).std())
        average_turnover = turnover.groupby(
            level="symbol", sort=False
        ).transform(lambda item: item.rolling(20, min_periods=1).mean())
        liquidity = (amount / market_cap).where(market_cap > 0)
        components = pd.concat(
            [-average_turnover, -volatility, liquidity], axis=1
        )
        ranks = components.groupby(level="date", sort=False).rank(pct=True)
        result = ranks.mean(axis=1).fillna(0.0)
        result.name = "value"
        return result
