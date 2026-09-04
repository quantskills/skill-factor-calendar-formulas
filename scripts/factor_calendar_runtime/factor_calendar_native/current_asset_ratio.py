"""Factor Calendar 流动资产占比因子。"""

from factor_calendar_runtime import Factor


class CurrentAssetRatioFactor(Factor):
    """最近报告期流动资产占总资产的比例。"""

    def calculate(self, factors):
        current_assets = factors["current_assets"]
        total_assets = factors["total_assets"]

        result = (current_assets / total_assets).where(total_assets > 0)
        return result
