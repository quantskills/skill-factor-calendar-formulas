"""Factor Calendar 流动性经营资产变动率市场代理因子。"""

import numpy as np

from factor_calendar_runtime import Factor


class CurrentAssetTurnoverFactor(Factor):
    """使用成交额市值比的中期变化代理流动经营资产变化。"""

    def calculate(self, factors):
        amount = factors["amount"] + 0
        market_cap = factors["market_cap"] + 0
        liquidity = (amount / market_cap).where(market_cap > 0)
        current = liquidity.groupby(level="symbol", sort=False).transform(
            lambda item: item.rolling(10, min_periods=1).mean()
        )
        previous = current.groupby(level="symbol", sort=False).shift(10)
        previous = previous.fillna(current)
        result = current - previous
        result = result.replace([np.inf, -np.inf], np.nan).fillna(0.0)
        result.name = "value"
        return result
