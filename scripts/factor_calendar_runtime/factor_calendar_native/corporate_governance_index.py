"""Factor Calendar 股东权利指数市场代理因子。"""

import numpy as np
import pandas as pd

from factor_calendar_runtime import Factor


class CorporateGovernanceIndexFactor(Factor):
    """以高换手、高波动和低流动性代理较弱的股东权利。"""

    def calculate(self, factors):
        close = factors["close"] + 0
        amount = factors["amount"] + 0
        turnover = factors["turnover"] + 0
        market_cap = factors["market_cap"] + 0
        daily_return = close.groupby(
            level="symbol", sort=False
        ).pct_change()
        volatility = daily_return.groupby(
            level="symbol", sort=False
        ).transform(lambda item: item.rolling(20, min_periods=5).std())
        average_turnover = turnover.groupby(
            level="symbol", sort=False
        ).transform(lambda item: item.rolling(20, min_periods=5).mean())
        liquidity = (amount / market_cap).where(market_cap > 0)
        components = pd.concat(
            [average_turnover, volatility, -liquidity], axis=1
        )
        ranks = components.groupby(
            level="date", sort=False
        ).rank(pct=True)
        result = ranks.mean(axis=1)
        result = result.replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
