"""Factor Calendar Amihud 非流动性因子。"""

from factor_calendar_runtime import Factor


class AmihudIlliquidityFactor(Factor):
    """最近一个月单位成交额对应的绝对日收益率均值。"""

    def calculate(self, factors):
        close = factors["close"] + 0
        amount = factors["amount"] + 0
        window = 21
        minimum_observations = 15

        previous_close = self.DELAY(close, 1)
        daily_return = (close / previous_close - 1).where(
            (close > 0) & (previous_close > 0)
        )
        daily_illiquidity = (daily_return.abs() / amount).where(amount > 0)
        result = daily_illiquidity.groupby(
            level="symbol", sort=False
        ).transform(
            lambda series: series.rolling(
                window=window,
                min_periods=minimum_observations,
            ).mean()
        )
        result.name = "value"
        return result
