"""Factor Calendar 权益资产比率因子。"""

from factor_calendar_runtime import Factor


class EquityToAssetRatioFactor(Factor):
    """最近报告期股东权益与总资产之比。"""

    def calculate(self, factors):
        total_equity = factors["total_equity"] + 0
        total_assets = factors["total_assets"] + 0

        result = (total_equity / total_assets).where(
            (total_equity >= 0) & (total_assets > 0)
        )
        result.name = "value"
        return result
