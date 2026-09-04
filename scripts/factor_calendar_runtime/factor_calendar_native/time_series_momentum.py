"""Factor Calendar 时间序列动量（TSMOM）因子。"""

from factor_calendar_runtime import Factor


class TimeSeriesMomentumFactor(Factor):
    """过去十二个月动量方向乘以当月风险调整后超额收益。"""

    def calculate(self, factors):
        close = factors["close"] + 0
        month = 21
        months = 12

        previous_month_close = self.DELAY(close, month)
        monthly_return = (close / previous_month_close - 1).where(
            (close > 0) & (previous_month_close > 0)
        )
        historical_mean = self.DELAY(
            self.MA(monthly_return, month * months), month
        )
        excess_return = monthly_return - historical_mean
        historical_excess_mean = self.DELAY(
            self.MA(excess_return, month * months), month
        )
        direction = historical_excess_mean.where(
            historical_excess_mean == 0,
            historical_excess_mean / historical_excess_mean.abs(),
        )
        volatility = self.STDDEV(excess_return, month * months)
        result = (direction * excess_return / volatility).where(volatility > 0)
        result.name = "value"
        return result
