"""Factor Calendar 历史波动率因子。"""

from factor_calendar_runtime import Factor


class HistoricalVolatilityFactor(Factor):
    """最近一个月日收益率的滚动标准差。"""

    def calculate(self, factors):
        close = factors["close"] + 0
        window = 20

        previous_close = self.DELAY(close, 1)
        daily_return = (close / previous_close - 1).where(
            (close > 0) & (previous_close > 0)
        )
        result = self.STDDEV(daily_return, window)
        result.name = "value"
        return result
