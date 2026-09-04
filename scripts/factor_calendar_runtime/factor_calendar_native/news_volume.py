"""Factor Calendar 历史新闻提及量市场代理因子。"""

import numpy as np

from factor_calendar_runtime import Factor


class NewsVolumeFactor(Factor):
    """使用异常成交额事件的月度累计值代理历史新闻提及量。"""

    def calculate(self, factors):
        amount = factors["amount"] + 0
        market_average = amount.groupby(
            level="date", sort=False
        ).transform("mean")
        relative_attention = (amount / market_average).where(
            market_average > 0
        )
        result = relative_attention.groupby(
            level="symbol", sort=False
        ).transform(
            lambda item: item.rolling(20, min_periods=10).sum()
        )
        result = result.replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
