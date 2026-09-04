"""Factor Calendar 对数市值规模因子。"""

from factor_calendar_runtime import Factor


class LogMarketCapFactor(Factor):
    """当日总市值的自然对数。"""

    def calculate(self, factors):
        market_cap = factors["market_cap"] + 0

        result = self.LOG(market_cap.where(market_cap > 0))
        result.name = "value"
        return result
