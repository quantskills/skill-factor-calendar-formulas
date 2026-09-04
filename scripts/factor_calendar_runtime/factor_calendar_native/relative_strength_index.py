"""Factor Calendar 相对强弱指标（RSI）因子。"""

from factor_calendar_runtime import Factor


class RelativeStrengthIndexFactor(Factor):
    """基于 Wilder 平滑的 14 日相对强弱指标。"""

    def calculate(self, factors):
        close = factors["close"] + 0
        window = 14

        previous_close = self.DELAY(close, 1)
        change = (close - previous_close).where(
            (close > 0) & (previous_close > 0)
        )
        gain = change.clip(lower=0)
        loss = (-change).clip(lower=0)
        average_gain = gain.groupby(level="symbol", sort=False).transform(
            lambda series: series.ewm(
                alpha=1 / window,
                adjust=False,
                min_periods=window,
            ).mean()
        )
        average_loss = loss.groupby(level="symbol", sort=False).transform(
            lambda series: series.ewm(
                alpha=1 / window,
                adjust=False,
                min_periods=window,
            ).mean()
        )
        total_momentum = average_gain + average_loss
        result = (average_gain / total_momentum * 100).where(total_momentum > 0)
        result.name = "value"
        return result
