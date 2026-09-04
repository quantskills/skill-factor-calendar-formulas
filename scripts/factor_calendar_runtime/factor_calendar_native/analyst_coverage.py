"""Factor Calendar 分析师覆盖度市场代理因子。"""

import numpy as np

from factor_calendar_runtime import Factor


class AnalystCoverageFactor(Factor):
    """使用二十日平均成交额相对市场均值代理分析师覆盖度。"""

    def calculate(self, factors):
        amount = factors["amount"] + 0
        attention = amount.groupby(
            level="symbol", sort=False
        ).transform(
            lambda item: item.rolling(20, min_periods=10).mean()
        )
        market_attention = attention.groupby(
            level="date", sort=False
        ).transform("mean")
        result = (attention / market_attention).where(market_attention > 0)
        result = result.replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
