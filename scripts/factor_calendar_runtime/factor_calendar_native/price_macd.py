"""Factor Calendar 移动平均汇聚背离（MACD）因子。"""

from factor_calendar_runtime import Factor


class PriceMACDFactor(Factor):
    """收盘价快慢 EMA 差值与 9 日信号线之差。"""

    def calculate(self, factors):
        close = factors["close"] + 0
        short_window = 12
        long_window = 26
        signal_window = 9

        valid_close = close.where(close > 0)
        short_ema = valid_close.groupby(level="symbol", sort=False).transform(
            lambda series: series.ewm(
                span=short_window,
                adjust=False,
                min_periods=short_window,
            ).mean()
        )
        long_ema = valid_close.groupby(level="symbol", sort=False).transform(
            lambda series: series.ewm(
                span=long_window,
                adjust=False,
                min_periods=long_window,
            ).mean()
        )
        diff = short_ema - long_ema
        dea = diff.groupby(level="symbol", sort=False).transform(
            lambda series: series.ewm(
                span=signal_window,
                adjust=False,
                min_periods=signal_window,
            ).mean()
        )
        result = diff - dea
        result.name = "value"
        return result
