"""Factor Calendar 固定资产比率因子。"""

from factor_calendar_runtime import Factor


class FixedAssetRatioFactor(Factor):
    """最近报告期固定资产净额占总资产的比率。"""

    def calculate(self, factors):
        net_fixed_assets = factors["net_fixed_assets"] + 0
        total_assets = factors["total_assets"] + 0

        valid = (net_fixed_assets >= 0) & (total_assets > 0)
        result = (net_fixed_assets / total_assets).where(valid)
        result.name = "value"
        return result
