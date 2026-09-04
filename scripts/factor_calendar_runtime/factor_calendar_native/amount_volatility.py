"""Factor Calendar 成交额波动率因子。"""

from factor_calendar_runtime import Factor


class AmountVolatilityFactor(Factor):
    """最近 3 个月日成交额的滚动标准差。"""

    def calculate(self, factors):
        amount = factors["amount"]
        window = 63  # 3 个月约等于 63 个交易日

        return self.STDDEV(amount, window)
