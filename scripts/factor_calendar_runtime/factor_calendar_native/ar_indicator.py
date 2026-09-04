"""Factor Calendar 相对强弱人气指标（AR）因子。"""

from factor_calendar_runtime import Factor


class ARIndicatorFactor(Factor):
    """20 日向上日内振幅与向下日内振幅之比。"""

    def calculate(self, factors):
        open_price = factors["open"] + 0
        high = factors["high"] + 0
        low = factors["low"] + 0
        window = 20

        valid = (
            (open_price > 0)
            & (high > 0)
            & (low > 0)
            & (high >= open_price)
            & (open_price >= low)
        )
        upward_range = (high - open_price).where(valid)
        downward_range = (open_price - low).where(valid)
        upward_sum = upward_range.groupby(level="symbol", sort=False).transform(
            lambda series: series.rolling(
                window=window, min_periods=window
            ).sum()
        )
        downward_sum = downward_range.groupby(
            level="symbol", sort=False
        ).transform(
            lambda series: series.rolling(
                window=window, min_periods=window
            ).sum()
        )
        result = (upward_sum / downward_sum * 100).where(downward_sum > 0)
        result.name = "value"
        return result
