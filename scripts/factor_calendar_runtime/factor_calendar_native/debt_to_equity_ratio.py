"""Factor Calendar 债务权益比率市场代理因子。"""

import numpy as np
from factor_calendar_runtime import Factor


class DebtToEquityRatioFactor(Factor):
    """以权益波动和小市值特征代理财务杠杆。"""

    def calculate(self, factors):
        close = factors["close"] + 0
        market_cap = factors["market_cap"] + 0
        previous = close.groupby(level="symbol", sort=False).shift(1)
        returns = close / previous - 1
        volatility = returns.groupby(level="symbol", sort=False).transform(lambda item: item.rolling(60, min_periods=20).std(ddof=0))
        volatility_rank = volatility.groupby(level="date", sort=False).rank(pct=True)
        small_size_rank = (-np.log(market_cap.where(market_cap > 0))).groupby(level="date", sort=False).rank(pct=True)
        result = 0.7 * volatility_rank + 0.3 * small_size_rank
        result = result.replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
