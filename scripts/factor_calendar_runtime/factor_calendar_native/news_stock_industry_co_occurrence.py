"""Factor Calendar 行业共现变动市场代理因子。"""

import numpy as np

from factor_calendar_runtime import Factor


class NewsStockIndustryCoOccurrenceFactor(Factor):
    """以个股与市场成交关注度共振代理行业新闻共现变化。"""

    def calculate(self, factors):
        amount = factors["amount"] + 0
        average_amount = amount.groupby(
            level="symbol", sort=False
        ).transform(lambda item: item.rolling(20, min_periods=5).mean())
        attention = (amount / average_amount).where(average_amount > 0)
        common_attention = attention.groupby(
            level="date", sort=False
        ).transform("mean")
        co_occurrence = attention * common_attention
        result = co_occurrence - co_occurrence.groupby(
            level="symbol", sort=False
        ).shift(1)
        result = result.replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
