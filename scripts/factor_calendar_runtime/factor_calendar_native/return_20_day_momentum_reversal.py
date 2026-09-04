"""Factor Calendar 20 日区间收益率动量/反转因子。"""

from factor_calendar_runtime import Factor


class Return20DayMomentumReversalFactor(Factor):
    """当前收盘价与 20 个交易日前收盘价之比。"""

    def calculate(self, factors):
        close = factors["close"] + 0
        lookback = 20

        delayed_close = self.DELAY(close, lookback)
        result = (close / delayed_close).where(
            (close > 0) & (delayed_close > 0)
        )
        result.name = "value"
        return result
