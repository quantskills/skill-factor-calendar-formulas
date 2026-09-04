"""Factor Calendar 异常尾部不对称度市场代理因子。"""

import numpy as np

from factor_calendar_runtime import Factor


class AbnormalTailProbabilityFactor(Factor):
    """比较市场调整收益右尾与左尾的超额厚度。"""

    def calculate(self, factors):
        close = factors["close"] + 0
        previous_close = close.groupby(level="symbol", sort=False).shift(1)
        returns = (close / previous_close - 1).where(
            (close > 0) & (previous_close > 0)
        )
        market_return = returns.groupby(
            level="date", sort=False
        ).transform("mean")
        residual_return = returns - market_return
        rolling_mean = residual_return.groupby(
            level="symbol", sort=False
        ).transform(
            lambda item: item.rolling(120, min_periods=30).mean()
        )
        rolling_std = residual_return.groupby(
            level="symbol", sort=False
        ).transform(
            lambda item: item.rolling(120, min_periods=30).std(ddof=0)
        )
        standardized = (
            (residual_return - rolling_mean) / rolling_std
        ).where(rolling_std > 0)
        right_tail = np.maximum(standardized - 1.5, 0) ** 2
        left_tail = np.maximum(-standardized - 1.5, 0) ** 2
        daily_asymmetry = right_tail - left_tail
        result = daily_asymmetry.groupby(
            level="symbol", sort=False
        ).transform(
            lambda item: item.rolling(120, min_periods=30).mean()
        )
        result = result.replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
