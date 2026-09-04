"""Factor Calendar 内生无形资产累积市场代理因子。"""

import numpy as np
from factor_calendar_runtime import Factor


class EndogenousIntangibleAssetsFactor(Factor):
    """以持续成交投入和长期成长代理知识资本与组织资本。"""

    def calculate(self, factors):
        close = factors["close"] + 0
        amount = factors["amount"] + 0
        market_cap = factors["market_cap"] + 0
        investment_intensity = (amount / market_cap).where(market_cap > 0)
        accumulated_investment = investment_intensity.groupby(level="symbol", sort=False).transform(lambda item: item.ewm(span=252, min_periods=20, adjust=False).mean())
        long_close = close.groupby(level="symbol", sort=False).shift(252)
        short_close = close.groupby(level="symbol", sort=False).shift(60)
        growth = (close / long_close - 1).where((close > 0) & (long_close > 0)).fillna((close / short_close - 1).where((close > 0) & (short_close > 0)))
        result = 0.6 * accumulated_investment.groupby(level="date", sort=False).rank(pct=True) + 0.4 * growth.groupby(level="date", sort=False).rank(pct=True)
        result = result.replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
