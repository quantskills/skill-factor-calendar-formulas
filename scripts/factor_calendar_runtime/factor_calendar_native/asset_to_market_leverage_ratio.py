"""Factor Calendar 资产负债市值比率因子。"""

from factor_calendar_runtime import Factor


class AssetToMarketLeverageRatioFactor(Factor):
    """最近报告期非流动负债与当日总市值之和相对于总市值的比率。"""

    def calculate(self, factors):
        total_liabilities = factors["total_liabilities"]
        current_liabilities = factors["current_liabilities"]
        market_cap = factors["market_cap"]

        # Factor Calendar 基础字段未单列非流动负债，用总负债减流动负债还原。
        non_current_liabilities = total_liabilities - current_liabilities

        valid = (market_cap > 0) & (non_current_liabilities >= 0)
        result = ((non_current_liabilities + market_cap) / market_cap).where(
            valid
        )
        return result
