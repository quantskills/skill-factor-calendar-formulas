"""Factor Calendar 梅斯指数（Mass Index）因子。"""

from factor_calendar_runtime import Factor


class MassIndexFactor(Factor):
    """双重平滑日内振幅之比的 25 日滚动和。"""

    def calculate(self, factors):
        high = factors["high"] + 0
        low = factors["low"] + 0
        ema_window = 9
        sum_window = 25

        price_range = (high - low).where(
            (high > 0) & (low > 0) & (high >= low)
        )
        first_ema = price_range.groupby(level="symbol", sort=False).transform(
            lambda series: series.ewm(
                span=ema_window,
                adjust=False,
                min_periods=ema_window,
            ).mean()
        )
        second_ema = first_ema.groupby(level="symbol", sort=False).transform(
            lambda series: series.ewm(
                span=ema_window,
                adjust=False,
                min_periods=ema_window,
            ).mean()
        )
        ema_ratio = (first_ema / second_ema).where(second_ema > 0)
        result = ema_ratio.groupby(level="symbol", sort=False).transform(
            lambda series: series.rolling(
                window=sum_window, min_periods=sum_window
            ).sum()
        )
        result.name = "value"
        return result
