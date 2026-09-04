"""Factor Calendar 账面市值比因子。"""

from factor_calendar_runtime import Factor


class BookToMarketRatioFactor(Factor):
    """最近报告期归母权益与当日总市值之比。"""

    def calculate(self, factors):
        equity = factors["equity_parent_company"] + 0
        market_cap = factors["market_cap"] + 0

        result = (equity / market_cap).where(
            (equity > 0) & (market_cap > 0)
        )
        result.name = "value"
        return result
