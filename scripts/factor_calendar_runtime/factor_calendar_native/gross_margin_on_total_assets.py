"""Factor Calendar 总资产毛利率因子。"""

from factor_calendar_runtime import Factor


class GrossMarginOnTotalAssetsFactor(Factor):
    """营业毛利与平均总资产之比。"""

    def calculate(self, factors):
        revenue_ttm = factors["sp_ratio_ttm"] * factors["market_cap"]
        operating_cost = factors["cost_of_goods_sold"] + 0
        total_assets = factors["total_assets"] + 0
        previous_assets = self.DELAY(total_assets, 252)
        average_assets = (total_assets + previous_assets) / 2
        gross_profit = revenue_ttm - operating_cost

        result = (gross_profit / average_assets).where(
            (revenue_ttm >= 0)
            & (operating_cost >= 0)
            & (average_assets > 0)
        )
        result.name = "value"
        return result
