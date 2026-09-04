"""Factor Calendar 企业自由现金流/经营性净资产市值市场代理因子。"""

import numpy as np
from factor_calendar_runtime import Factor


class DeleveragedFreeCashFlowToOperatingMarketValueFactor(Factor):
    """以成交额加权收益产生能力相对市值代理自由现金流收益率。"""

    def calculate(self, factors):
        close = factors["close"] + 0
        amount = factors["amount"] + 0
        market_cap = factors["market_cap"] + 0
        previous = close.groupby(level="symbol", sort=False).shift(1)
        returns = (close / previous - 1).where((close > 0) & (previous > 0))
        cash_generation = (returns * amount).groupby(level="symbol", sort=False).transform(lambda item: item.rolling(60, min_periods=20).sum())
        result = (cash_generation / market_cap).where(market_cap > 0)
        result = result.replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
