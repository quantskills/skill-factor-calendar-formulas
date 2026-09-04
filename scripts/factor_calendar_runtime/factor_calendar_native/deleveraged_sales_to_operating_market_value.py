"""Factor Calendar 去杠杆化企业价值/销售收入比市场代理因子。"""

import numpy as np
from factor_calendar_runtime import Factor


class DeleveragedSalesToOperatingMarketValueFactor(Factor):
    """以年化成交额相对市值代理销售收入/经营性净资产市值。"""

    def calculate(self, factors):
        amount = factors["amount"] + 0
        turnover = factors["turnover"] + 0
        market_cap = factors["market_cap"] + 0
        annualized_amount = amount.groupby(level="symbol", sort=False).transform(lambda item: item.rolling(60, min_periods=20).mean()) * 252
        activity_value = (annualized_amount / market_cap).where(market_cap > 0)
        average_turnover = turnover.groupby(level="symbol", sort=False).transform(lambda item: item.rolling(20, min_periods=5).mean())
        result = activity_value * (1 + average_turnover.clip(lower=0))
        result = result.replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
