"""Factor Calendar 平均真实波幅（ATR）因子。"""

from factor_calendar_runtime import Factor


class AverageTrueRangeFactor(Factor):
    """真实波幅的 20 日指数移动平均。"""

    def calculate(self, factors):
        high = factors["high"] + 0
        low = factors["low"] + 0
        close = factors["close"] + 0
        window = 20

        valid_price = (high > 0) & (low > 0) & (close > 0) & (high >= low)
        valid_high = high.where(valid_price)
        valid_low = low.where(valid_price)
        previous_close = self.DELAY(close.where(close > 0), 1)

        intraday_range = valid_high - valid_low
        high_gap = (valid_high - previous_close).abs()
        low_gap = (valid_low - previous_close).abs()
        gap_range = high_gap.where(high_gap >= low_gap, low_gap)
        true_range = intraday_range.where(previous_close.isna(), gap_range)
        true_range = true_range.where(true_range >= gap_range, gap_range)
        result = true_range.groupby(level="symbol", sort=False).transform(
            lambda series: series.ewm(
                span=window, adjust=False, min_periods=window
            ).mean()
        )
        result.name = "value"
        return result
