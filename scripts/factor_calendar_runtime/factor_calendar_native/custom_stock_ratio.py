"""Factor Calendar 投资者关注度占比市场代理因子。"""

import numpy as np

from factor_calendar_runtime import Factor


class CustomStockRatioFactor(Factor):
    """使用个股成交额占全市场成交额的月度均值代理自选关注占比。"""

    def calculate(self, factors):
        amount = factors["amount"] + 0
        market_amount = amount.groupby(level="date", sort=False).transform(
            "sum"
        )
        daily_attention = (amount / market_amount).where(market_amount > 0)
        result = daily_attention.groupby(
            level="symbol", sort=False
        ).transform(
            lambda item: item.rolling(20, min_periods=5).mean()
        )
        result = result.replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
