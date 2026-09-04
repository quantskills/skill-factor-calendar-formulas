"""Factor Calendar 过去 K 个月累计收益率动量因子。"""

from factor_calendar_runtime import Factor


class CumulativeReturnMomentumFactor(Factor):
    """过去六个月月度简单收益率之和。"""

    def calculate(self, factors):
        close = factors["close"] + 0
        month = 21
        months = 6

        result = close * 0
        for period in range(month, month * months + 1, month):
            current_month_end = self.DELAY(close, period - month)
            previous_month_end = self.DELAY(close, period)
            monthly_return = (
                current_month_end / previous_month_end - 1
            ).where(
                (current_month_end > 0) & (previous_month_end > 0)
            )
            result = result + monthly_return

        result.name = "value"
        return result
