"""Factor Calendar 权益周转率因子。"""

from factor_calendar_runtime import Factor


class EquityTurnoverRatioFactor(Factor):
    """最近 12 个月营业收入与平均股东权益之比。"""

    def calculate(self, factors):
        sp_ratio_ttm = factors["sp_ratio_ttm"]
        market_cap = factors["market_cap"]
        total_equity = factors["total_equity"]
        lookback = 252  # 约 12 个月

        revenue_ttm = sp_ratio_ttm * market_cap
        start_equity = self.DELAY(total_equity, lookback)
        average_equity = (start_equity + total_equity) / 2

        result = (revenue_ttm / average_equity).where(average_equity > 0)
        return result
