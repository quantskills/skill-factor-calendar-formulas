"""Factor Calendar 累计振荡指标（ASI）因子。"""

from factor_calendar_runtime import Factor


class AccumulatedSwingIndexFactor(Factor):
    """按页面公式累计最近 20 日的单日 Swing Index。"""

    def calculate(self, factors):
        open_price = factors["open"] + 0
        high = factors["high"] + 0
        low = factors["low"] + 0
        close = factors["close"] + 0
        window = 20

        valid = (
            (open_price > 0)
            & (high > 0)
            & (low > 0)
            & (close > 0)
            & (high >= open_price)
            & (high >= close)
            & (open_price >= low)
            & (close >= low)
        )
        valid_open = open_price.where(valid)
        valid_high = high.where(valid)
        valid_low = low.where(valid)
        valid_close = close.where(valid)

        previous_open = self.DELAY(valid_open, 1)
        previous_low = self.DELAY(valid_low, 1)
        previous_close = self.DELAY(valid_close, 1)
        previous_valid = (
            previous_open.notna()
            & previous_low.notna()
            & previous_close.notna()
        )

        a_value = (valid_high - previous_close).abs()
        b_value = (valid_low - previous_close).abs()
        c_value = (valid_high - previous_low).abs()
        d_value = (previous_close - previous_open).abs()
        x_value = (
            (valid_close - previous_close)
            + 0.5 * (valid_close - valid_open)
            + (previous_close - previous_open)
        )
        k_value = a_value.where(a_value >= b_value, b_value)

        first_case = (a_value > b_value) & (a_value > c_value)
        second_case = (b_value > a_value) & (b_value > c_value)
        r_value = (c_value + 0.25 * d_value).where(~first_case)
        r_value = r_value.where(
            ~second_case, b_value + 0.5 * a_value + 0.25 * d_value
        )
        r_value = r_value.where(
            ~first_case, a_value + 0.5 * b_value + 0.25 * d_value
        )

        denominator = r_value * k_value
        swing_index = (16 * x_value / denominator).where(
            previous_valid & (denominator > 0)
        )
        result = swing_index.groupby(level="symbol", sort=False).transform(
            lambda series: series.rolling(
                window=window, min_periods=window
            ).sum()
        )
        result.name = "value"
        return result
