"""Factor Calendar 动量加速度因子。"""

from factor_calendar_runtime import Factor


class MomentumAccelerationFactor(Factor):
    """最近半年动量与此前半年动量之差，并跳过最近一个月。"""

    def calculate(self, factors):
        close = factors["close"] + 0
        month = 21
        half_year = 6 * month
        skip = month

        recent_end = self.DELAY(close, skip)
        recent_start = self.DELAY(close, skip + half_year)
        previous_start = self.DELAY(close, skip + 2 * half_year)
        recent_return = (recent_end / recent_start - 1).where(
            (recent_end > 0) & (recent_start > 0)
        )
        previous_return = (recent_start / previous_start - 1).where(
            (recent_start > 0) & (previous_start > 0)
        )
        result = recent_return - previous_return
        result.name = "value"
        return result
