"""Factor Calendar 流动资产周转率因子。"""

from factor_calendar_runtime import Factor


class CurrentAssetTurnoverRatioFactor(Factor):
    """营业收入 TTM 与期初、期末流动资产平均值之比。"""

    def calculate(self, factors):
        sp_ratio_ttm = factors["sp_ratio_ttm"]
        market_cap = factors["market_cap"]
        current_assets = factors["current_assets"]
        lookback = 252  # 约 12 个月

        revenue_ttm = sp_ratio_ttm * market_cap
        start_current_assets = self.DELAY(current_assets, lookback)
        average_current_assets = (start_current_assets + current_assets) / 2

        result = (revenue_ttm / average_current_assets).where(average_current_assets > 0)
        return result
