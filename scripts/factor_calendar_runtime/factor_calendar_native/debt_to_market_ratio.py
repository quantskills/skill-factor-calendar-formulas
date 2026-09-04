"""Factor Calendar 债务市值比率因子。"""

from factor_calendar_runtime import Factor


class DebtToMarketRatioFactor(Factor):
    """最近报告期总负债与当日总市值之比。"""

    def calculate(self, factors):
        total_liabilities = factors["total_liabilities"] + 0
        market_cap = factors["market_cap"] + 0

        valid = (total_liabilities >= 0) & (market_cap > 0)
        result = (total_liabilities / market_cap).where(valid)
        result.name = "value"
        return result
