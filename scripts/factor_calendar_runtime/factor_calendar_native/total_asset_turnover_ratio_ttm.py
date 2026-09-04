"""Factor Calendar 总资产周转率（TTM）因子。"""

from factor_calendar_runtime import Factor


class TotalAssetTurnoverRatioTTMFactor(Factor):
    """营业收入 TTM 与期初、期末平均总资产之比。"""

    def calculate(self, factors):
        sp_ratio_ttm = factors["sp_ratio_ttm"] + 0
        market_cap = factors["market_cap"] + 0
        total_assets = factors["total_assets"] + 0
        lookback = 252

        revenue_ttm = sp_ratio_ttm * market_cap
        start_total_assets = self.DELAY(total_assets, lookback)
        average_total_assets = (start_total_assets + total_assets) / 2
        result = (revenue_ttm / average_total_assets).where(
            (revenue_ttm >= 0) & (average_total_assets > 0)
        )
        result.name = "value"
        return result
