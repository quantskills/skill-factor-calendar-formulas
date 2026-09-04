"""Factor Calendar 相对新闻点击量市场代理因子。"""

import numpy as np

from factor_calendar_runtime import Factor


class ProportionOfNewsClicksFactor(Factor):
    """以异常成交额代理个股新闻点击量占比。"""

    def calculate(self, factors):
        amount = factors["amount"] + 0
        average_amount = amount.groupby(
            level="symbol", sort=False
        ).transform(lambda item: item.rolling(20, min_periods=5).mean())
        clicks = (amount / average_amount).where(average_amount > 0)
        total_clicks = clicks.groupby(level="date", sort=False).transform("sum")
        result = (clicks / total_clicks).where(total_clicks > 0)
        result = result.replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
