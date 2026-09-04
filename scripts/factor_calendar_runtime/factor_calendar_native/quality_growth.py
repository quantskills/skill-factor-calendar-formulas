"""Factor Calendar 质量增长动量市场代理因子。"""

import numpy as np

from factor_calendar_runtime import Factor


class QualityGrowthFactor(Factor):
    """以风险调整收益作为质量指标计算季度增长动量。"""

    def calculate(self, factors):
        close = factors["close"] + 0
        previous_close = close.groupby(
            level="symbol", sort=False
        ).shift(20)
        return_20d = (close / previous_close - 1).where(previous_close > 0)
        daily_previous = close.groupby(
            level="symbol", sort=False
        ).shift(1)
        daily_return = (close / daily_previous - 1).where(daily_previous > 0)
        volatility = daily_return.groupby(
            level="symbol", sort=False
        ).transform(lambda item: item.rolling(20, min_periods=5).std(ddof=0))
        quality = (return_20d / volatility).where(volatility > 0)
        previous_quality = quality.groupby(
            level="symbol", sort=False
        ).shift(40)
        result = (
            (quality - previous_quality) / previous_quality.abs()
        ).where(previous_quality != 0)
        result = result.replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
