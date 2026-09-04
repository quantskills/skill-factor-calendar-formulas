"""Factor Calendar 北向资金持股比例市场代理因子。"""

import numpy as np

from factor_calendar_runtime import Factor


class NorthboundHoldingsFactor(Factor):
    """使用成交额占流通市值比例的月均值代理北向持股比例。"""

    def calculate(self, factors):
        amount = factors["amount"] + 0
        market_cap = factors["market_cap"] + 0
        holding_ratio = (amount / market_cap).where(market_cap > 0)
        result = holding_ratio.groupby(
            level="symbol", sort=False
        ).transform(
            lambda item: item.rolling(20, min_periods=10).mean()
        )
        result = result.replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
