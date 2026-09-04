"""Factor Calendar 成交量异同移动平均线（VMACD）因子。"""

from factor_calendar_runtime import Factor


class VolumeMACDFactor(Factor):
    """成交量快慢 EMA 差值与其信号线之差。"""

    def calculate(self, factors):
        volume = factors["volume"] + 0
        short_window = 12
        long_window = 26
        signal_window = 9

        valid_volume = volume.where(volume >= 0)
        short_ema = valid_volume.groupby(
            level="symbol", sort=False
        ).transform(
            lambda series: series.ewm(
                span=short_window, adjust=False, min_periods=short_window
            ).mean()
        )
        long_ema = valid_volume.groupby(
            level="symbol", sort=False
        ).transform(
            lambda series: series.ewm(
                span=long_window, adjust=False, min_periods=long_window
            ).mean()
        )
        diff = short_ema - long_ema
        dea = diff.groupby(level="symbol", sort=False).transform(
            lambda series: series.ewm(
                span=signal_window, adjust=False, min_periods=signal_window
            ).mean()
        )
        result = diff - dea
        result.name = "value"
        return result
