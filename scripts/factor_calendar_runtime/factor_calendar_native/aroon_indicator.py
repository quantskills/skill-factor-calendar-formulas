"""Factor Calendar 阿隆指标因子。"""

from factor_calendar_runtime import Factor


class AroonIndicatorFactor(Factor):
    """最近高点与最近低点出现时点之差。"""

    def calculate(self, factors):
        high = factors["high"] + 0
        low = factors["low"] + 0
        window = 25

        valid_high = high.where(high > 0)
        valid_low = low.where(low > 0)
        days_since_high = valid_high.groupby(
            level="symbol", sort=False
        ).transform(
            lambda series: series.rolling(
                window=window, min_periods=window
            ).apply(lambda values: values[::-1].argmax(), raw=True)
        )
        days_since_low = valid_low.groupby(
            level="symbol", sort=False
        ).transform(
            lambda series: series.rolling(
                window=window, min_periods=window
            ).apply(lambda values: values[::-1].argmin(), raw=True)
        )

        aroon_up = (window - days_since_high) / window * 100
        aroon_down = (window - days_since_low) / window * 100
        result = aroon_up - aroon_down
        result.name = "value"
        return result
