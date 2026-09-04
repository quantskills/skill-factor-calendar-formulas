"""Factor Calendar 长期债务资本比率因子。"""

from factor_calendar_runtime import Factor


class LongTermDebtCapitalRatioFactor(Factor):
    """最近报告期非流动负债占总资产的比例。"""

    def calculate(self, factors):
        total_liabilities = factors["total_liabilities"]
        current_liabilities = factors["current_liabilities"]
        total_assets = factors["total_assets"]

        # Factor Calendar 基础字段未单列非流动负债，用总负债减流动负债还原。
        non_current_liabilities = total_liabilities - current_liabilities

        valid = (total_assets > 0) & (non_current_liabilities >= 0)
        result = (non_current_liabilities / total_assets).where(valid)
        return result
