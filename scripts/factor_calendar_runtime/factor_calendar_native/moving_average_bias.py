"""Factor Calendar 价格偏离移动均线百分比（BIAS）因子。"""

from factor_calendar_runtime import Factor


class MovingAverageBiasFactor(Factor):
    """收盘价相对 20 日简单移动平均线的偏离百分比。"""

    def calculate(self, factors):
        close = factors["close"] + 0
        window = 20

        valid_close = close.where(close > 0)
        moving_average = valid_close.groupby(
            level="symbol", sort=False
        ).transform(
            lambda series: series.rolling(
                window=window, min_periods=window
            ).mean()
        )
        result = ((valid_close - moving_average) / moving_average * 100).where(
            moving_average > 0
        )
        result.name = "value"
        return result
