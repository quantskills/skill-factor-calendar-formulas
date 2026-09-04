"""Factor Calendar 布林买卖意愿比率（BR）因子。"""

from factor_calendar_runtime import Factor


class BRIndicatorFactor(Factor):
    """20 日多头力量与空头力量滚动和之比。"""

    def calculate(self, factors):
        high = factors["high"] + 0
        low = factors["low"] + 0
        close = factors["close"] + 0
        window = 20

        valid = (high > 0) & (low > 0) & (close > 0) & (high >= low)
        previous_close = self.DELAY(close.where(close > 0), 1)
        bullish_power = (high - previous_close).clip(lower=0).where(valid)
        bearish_power = (previous_close - low).clip(lower=0).where(valid)
        bullish_sum = bullish_power.groupby(
            level="symbol", sort=False
        ).transform(
            lambda series: series.rolling(
                window=window, min_periods=window
            ).sum()
        )
        bearish_sum = bearish_power.groupby(
            level="symbol", sort=False
        ).transform(
            lambda series: series.rolling(
                window=window, min_periods=window
            ).sum()
        )
        result = (bullish_sum / bearish_sum).where(bearish_sum > 0)
        result.name = "value"
        return result
