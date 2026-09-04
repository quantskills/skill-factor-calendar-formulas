"""Factor Calendar 短期偿债压力比率因子。"""

from factor_calendar_runtime import Factor


class ShortTermDebtPressureRatioFactor(Factor):
    """最近报告期流动负债占总负债的比例。"""

    def calculate(self, factors):
        current_liabilities = factors["current_liabilities"]
        total_liabilities = factors["total_liabilities"]

        result = (current_liabilities / total_liabilities).where(total_liabilities > 0)
        return result
