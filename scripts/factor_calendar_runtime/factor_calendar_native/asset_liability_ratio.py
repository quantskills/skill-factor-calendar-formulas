"""Factor Calendar 资产负债率因子。"""

from factor_calendar_runtime import Factor


class AssetLiabilityRatioFactor(Factor):
    """最近报告期总负债与总资产之比。"""

    def calculate(self, factors):
        total_liabilities = factors["total_liabilities"] + 0
        total_assets = factors["total_assets"] + 0

        result = (total_liabilities / total_assets).where(
            (total_liabilities >= 0) & (total_assets > 0)
        )
        result.name = "value"
        return result
