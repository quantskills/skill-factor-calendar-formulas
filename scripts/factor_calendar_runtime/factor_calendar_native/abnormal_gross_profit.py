"""Factor Calendar 季度异常毛利润率市场代理因子。"""

import numpy as np

from factor_calendar_runtime import Factor


class AbnormalGrossProfitFactor(Factor):
    """以成交额增长超过价格增长的部分代理异常毛利润率。"""

    def calculate(self, factors):
        close = factors["close"] + 0
        amount = factors["amount"] + 0
        market_cap = factors["market_cap"] + 0
        amount_mean = amount.groupby(level="symbol", sort=False).transform(
            lambda item: item.rolling(20, min_periods=5).mean()
        )
        previous_amount = amount_mean.groupby(
            level="symbol", sort=False
        ).shift(60)
        previous_close = close.groupby(level="symbol", sort=False).shift(60)
        sales_growth = (amount_mean / previous_amount - 1).where(
            previous_amount > 0
        )
        price_growth = (close / previous_close - 1).where(previous_close > 0)
        result = ((sales_growth - price_growth) / np.log1p(market_cap)).where(
            market_cap > 0
        )
        result = result.replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
