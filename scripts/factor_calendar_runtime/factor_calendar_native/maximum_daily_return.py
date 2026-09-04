"""Factor Calendar 最大日收益率因子。"""

from factor_calendar_runtime import Factor


class MaximumDailyReturnFactor(Factor):
    """过去一个月日收益率序列中的最大值。"""

    def calculate(self, factors):
        close = factors["close"] + 0
        window = 21  # 约 1 个月

        previous_close = self.DELAY(close, 1)
        daily_return = (close / previous_close - 1).where(
            (close > 0) & (previous_close > 0)
        )
        result = self.TS_MAX(daily_return, window)
        result.name = "value"
        return result
