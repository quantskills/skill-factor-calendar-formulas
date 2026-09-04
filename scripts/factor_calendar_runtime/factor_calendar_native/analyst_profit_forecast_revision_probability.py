"""Factor Calendar 分析师盈利预测修订动量市场代理因子。"""

import numpy as np

from factor_calendar_runtime import Factor


class AnalystProfitForecastRevisionProbabilityFactor(Factor):
    """使用最近二十日动量相对前二十日动量的变化代理预测修订。"""

    def calculate(self, factors):
        close = factors["close"] + 0
        close_20 = close.groupby(level="symbol", sort=False).shift(20)
        close_40 = close.groupby(level="symbol", sort=False).shift(40)
        recent_momentum = (close / close_20 - 1).where(
            (close > 0) & (close_20 > 0)
        )
        previous_momentum = (close_20 / close_40 - 1).where(
            (close_20 > 0) & (close_40 > 0)
        )
        result = recent_momentum - previous_momentum
        result = result.replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
