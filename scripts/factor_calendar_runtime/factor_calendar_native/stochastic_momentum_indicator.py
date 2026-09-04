"""Factor Calendar 随机动量指标（SMI）因子。"""

from factor_calendar_runtime import Factor


class StochasticMomentumIndicatorFactor(Factor):
    """收盘价相对近期价格中轴的双重平滑动量。"""

    def calculate(self, factors):
        high = factors["high"] + 0
        low = factors["low"] + 0
        close = factors["close"] + 0
        lookback = 10
        first_smoothing = 3
        second_smoothing = 3

        valid_high = high.where(high > 0)
        valid_low = low.where(low > 0)
        valid_close = close.where(close > 0)
        highest_high = valid_high.groupby(
            level="symbol", sort=False
        ).transform(
            lambda series: series.rolling(
                window=lookback, min_periods=lookback
            ).max()
        )
        lowest_low = valid_low.groupby(
            level="symbol", sort=False
        ).transform(
            lambda series: series.rolling(
                window=lookback, min_periods=lookback
            ).min()
        )
        price_momentum = valid_close - (highest_high + lowest_low) / 2
        price_range = highest_high - lowest_low

        smooth_momentum = price_momentum.groupby(
            level="symbol", sort=False
        ).transform(
            lambda series: series.ewm(
                span=first_smoothing,
                adjust=False,
                min_periods=first_smoothing,
            ).mean()
        )
        double_smooth_momentum = smooth_momentum.groupby(
            level="symbol", sort=False
        ).transform(
            lambda series: series.ewm(
                span=second_smoothing,
                adjust=False,
                min_periods=second_smoothing,
            ).mean()
        )
        smooth_range = price_range.groupby(
            level="symbol", sort=False
        ).transform(
            lambda series: series.ewm(
                span=first_smoothing,
                adjust=False,
                min_periods=first_smoothing,
            ).mean()
        )
        double_smooth_range = smooth_range.groupby(
            level="symbol", sort=False
        ).transform(
            lambda series: series.ewm(
                span=second_smoothing,
                adjust=False,
                min_periods=second_smoothing,
            ).mean()
        )

        half_range = double_smooth_range / 2
        result = (double_smooth_momentum / half_range * 100).where(
            half_range > 0
        )
        result.name = "value"
        return result
