"""Factor Calendar 异同离差乖离率振荡器（DBCD）因子。"""

from factor_calendar_runtime import Factor


class DeviationRateOscillatorFactor(Factor):
    """5 日乖离率的 16 日差分经 17 日中国式 SMA 平滑。"""

    def calculate(self, factors):
        close = factors["close"] + 0
        bias_window = 5
        difference_lag = 16
        smoothing_window = 17

        valid_close = close.where(close > 0)
        moving_average = valid_close.groupby(
            level="symbol", sort=False
        ).transform(
            lambda series: series.rolling(
                window=bias_window, min_periods=bias_window
            ).mean()
        )
        bias = ((valid_close - moving_average) / moving_average).where(
            moving_average > 0
        )
        bias_difference = bias - self.DELAY(bias, difference_lag)
        result = bias_difference.groupby(
            level="symbol", sort=False
        ).transform(
            lambda series: series.ewm(
                alpha=1 / smoothing_window,
                adjust=False,
                min_periods=smoothing_window,
            ).mean()
        )
        result.name = "value"
        return result
