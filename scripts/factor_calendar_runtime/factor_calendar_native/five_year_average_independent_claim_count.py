"""Factor Calendar 五年滚动平均独立权利要求项数市场代理因子。"""

import numpy as np
from factor_calendar_runtime import Factor


class FiveYearAverageIndependentClaimCountFactor(Factor):
    """以长期成长、成交活跃度改善和规模代理专利质量。"""

    def calculate(self, factors):
        close = factors["close"] + 0
        amount = factors["amount"] + 0
        market_cap = factors["market_cap"] + 0
        long_close = close.groupby(level="symbol", sort=False).shift(252)
        short_close = close.groupby(level="symbol", sort=False).shift(60)
        growth = (close / long_close - 1).where((close > 0) & (long_close > 0)).fillna((close / short_close - 1).where((close > 0) & (short_close > 0)))
        recent_amount = amount.groupby(level="symbol", sort=False).transform(lambda item: item.rolling(20, min_periods=5).mean())
        old_amount = recent_amount.groupby(level="symbol", sort=False).shift(60)
        activity_growth = np.log((recent_amount / old_amount).where((recent_amount > 0) & (old_amount > 0)))
        result = 0.5 * growth.groupby(level="date", sort=False).rank(pct=True) + 0.3 * activity_growth.groupby(level="date", sort=False).rank(pct=True) + 0.2 * market_cap.groupby(level="date", sort=False).rank(pct=True)
        result = result.replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
