"""Factor Calendar 钱德动量振荡器（CMO）因子。"""

from factor_calendar_runtime import Factor


class ChandeMomentumOscillatorFactor(Factor):
    """20 日价格上涨总幅度与下跌总幅度的标准化差。"""

    def calculate(self, factors):
        close = factors["close"] + 0
        window = 20

        previous_close = self.DELAY(close, 1)
        change = (close - previous_close).where(
            (close > 0) & (previous_close > 0)
        )
        upward_movement = change.clip(lower=0)
        downward_movement = (-change).clip(lower=0)
        upward_sum = upward_movement.groupby(
            level="symbol", sort=False
        ).transform(
            lambda series: series.rolling(
                window=window, min_periods=window
            ).sum()
        )
        downward_sum = downward_movement.groupby(
            level="symbol", sort=False
        ).transform(
            lambda series: series.rolling(
                window=window, min_periods=window
            ).sum()
        )
        total_movement = upward_sum + downward_sum
        result = ((upward_sum - downward_sum) / total_movement * 100).where(
            total_movement > 0
        )
        result.name = "value"
        return result
