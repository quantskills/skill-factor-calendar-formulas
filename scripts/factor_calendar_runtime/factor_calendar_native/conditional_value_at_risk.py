"""Factor Calendar 条件风险价值（CVaR）因子。"""

from factor_calendar_runtime import Factor


class ConditionalValueAtRiskFactor(Factor):
    """最近一年最差 5% 日收益率对应的平均损失。"""

    def calculate(self, factors):
        close = factors["close"] + 0
        window = 252
        tail_probability = 0.05

        previous_close = self.DELAY(close, 1)
        daily_return = (close / previous_close - 1).where(
            (close > 0) & (previous_close > 0)
        )
        result = daily_return.groupby(
            level="symbol", sort=False
        ).transform(
            lambda series: series.rolling(
                window=window, min_periods=window
            ).apply(
                lambda values: -values[
                    values <= values.quantile(tail_probability)
                ].mean(),
                raw=False,
            )
        )
        result.name = "value"
        return result
