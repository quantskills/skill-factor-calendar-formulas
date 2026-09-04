"""Factor Calendar 相对波动性指标（RVI）因子。"""

from factor_calendar_runtime import Factor


class RelativeVolatilityIndexFactor(Factor):
    """高价、低价方向性波动强度的平均值。"""

    def calculate(self, factors):
        high = factors["high"] + 0
        low = factors["low"] + 0
        volatility_window = 10
        smoothing_window = 20

        valid_high = high.where(high > 0)
        valid_low = low.where(low > 0)

        def relative_strength(price):
            volatility = price.groupby(level="symbol", sort=False).transform(
                lambda series: series.rolling(
                    window=volatility_window,
                    min_periods=volatility_window,
                ).std(ddof=0)
            )
            previous_price = self.DELAY(price, 1)
            upward = volatility.where(price > previous_price, 0.0)
            downward = volatility.where(price < previous_price, 0.0)
            upward = upward.where(volatility.notna())
            downward = downward.where(volatility.notna())
            average_upward = upward.groupby(
                level="symbol", sort=False
            ).transform(
                lambda series: series.ewm(
                    span=smoothing_window,
                    adjust=False,
                    min_periods=smoothing_window,
                ).mean()
            )
            average_downward = downward.groupby(
                level="symbol", sort=False
            ).transform(
                lambda series: series.ewm(
                    span=smoothing_window,
                    adjust=False,
                    min_periods=smoothing_window,
                ).mean()
            )
            total = average_upward + average_downward
            return (average_upward / total * 100).where(total > 0)

        result = (relative_strength(valid_high) + relative_strength(valid_low)) / 2
        result = result.where(high >= low)
        result.name = "value"
        return result
