"""Factor Calendar 月度收益季节性反转因子。"""

from factor_calendar_runtime import Factor


class SeasonalReturnReversalFactor(Factor):
    """过去约 1 至 11 个月、排除最近一个月的平均超额收益。"""

    def calculate(self, factors):
        close = factors["close"] + 0
        previous_close = self.DELAY(close, 1)
        daily_return = (close / previous_close - 1).where(
            (close > 0) & (previous_close > 0)
        )
        market_return = daily_return.groupby(
            level="date", sort=False
        ).transform("mean")
        excess_return = daily_return - market_return
        recent_month = excess_return.groupby(
            level="symbol", sort=False
        ).transform(
            lambda series: series.rolling(21, min_periods=21).mean()
        )
        eleven_months = excess_return.groupby(
            level="symbol", sort=False
        ).transform(
            lambda series: series.rolling(231, min_periods=231).mean()
        )

        result = (eleven_months * 231 - recent_month * 21) / 210
        result.name = "value"
        return result
