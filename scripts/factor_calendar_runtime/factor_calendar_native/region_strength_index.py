"""Factor Calendar 区域强度指数（Region Strength Index）因子。"""

from factor_calendar_runtime import Factor


class RegionStrengthIndexFactor(Factor):
    """20 日标准化波动幅度的 5 日指数移动平均。"""

    def calculate(self, factors):
        high = factors["high"] + 0
        low = factors["low"] + 0
        close = factors["close"] + 0
        normalization_window = 20
        smoothing_window = 5

        valid_price = (high > 0) & (low > 0) & (close > 0) & (high >= low)
        valid_high = high.where(valid_price)
        valid_low = low.where(valid_price)
        valid_close = close.where(valid_price)
        previous_close = self.DELAY(valid_close, 1)

        intraday_range = valid_high - valid_low
        high_gap = (valid_high - previous_close).abs()
        low_gap = (valid_low - previous_close).abs()
        gap_range = high_gap.where(high_gap >= low_gap, low_gap)
        true_range = intraday_range.where(intraday_range >= gap_range, gap_range)
        close_change = valid_close - previous_close
        range_weight = true_range.where(
            close_change <= 0, true_range / close_change
        ).where(previous_close.notna())

        rolling_min = range_weight.groupby(
            level="symbol", sort=False
        ).transform(
            lambda series: series.rolling(
                window=normalization_window,
                min_periods=normalization_window,
            ).min()
        )
        rolling_max = range_weight.groupby(
            level="symbol", sort=False
        ).transform(
            lambda series: series.rolling(
                window=normalization_window,
                min_periods=normalization_window,
            ).max()
        )
        rolling_range = rolling_max - rolling_min
        standardized_range = (
            (range_weight - rolling_min) / rolling_range * 100
        ).where(rolling_range > 0, 0.0)
        standardized_range = standardized_range.where(rolling_min.notna())
        result = standardized_range.groupby(
            level="symbol", sort=False
        ).transform(
            lambda series: series.ewm(
                span=smoothing_window,
                adjust=False,
                min_periods=smoothing_window,
            ).mean()
        )
        result.name = "value"
        return result
