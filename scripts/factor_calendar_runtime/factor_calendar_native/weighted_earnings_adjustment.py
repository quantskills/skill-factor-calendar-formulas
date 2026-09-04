"""Factor Calendar 分析师预测加权盈余修正幅度市场代理因子。"""

import numpy as np

from factor_calendar_runtime import Factor


class WeightedEarningsAdjustmentFactor(Factor):
    """以三个月价格修正和趋势置信度代理加权盈余修正。"""

    def calculate(self, factors):
        close = factors["close"] + 0
        previous_close = close.groupby(level="symbol", sort=False).shift(60)
        revision = ((close - previous_close) / previous_close.abs()).where(
            previous_close != 0
        )
        daily_previous = close.groupby(level="symbol", sort=False).shift(1)
        returns = (close / daily_previous - 1).where(
            (close > 0) & (daily_previous > 0)
        )
        positive_ratio = (returns > 0).astype(float).where(returns.notna())
        confidence = positive_ratio.groupby(
            level="symbol", sort=False
        ).transform(
            lambda item: item.rolling(60, min_periods=20).mean()
        )
        directional_confidence = (confidence - 0.5).abs() * 2
        result = revision * directional_confidence
        result = result.replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
