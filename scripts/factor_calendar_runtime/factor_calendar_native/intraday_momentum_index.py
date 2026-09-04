"""Factor Calendar 日内强度指标（IMI）因子。"""

from factor_calendar_runtime import Factor


class IntradayMomentumIndexFactor(Factor):
    """14 日上涨实体占全部日内实体幅度的比例。"""

    def calculate(self, factors):
        open_price = factors["open"] + 0
        close = factors["close"] + 0
        window = 14

        valid = (open_price > 0) & (close > 0)
        intraday_change = (close - open_price).where(valid)
        upward_movement = intraday_change.clip(lower=0)
        downward_movement = (-intraday_change).clip(lower=0)
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
        result = (upward_sum / total_movement * 100).where(total_movement > 0)
        result.name = "value"
        return result
