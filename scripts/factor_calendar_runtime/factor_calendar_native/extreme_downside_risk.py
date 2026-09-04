"""Factor Calendar 尾部风险厚度市场代理因子。"""

import numpy as np

from factor_calendar_runtime import Factor


class ExtremeDownsideRiskFactor(Factor):
    """使用 L 矩快速估计市场调整负收益的 GEV 尾部形状。"""

    def calculate(self, factors):
        close = factors["close"] + 0
        previous_close = close.groupby(level="symbol", sort=False).shift(1)
        returns = (close / previous_close - 1).where(
            (close > 0) & (previous_close > 0)
        )
        market_return = returns.groupby(
            level="date", sort=False
        ).transform("mean")
        downside = -(returns - market_return)

        def gev_shape(window):
            values = np.asarray(window, dtype=float)
            values = values[np.isfinite(values)]
            count = len(values)
            if count < 30:
                return np.nan
            values.sort()
            positions = np.arange(count, dtype=float)
            probability_weighted_moment_0 = values.mean()
            probability_weighted_moment_1 = np.dot(
                positions / (count - 1), values
            ) / count
            probability_weighted_moment_2 = np.dot(
                positions
                * (positions - 1)
                / ((count - 1) * (count - 2)),
                values,
            ) / count
            second_l_moment = (
                2 * probability_weighted_moment_1
                - probability_weighted_moment_0
            )
            if not np.isfinite(second_l_moment) or second_l_moment <= 0:
                return np.nan
            third_l_moment = (
                6 * probability_weighted_moment_2
                - 6 * probability_weighted_moment_1
                + probability_weighted_moment_0
            )
            l_skewness = third_l_moment / second_l_moment
            denominator = 3 + l_skewness
            if not np.isfinite(l_skewness) or denominator <= 0:
                return np.nan
            approximation = (
                2 / denominator - np.log(2) / np.log(3)
            )
            scipy_shape = (
                7.8590 * approximation
                + 2.9554 * approximation * approximation
            )
            return -scipy_shape

        result = downside.groupby(level="symbol", sort=False).transform(
            lambda item: item.rolling(60, min_periods=30).apply(
                gev_shape, raw=True
            )
        )
        result = result.replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
