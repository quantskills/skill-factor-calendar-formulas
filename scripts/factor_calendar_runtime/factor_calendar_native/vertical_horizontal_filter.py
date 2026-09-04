"""Factor Calendar 垂直水平滤波（VHF）因子。"""

from factor_calendar_runtime import Factor


class VerticalHorizontalFilterFactor(Factor):
    """20 日价格区间与收盘价逐日绝对变动总和之比。"""

    def calculate(self, factors):
        high = factors["high"] + 0
        low = factors["low"] + 0
        close = factors["close"] + 0
        window = 20

        valid = (high > 0) & (low > 0) & (close > 0) & (high >= low)
        valid_high = high.where(valid)
        valid_low = low.where(valid)
        valid_close = close.where(valid)
        highest_high = valid_high.groupby(
            level="symbol", sort=False
        ).transform(
            lambda series: series.rolling(
                window=window, min_periods=window
            ).max()
        )
        lowest_low = valid_low.groupby(level="symbol", sort=False).transform(
            lambda series: series.rolling(
                window=window, min_periods=window
            ).min()
        )
        absolute_change = (valid_close - self.DELAY(valid_close, 1)).abs()
        total_change = absolute_change.groupby(
            level="symbol", sort=False
        ).transform(
            lambda series: series.rolling(
                window=window, min_periods=window
            ).sum()
        )
        result = ((highest_high - lowest_low) / total_change).where(
            total_change > 0
        )
        result.name = "value"
        return result
