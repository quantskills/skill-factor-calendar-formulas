"""Factor Calendar 年度股票发行增长率市场代理因子。"""

import numpy as np
from factor_calendar_runtime import Factor


class AnnualShareIssuanceGrowthRateFactor(Factor):
    """以市值增长扣除价格收益代理净股权发行。"""

    def calculate(self, factors):
        market_cap = factors["market_cap"] + 0
        close = factors["close"] + 0
        annual_cap = market_cap.groupby(level="symbol", sort=False).shift(252)
        annual_close = close.groupby(level="symbol", sort=False).shift(252)
        annual = np.log((market_cap / annual_cap).where((market_cap > 0) & (annual_cap > 0))) - np.log((close / annual_close).where((close > 0) & (annual_close > 0)))
        short_cap = market_cap.groupby(level="symbol", sort=False).shift(20)
        short_close = close.groupby(level="symbol", sort=False).shift(20)
        short = 252 / 20 * (np.log((market_cap / short_cap).where((market_cap > 0) & (short_cap > 0))) - np.log((close / short_close).where((close > 0) & (short_close > 0))))
        result = annual.fillna(short) + np.log(market_cap.where(market_cap > 0)) * 1e-12
        result = result.replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
