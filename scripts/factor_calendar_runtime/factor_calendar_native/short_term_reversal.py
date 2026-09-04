"""Factor Calendar 短期反转因子。"""

from factor_calendar_runtime import Factor


class ShortTermReversalFactor(Factor):
    """过去一个月收益率的相反数。"""

    def calculate(self, factors):
        close = factors["close"] + 0
        lookback = 21

        previous_close = self.DELAY(close, lookback)
        result = -(close / previous_close - 1).where(
            (close > 0) & (previous_close > 0)
        )
        result.name = "value"
        return result
