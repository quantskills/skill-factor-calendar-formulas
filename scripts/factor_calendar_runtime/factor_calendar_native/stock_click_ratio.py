"""Factor Calendar 个股相对点击量市场代理因子。"""

import numpy as np

from factor_calendar_runtime import Factor


class StockClickRatioFactor(Factor):
    """使用个股成交额占市场成交额比例代理相对关注度。"""

    def calculate(self, factors):
        amount = factors["amount"] + 0
        total_amount = amount.groupby(level="date", sort=False).transform(
            "sum"
        )
        result = (amount / total_amount).where(total_amount > 0)
        result = result.replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
