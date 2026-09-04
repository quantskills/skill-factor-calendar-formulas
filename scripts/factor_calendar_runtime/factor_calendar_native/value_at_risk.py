"""Factor Calendar 历史模拟风险价值（VaR）因子。"""

from factor_calendar_runtime import Factor


class ValueAtRiskFactor(Factor):
    """最近一年的 95% 历史模拟损失分位数。"""

    def calculate(self, factors):
        close = factors["close"] + 0
        window = 252
        tail_probability = 0.05

        previous_close = self.DELAY(close, 1)
        daily_return = (close / previous_close - 1).where(
            (close > 0) & (previous_close > 0)
        )
        tail_return = daily_return.groupby(
            level="symbol", sort=False
        ).transform(
            lambda series: series.rolling(
                window=window, min_periods=window
            ).quantile(tail_probability)
        )
        result = -tail_return
        result.name = "value"
        return result
