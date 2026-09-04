"""Factor Calendar 股票换手率因子。"""

from factor_calendar_runtime import Factor


class StockTurnoverRateFactor(Factor):
    """最近 20 个交易日成交额合计与平均总市值之比。"""

    def calculate(self, factors):
        amount = factors["amount"]
        market_cap = factors["market_cap"]
        window = 20  # 约 1 个月

        period_amount = self.SUM(amount, window)
        start_market_cap = self.DELAY(market_cap, window - 1)
        average_market_cap = (start_market_cap + market_cap) / 2

        result = (period_amount / average_market_cap).where(average_market_cap > 0)
        return result
