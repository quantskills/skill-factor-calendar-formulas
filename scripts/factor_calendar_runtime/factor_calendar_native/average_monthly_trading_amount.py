"""Factor Calendar 平均月度成交额因子。"""

from factor_calendar_runtime import Factor


class AverageMonthlyTradingAmountFactor(Factor):
    """最近三个月（63 个交易日）的日均成交额。"""

    def calculate(self, factors):
        amount = factors["amount"] + 0
        window = 63

        result = amount.where(amount >= 0).groupby(
            level="symbol", sort=False
        ).transform(
            lambda series: series.rolling(
                window=window, min_periods=window
            ).mean()
        )
        result.name = "value"
        return result
