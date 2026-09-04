"""Factor Calendar 最小收益率因子。"""

from factor_calendar_runtime import Factor


class MinimumReturnFactor(Factor):
    """过去三个月最小日收益率的相反数。"""

    def calculate(self, factors):
        close = factors["close"] + 0
        window = 63  # 约 3 个月

        previous_close = self.DELAY(close, 1)
        daily_return = (close / previous_close - 1).where(
            (close > 0) & (previous_close > 0)
        )
        result = -self.TS_MIN(daily_return, window)
        result.name = "value"
        return result
