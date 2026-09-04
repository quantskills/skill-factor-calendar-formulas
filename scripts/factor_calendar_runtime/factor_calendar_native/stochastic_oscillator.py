"""Factor Calendar 随机摆动指标（KDJ-J）因子。"""

from factor_calendar_runtime import Factor


class StochasticOscillatorFactor(Factor):
    """9 日 RSV 经 K、D 平滑后的 J 值。"""

    def calculate(self, factors):
        high = factors["high"] + 0
        low = factors["low"] + 0
        close = factors["close"] + 0
        window = 9
        smoothing = 3

        valid_high = high.where(high > 0)
        valid_low = low.where(low > 0)
        valid_close = close.where(close > 0)
        highest_high = valid_high.groupby(
            level="symbol", sort=False
        ).transform(
            lambda series: series.rolling(
                window=window, min_periods=window
            ).max()
        )
        lowest_low = valid_low.groupby(
            level="symbol", sort=False
        ).transform(
            lambda series: series.rolling(
                window=window, min_periods=window
            ).min()
        )
        price_range = highest_high - lowest_low
        rsv = ((valid_close - lowest_low) / price_range * 100).where(
            price_range > 0
        )
        k_value = rsv.groupby(level="symbol", sort=False).transform(
            lambda series: series.ewm(
                alpha=1 / smoothing,
                adjust=False,
                min_periods=smoothing,
            ).mean()
        )
        d_value = k_value.groupby(level="symbol", sort=False).transform(
            lambda series: series.ewm(
                alpha=1 / smoothing,
                adjust=False,
                min_periods=smoothing,
            ).mean()
        )
        result = 3 * k_value - 2 * d_value
        result.name = "value"
        return result
