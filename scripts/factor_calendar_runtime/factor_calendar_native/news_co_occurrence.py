"""Factor Calendar 新闻共现注意力溢出代理因子。"""

import numpy as np
import pandas as pd

from factor_calendar_runtime import Factor


class NewsCoOccurrenceFactor(Factor):
    """以成交额市场份额变化代理共现注意力的净溢出。"""

    def calculate(self, factors):
        amount = factors["amount"] + 0
        market_amount = amount.groupby(
            level="date", sort=False
        ).transform("sum")
        attention_share = (amount / market_amount).where(market_amount > 0)
        previous_share = attention_share.groupby(
            level="symbol", sort=False
        ).shift(1)
        attention_change = attention_share - previous_share
        result = attention_change.groupby(
            level="symbol", sort=False
        ).transform(
            lambda values: values.rolling(5, min_periods=2).mean()
        )
        result = result.replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
