"""Factor Calendar 心理线（PSY）因子。"""

from factor_calendar_runtime import Factor


class PsychologicalLineFactor(Factor):
    """最近 12 个交易日中上涨日所占的百分比。"""

    def calculate(self, factors):
        close = factors["close"] + 0
        window = 12

        previous_close = self.DELAY(close, 1)
        valid = (close > 0) & (previous_close > 0)
        up_day = (close > previous_close).astype(float).where(valid)
        up_count = up_day.groupby(level="symbol", sort=False).transform(
            lambda series: series.rolling(
                window=window, min_periods=window
            ).sum()
        )
        result = up_count / window * 100
        result.name = "value"
        return result
