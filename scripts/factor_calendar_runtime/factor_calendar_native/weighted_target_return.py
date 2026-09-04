"""Factor Calendar 分析师预期收益率加权平均市场代理因子。"""

import numpy as np

from factor_calendar_runtime import Factor


class WeightedTargetReturnFactor(Factor):
    """以历史高点空间和趋势稳定性代理准确率加权目标收益率。"""

    def calculate(self, factors):
        close = factors["close"] + 0
        high = factors["high"] + 0
        previous_close = close.groupby(level="symbol", sort=False).shift(1)
        returns = (close / previous_close - 1).where(
            (close > 0) & (previous_close > 0)
        )
        target_price = high.groupby(level="symbol", sort=False).transform(
            lambda item: item.rolling(60, min_periods=20).max()
        )
        target_return = (target_price / close - 1).where(close > 0)
        mean_return = returns.groupby(level="symbol", sort=False).transform(
            lambda item: item.rolling(60, min_periods=20).mean()
        )
        volatility = returns.groupby(level="symbol", sort=False).transform(
            lambda item: item.rolling(60, min_periods=20).std()
        )
        accuracy_weight = (mean_return.abs() / volatility).where(
            volatility > 0
        )
        result = target_return * accuracy_weight
        result = result.replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
