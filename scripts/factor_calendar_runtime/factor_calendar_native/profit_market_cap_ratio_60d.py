"""Factor Calendar 60日盈利市值比率变动市场代理因子。"""

import numpy as np

from factor_calendar_runtime import Factor


class ProfitMarketCapRatio60DFactor(Factor):
    """使用价格强度除以市值代理盈利市值比率的60日变化。"""

    def calculate(self, factors):
        close = factors["close"] + 0
        market_cap = factors["market_cap"] + 0
        price_mean = close.groupby(level="symbol", sort=False).transform(
            lambda item: item.rolling(20, min_periods=5).mean()
        )
        price_strength = (close / price_mean).where(price_mean > 0)
        earning_yield_proxy = (price_strength / market_cap).where(
            market_cap > 0
        )
        previous = earning_yield_proxy.groupby(
            level="symbol", sort=False
        ).shift(60)
        result = earning_yield_proxy - previous
        result = result.replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
