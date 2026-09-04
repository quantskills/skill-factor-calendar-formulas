"""Factor Calendar 非流动性变异系数因子。"""

from factor_calendar_runtime import Factor


class IlliquidityCoefficientOfVariationFactor(Factor):
    """20 日 Amihud 非流动性序列的标准差与均值之比。"""

    def calculate(self, factors):
        close = factors["close"] + 0
        amount = factors["amount"] + 0
        window = 20

        previous_close = self.DELAY(close, 1)
        daily_return = (close / previous_close - 1).where(
            (close > 0) & (previous_close > 0)
        )
        daily_illiquidity = (daily_return.abs() / amount).where(amount > 0)
        rolling_mean = daily_illiquidity.groupby(
            level="symbol", sort=False
        ).transform(
            lambda series: series.rolling(
                window=window, min_periods=window
            ).mean()
        )
        rolling_std = daily_illiquidity.groupby(
            level="symbol", sort=False
        ).transform(
            lambda series: series.rolling(
                window=window, min_periods=window
            ).std(ddof=1)
        )
        result = (rolling_std / rolling_mean).where(rolling_mean > 0)
        result.name = "value"
        return result
