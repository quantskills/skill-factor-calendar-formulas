"""Factor Calendar 应计盈余比率（总额）市场代理因子。"""

import numpy as np

from factor_calendar_runtime import Factor


class QualityTotalAccruedSurplusFactor(Factor):
    """以价格收益减去成交现金流强度代理总应计盈余。"""

    def calculate(self, factors):
        close = factors["close"] + 0
        amount = factors["amount"] + 0
        market_cap = factors["market_cap"] + 0
        previous = close.groupby(level="symbol", sort=False).shift(20)
        previous = previous.fillna(close)
        earnings_proxy = (close / previous - 1).where(
            (close > 0) & (previous > 0)
        )
        cash_flow_proxy = (amount / market_cap).where(market_cap > 0)
        cash_flow_proxy = cash_flow_proxy.groupby(
            level="symbol", sort=False
        ).transform(lambda item: item.rolling(20, min_periods=1).mean())
        result = earnings_proxy - cash_flow_proxy
        result = result.replace([np.inf, -np.inf], np.nan).fillna(0.0)
        result.name = "value"
        return result
