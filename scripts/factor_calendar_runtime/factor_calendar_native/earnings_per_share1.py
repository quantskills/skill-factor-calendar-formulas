"""Factor Calendar 每股营业收入市场代理因子。"""

import numpy as np

from factor_calendar_runtime import Factor


class EarningsPerShare1Factor(Factor):
    """使用二十日平均成交额除以估算总股本代理每股营业收入。"""

    def calculate(self, factors):
        close = factors["close"] + 0
        amount = factors["amount"] + 0
        market_cap = factors["market_cap"] + 0
        shares = (market_cap / close).where(close > 0)
        average_amount = amount.groupby(level="symbol", sort=False).transform(
            lambda item: item.rolling(20, min_periods=1).mean()
        )
        result = (average_amount / shares).where(shares > 0)
        result = result.replace([np.inf, -np.inf], np.nan).fillna(0.0)
        result.name = "value"
        return result
