"""Factor Calendar TTM 有形资本回报率环比增长率市场代理因子。"""

import numpy as np

from factor_calendar_runtime import Factor


class ReturnOnTangibleCapitalROTCMoMGrowthRateFactor(Factor):
    """以成交额相对市值的资本效率代理 ROTC 环比增长。"""

    def calculate(self, factors):
        amount = factors["amount"] + 0
        market_cap = factors["market_cap"] + 0
        capital_efficiency = (amount / market_cap).where(market_cap > 0)
        rotc = capital_efficiency.groupby(
            level="symbol", sort=False
        ).transform(lambda item: item.rolling(20, min_periods=5).mean())
        previous = rotc.groupby(level="symbol", sort=False).shift(60)
        result = ((rotc - previous) / previous.abs()).where(previous != 0)
        result = result.replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
