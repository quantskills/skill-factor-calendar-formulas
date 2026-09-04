"""Factor Calendar 三重指数移动平均（TEMA）因子。"""

from factor_calendar_runtime import Factor


class TripleExponentialMovingAverageFactor(Factor):
    """通过三层 EMA 降低移动平均滞后的 5 日价格趋势指标。"""

    def calculate(self, factors):
        close = factors["close"] + 0
        window = 5

        valid_close = close.where(close > 0)

        def exponential_average(series):
            return series.groupby(level="symbol", sort=False).transform(
                lambda values: values.ewm(
                    span=window,
                    adjust=False,
                    min_periods=window,
                ).mean()
            )

        ema1 = exponential_average(valid_close)
        ema2 = exponential_average(ema1)
        ema3 = exponential_average(ema2)
        result = 3 * ema1 - 3 * ema2 + ema3
        result.name = "value"
        return result
