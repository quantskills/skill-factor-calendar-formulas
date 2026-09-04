"""Factor Calendar 月度消费指数同比变动率市场代理因子。"""

import numpy as np

from factor_calendar_runtime import Factor


class ConsumerIndexChangeFactor(Factor):
    """使用近期成交额相对前期成交额的变化代理消费景气变化。"""

    def calculate(self, factors):
        amount = factors["amount"] + 0
        recent = amount.groupby(level="symbol", sort=False).transform(
            lambda item: item.rolling(10, min_periods=1).mean()
        )
        previous = recent.groupby(level="symbol", sort=False).shift(10)
        previous = previous.fillna(recent)
        result = ((recent - previous) / previous.abs()).where(previous != 0)
        result = result.replace([np.inf, -np.inf], np.nan).fillna(0.0)
        result.name = "value"
        return result
