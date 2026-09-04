"""Factor Calendar 动态趋向指标（DTMI）因子。"""

from factor_calendar_runtime import Factor


class DynamicTrendMomentumIndicatorFactor(Factor):
    """基于开盘跳变构造的 23 日多空动能相对强度。"""

    def calculate(self, factors):
        open_price = factors["open"] + 0
        high = factors["high"] + 0
        low = factors["low"] + 0
        window = 23

        valid = (
            (open_price > 0)
            & (high > 0)
            & (low > 0)
            & (high >= open_price)
            & (open_price >= low)
        )
        valid_open = open_price.where(valid)
        valid_high = high.where(valid)
        valid_low = low.where(valid)
        previous_open = self.DELAY(valid_open, 1)

        upward_range = valid_high - valid_open
        upward_gap = valid_open - previous_open
        upward_momentum = upward_range.where(
            upward_range >= upward_gap, upward_gap
        ).where(valid_open >= previous_open, 0.0).where(previous_open.notna())

        downward_range = valid_open - valid_low
        downward_gap = previous_open - valid_open
        downward_momentum = downward_range.where(
            downward_range >= downward_gap, downward_gap
        ).where(valid_open < previous_open, 0.0).where(previous_open.notna())

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
        difference = upward_sum - downward_sum
        denominator = upward_sum.where(
            upward_sum > downward_sum, downward_sum
        )
        result = (difference / denominator).where(denominator > 0, 0.0)
        result = result.where(upward_sum.notna() & downward_sum.notna())
        result.name = "value"
        return result
