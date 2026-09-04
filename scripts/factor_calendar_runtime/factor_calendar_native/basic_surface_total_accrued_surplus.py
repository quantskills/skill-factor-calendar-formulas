"""Factor Calendar 应计盈余资产比率市场代理因子。"""

import numpy as np

from factor_calendar_runtime import Factor


class BasicSurfaceTotalAccruedSurplusFactor(Factor):
    """使用价格收益与成交额变化背离代理应计盈余风险。"""

    def calculate(self, factors):
        close = factors["close"] + 0
        amount = factors["amount"] + 0
        price_return = close.groupby(level="symbol", sort=False).pct_change()
        amount_change = amount.groupby(level="symbol", sort=False).pct_change()
        divergence = price_return - amount_change
        result = divergence.groupby(level="symbol", sort=False).transform(
            lambda item: item.rolling(20, min_periods=2).mean()
        )
        result = result.replace([np.inf, -np.inf], np.nan).fillna(0.0)
        result.name = "value"
        return result
