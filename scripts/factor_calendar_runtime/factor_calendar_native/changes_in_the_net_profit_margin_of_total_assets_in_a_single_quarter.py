"""Factor Calendar 单季度总资产净利率同比变动市场代理因子。"""

import numpy as np

from factor_calendar_runtime import Factor


class ChangesInNetProfitMarginOfTotalAssetsSingleQuarterFactor(Factor):
    """以20日收益市值比相对前一季度的变化代理单季度 ROA 变动。"""

    def calculate(self, factors):
        close = factors["close"] + 0
        market_cap = factors["market_cap"] + 0
        previous_close = close.groupby(
            level="symbol", sort=False
        ).shift(20)
        return_20d = (close / previous_close - 1).where(previous_close > 0)
        roa_proxy = (return_20d / np.log(1 + market_cap)).where(
            market_cap > 0
        )
        result = roa_proxy - roa_proxy.groupby(
            level="symbol", sort=False
        ).shift(40)
        result = result.replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
