"""Factor Calendar 分析师一致预期净资产收益率市场代理因子。"""

import numpy as np
from factor_calendar_runtime import Factor


class ConsensusROEFactor(Factor):
    """以中期趋势、低波动和低换手代理市场一致预期盈利能力。"""

    def calculate(self, factors):
        close = factors["close"] + 0
        turnover = factors["turnover"] + 0
        previous = close.groupby(level="symbol", sort=False).shift(60)
        momentum = (close / previous - 1).where((close > 0) & (previous > 0))
        daily_return = close / close.groupby(level="symbol", sort=False).shift(1) - 1
        volatility = daily_return.groupby(level="symbol", sort=False).transform(lambda item: item.rolling(60, min_periods=20).std(ddof=0))
        average_turnover = turnover.groupby(level="symbol", sort=False).transform(lambda item: item.rolling(20, min_periods=5).mean())
        result = 0.5 * momentum.groupby(level="date", sort=False).rank(pct=True) + 0.3 * (-volatility).groupby(level="date", sort=False).rank(pct=True) + 0.2 * (-average_turnover).groupby(level="date", sort=False).rank(pct=True)
        result = result.replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
