"""Factor Calendar 价格变动速率（ROC）因子。"""

from factor_calendar_runtime import Factor


class PriceRateOfChangeFactor(Factor):
    """当前收盘价相对 12 个交易日前收盘价的变化率。"""

    def calculate(self, factors):
        close = factors["close"] + 0
        window = 12

        previous_close = self.DELAY(close, window)
        result = ((close - previous_close) / previous_close * 100).where(
            (close > 0) & (previous_close > 0)
        )
        result.name = "value"
        return result
