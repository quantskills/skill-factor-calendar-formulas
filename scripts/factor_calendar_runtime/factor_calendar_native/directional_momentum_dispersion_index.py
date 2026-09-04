"""Factor Calendar 方向性动量离散指标（DDI）因子。"""

from factor_calendar_runtime import Factor


class DirectionalMomentumDispersionIndexFactor(Factor):
    """20 日向上与向下价格动量之差占总动量的百分比。"""

    def calculate(self, factors):
        high = factors["high"] + 0
        low = factors["low"] + 0
        window = 20

        valid = (high > 0) & (low > 0) & (high >= low)
        valid_high = high.where(valid)
        valid_low = low.where(valid)
        previous_high = self.DELAY(valid_high, 1)
        previous_low = self.DELAY(valid_low, 1)

        high_change = (valid_high - previous_high).abs()
        low_change = (valid_low - previous_low).abs()
        movement = high_change.where(high_change >= low_change, low_change)
        direction_up = (valid_high + valid_low) > (
            previous_high + previous_low
        )
        upward_momentum = movement.where(direction_up, 0.0).where(
            previous_high.notna() & previous_low.notna()
        )
        downward_momentum = movement.where(~direction_up, 0.0).where(
            previous_high.notna() & previous_low.notna()
        )

        upward_sum = upward_momentum.groupby(
            level="symbol", sort=False
        ).transform(
            lambda series: series.rolling(
                window=window, min_periods=window
            ).sum()
        )
        downward_sum = downward_momentum.groupby(
            level="symbol", sort=False
        ).transform(
            lambda series: series.rolling(
                window=window, min_periods=window
            ).sum()
        )
        total_momentum = upward_sum + downward_sum
        result = ((upward_sum - downward_sum) / total_momentum * 100).where(
            total_momentum > 0, 0.0
        )
        result = result.where(total_momentum.notna())
        result.name = "value"
        return result
