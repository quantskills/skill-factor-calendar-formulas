"""Factor Calendar 资产现金回报率因子。"""

from factor_calendar_runtime import Factor


class AssetCashReturnRateFactor(Factor):
    """经营活动现金流量净额与平均总资产之比。"""

    def calculate(self, factors):
        operating_cash_flow = factors["cash_flow_from_operating_activities"]
        total_assets = factors["total_assets"]
        lookback = 252  # 约 12 个月

        start_assets = self.DELAY(total_assets, lookback)
        average_assets = (start_assets + total_assets) / 2

        result = (operating_cash_flow / average_assets).where(average_assets > 0)
        return result
