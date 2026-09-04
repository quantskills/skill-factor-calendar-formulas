"""Factor Calendar 股东盈余市值比率市场代理因子。"""

import numpy as np

from factor_calendar_runtime import Factor


class ShareholderEarningsToMarketCapFactor(Factor):
    """以成交额加权收益相对市值代理股东盈余收益率。"""

    def calculate(self, factors):
        close = factors["close"] + 0
        amount = factors["amount"] + 0
        market_cap = factors["market_cap"] + 0
        previous = close.groupby(level="symbol", sort=False).shift(1)
        previous = previous.fillna(close)
        returns = (close / previous - 1).where(
            (close > 0) & (previous > 0)
        )
        cash_generation = (returns * amount).groupby(
            level="symbol", sort=False
        ).transform(lambda item: item.rolling(20, min_periods=1).sum())
        result = (cash_generation / market_cap).where(market_cap > 0)
        result = result.replace([np.inf, -np.inf], np.nan).fillna(0.0)
        result.name = "value"
        return result
