"""Factor Calendar 供应链议价能力及资金占用市场代理因子。"""

import numpy as np
from factor_calendar_runtime import Factor


class SupplyChainPositionFactor(Factor):
    """以规模、流动性、低换手和价格稳定性代理供应链地位。"""

    def calculate(self, factors):
        close = factors["close"] + 0
        amount = factors["amount"] + 0
        turnover = factors["turnover"] + 0
        market_cap = factors["market_cap"] + 0
        previous = close.groupby(level="symbol", sort=False).shift(1)
        returns = close / previous - 1
        volatility = returns.groupby(level="symbol", sort=False).transform(lambda item: item.rolling(60, min_periods=20).std(ddof=0))
        average_amount = amount.groupby(level="symbol", sort=False).transform(lambda item: item.rolling(20, min_periods=5).mean())
        average_turnover = turnover.groupby(level="symbol", sort=False).transform(lambda item: item.rolling(20, min_periods=5).mean())
        result = (market_cap.groupby(level="date", sort=False).rank(pct=True) + average_amount.groupby(level="date", sort=False).rank(pct=True) + (-average_turnover).groupby(level="date", sort=False).rank(pct=True) + (-volatility).groupby(level="date", sort=False).rank(pct=True)) / 4
        result = result + np.log(market_cap.where(market_cap > 0)) * 1e-12
        result = result.replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
